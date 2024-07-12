import copy
import functools
import itertools
import json
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal, Union

from pydantic import AliasChoices, AliasPath, BaseModel
from pydantic._internal._typing_extra import origin_is_union
from pydantic._internal._utils import deep_update
from pydantic_core import PydanticUndefined
from typing_extensions import get_args, get_origin

from .constants import ORDERED_SETTINGS
from .errors import ArFiSettingsError
from .readers import ArFiBaseReader, ArFiReader
from .schemes import (
    EnvConfigSchema,
    FileConfigSchema,
    SettingsConfigSchema,
)
from .types import PathType
from .utils import (
    allow_json_parse_failure,
    create_dict_for_path,
    extract_unique_annotations,
    is_pydantic,
    is_settings,
    search_dict_for_path,
)

if TYPE_CHECKING:
    from .main import ArFiSettings

__all__ = (
    "ArFiHandler",
    "ArFiBaseHandler",
)


class ArFiBaseHandler(ABC):
    """Base handler class."""

    settings_class: "ArFiSettings" = None
    """The passed class for which the settings are being processed."""
    init_kwargs: dict[str, Any]
    """Parameters passed at initialisation or during previous processing."""
    handler: str = "default_main_handler"
    """Handler Method.
    Can be overridden for any instance of the passed settings reading class.
    """
    ordered_settings: list[str] = ORDERED_SETTINGS
    """In what order to read the settings.
    For any instance, you can swap / add new ones / remove existing ones,
    i.e. override as you like, regardless of the value set in the class
    """
    config: SettingsConfigSchema
    """The main settings parameters corresponding to the current class."""
    reader_class: ArFiBaseReader = ArFiReader
    """Settings reader class.
    Can be overridden in a handler that is defined in the passed settings class.
    """
    fields_names: set[str]
    """The names of all fields that are in the passed settings class."""
    fields_is_settings: list[str]
    """Field names that are correctly readable settings.
    There are limitations!!!
    ```
    class SQLite(ArFiSettings):
        pass

    class Postgres(ArFiSettings):
        pass

    class MySQL(BaseModel):
        pass

    # correctly processed fields - are readable settings
    class AppConfig(ArFiSettings):
        db: Postgres

    # correctly processed fields - are readable settings
    class AppConfig(ArFiSettings):
        db: Postgres | SQLite

    # Settings for the `db` specified in the `Postgres` class will not be read
    class AppConfig(ArFiSettings):
        db: Postgres | MySQL  # MySQL inherits from BaseModel, not ArFiSettings

    # Settings for the `db` specified in the `Postgres` class will not be read
    class AppConfig(ArFiSettings):
        db: Postgres | str | None

    # Settings for `db` set in `Postgres` or `SQLite` class will not be read
    class AppConfig(ArFiSettings):
        db: Postgres | SQLite | None

    # Settings for the `db` specified in the `Postgres` class will not be read
    class AppConfig(ArFiSettings):
        db: list[Postgres]
    ```
    """
    field_aliases: dict[str, list[str]]
    """Register-dependent aliases for specific fields.
    The key is the name of the field.
    Sorting is set by Pydantic
    """
    field_aliases_not_case_sensitive: dict[str, list[str]]
    """Registro NOT dependent aliases for specific fields.
    The key is the name of the field.
    Sorting is set by Pydantic,
    but alias.lower() is added after the case-dependent alias.
    """
    alias_fields: dict[str, list[str]]
    """List of fields for case-dependent aliases.
    Key - case-dependent alias
    """
    alias_fields_not_case_sensitive: dict[str, list[str]]
    """List of fields for case-independent aliases.
    Key - alias, case-independent
    """
    fields_alias_path: dict[str, dict[str, int | list[str | int]]]
    """Registry-dependent AliasPath
    Key - alias, case-sensitive
    """
    fields_alias_path_not_case_sensitive: dict[str, dict[str, int | list[str | int | list[str | int]]]]
    """Registro NOT dependent AliasPath
    Key - alias, case NOT dependent
    """
    fields_is_pydantic: list[str]
    """
    Names of fields inherited from the pydantic.BaseModel.
    """
    pydantic_single_fields: dict[str, list[str]]
    """
    Dict of fields keys info.
    Key - field name
    """
    fields_discriminator: dict[str, dict[str, Any]]
    """
    Fields that have a discriminator as a string.
    Key - field name
    """
    pydantic_aliases_info: dict[str, list[dict[str, Any]]]
    """
    Information about nested fields, if the field itself is inherited from pydantic.BaseModel.
    Key - field name
    """
    allowed_json_parse_failure_fields: set[str]
    """
    Fields that can be ignored when parsing JSON.
    """
    data: dict[str, Any]
    """
    Data returned by the handler.
    """

    def __init__(
        self,
        settings_class: "ArFiSettings",
        init_kwargs: dict[str, Any],
        handler: str = "",
    ) -> None:
        super().__init__()
        self.settings_class = settings_class
        self.reader_class.BASE_DIR = settings_class.BASE_DIR
        self.reader_class.ROOT_DIR = settings_class.root_dir
        self.init_kwargs = init_kwargs
        self.config = self.settings_class.settings_config
        if handler:
            self.handler = self._validate_main_handler(handler)
        self.config.conf_ext = self._validate_conf_ext(self.config.conf_ext)
        self.ordered_settings = self._validate_ordered_settings_handlers(
            self.settings_class.ordered_settings,
            self.settings_class,
        )
        self.conf_custom_ext_handler = self._validate_conf_custom_ext_handler(
            self.config.conf_custom_ext_handler,
        )
        self.data = {}
        self.fields_is_settings = []
        self.fields_is_pydantic = []
        self.pydantic_single_fields = dict()
        self.fields_names = set()
        self.field_aliases = dict()
        self.field_aliases_not_case_sensitive = dict()
        self.alias_fields = dict()
        self.alias_fields_not_case_sensitive = dict()
        self.fields_alias_path = dict()
        self.fields_alias_path_not_case_sensitive = dict()
        self.fields_defaults = dict()
        self.fields_discriminator = dict()
        self.pydantic_aliases_info = dict()
        self.allowed_json_parse_failure_fields = set()
        self._extract_fields_info()
        self._extract_alias_info()
        self._prepare_init_kwargs()

    def _prepare_init_kwargs(self) -> None:
        """Separate init and handler kwargs."""

        from arfi_settings import ArFiSettings

        _handler_value: bool = self.init_kwargs.get("_handler_value", False)
        _init_value: dict = self.init_kwargs.get("_init_value", {})

        for field_name, field_value in self.init_kwargs.items():
            if field_name in self.fields_is_settings:
                if issubclass(type(field_value), ArFiSettings):
                    instance_id = id(field_value)
                    field_value = field_value.model_dump()
                    # REMOVE computed fields
                    # field_value.pop("conf_path")
                    # field_value.pop("env_path")
                    field_value["_instance_id"] = instance_id
                    self.init_kwargs[field_name] = field_value
        self.init_kwargs = self._convert_data_to_field_names(self.init_kwargs)
        if not _handler_value:
            for field_name, field_value in self.init_kwargs.items():
                if field_name in self.fields_is_settings and field_value:
                    self.init_kwargs[field_name]["_init_value"] = field_value
        else:
            self.data = copy.deepcopy(self.init_kwargs)
            self.init_kwargs = dict()
            if _init_value:
                _init_value = self._convert_data_to_field_names(_init_value)
                for field_name, field_value in _init_value.items():
                    if field_name in self.fields_is_settings and field_value:
                        _init_value[field_name]["_init_value"] = field_value
                self.init_kwargs = _init_value

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.handler != "default_main_handler":
            cls.handler = cls._validate_main_handler(cls.handler)

    def _alias_decorator(self, func):
        """Find value by alias and return it."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            valid_data = dict()
            fields_set = set()
            data = func(*args, **kwargs)
            case_sensitive = data.get("__case_sensitive", self.config.case_sensitive)
            lower_data = dict()
            if case_sensitive:
                dict_fields_alias = self.field_aliases
                dict_fields_alias_path = self.fields_alias_path
            else:
                dict_fields_alias = self.field_aliases_not_case_sensitive
                dict_fields_alias_path = self.fields_alias_path_not_case_sensitive
                for key, value in data.items():
                    if isinstance(key, str):
                        key = key.lower()
                    if key not in lower_data:
                        lower_data[key] = value
            for field_name, aliases in dict_fields_alias.items():
                fields_alias_path = dict_fields_alias_path.get(field_name)
                for alias in aliases:
                    if field_name in fields_set:
                        break
                    value = data.get(alias, PydanticUndefined)
                    if not case_sensitive and value is PydanticUndefined:
                        value = lower_data.get(alias, PydanticUndefined)

                    if value is not PydanticUndefined:
                        if fields_alias_path:
                            if alias_path := fields_alias_path.get(alias):
                                if isinstance(value, str):
                                    value = json.loads(value)
                                value_dict = {alias: value}
                                field_value = search_dict_for_path(alias_path, value_dict, case_sensitive)
                                valid_data[field_name] = field_value
                                fields_set.add(field_name)
                            else:
                                valid_data[field_name] = value
                                fields_set.add(field_name)
                        else:
                            valid_data[field_name] = value
                            fields_set.add(field_name)
            return valid_data

        return wrapper

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if callable(value) and not name.startswith("_"):
            alias_decorator = object.__getattribute__(self, "_alias_decorator")
            if name.endswith("ext_handler"):
                value = alias_decorator(value)
            elif name == "cli_ordered_settings_handler":
                value = alias_decorator(value)
            elif name == "secrets_ordered_settings_handler":
                value = alias_decorator(value)
        return value

    def _convert_data_to_field_names(self, data: dict[str, Any]) -> dict[str, Any]:
        """Renames keys in data from alias to field names."""

        valid_data = dict()
        fields_set = set()
        add_to_fieldset = True
        is_handler_value = data.get("_handler_value", False)
        fields_alias_path = self.fields_alias_path
        if not self.config.case_sensitive:
            fields_alias_path = self.fields_alias_path_not_case_sensitive

        for name, value in data.items():
            if is_handler_value and name not in fields_set:
                # NOTE: Only for AliasPath
                if name in self.fields_names and name in fields_alias_path:
                    valid_data[name] = value

            alias_fields = self.alias_fields.get(name)
            if not alias_fields and not self.config.case_sensitive:
                alias_fields = self.alias_fields_not_case_sensitive.get(name)
                if not alias_fields:
                    add_to_fieldset = False
                    alias_fields = self.alias_fields_not_case_sensitive.get(name.lower())

            if alias_fields:
                for field_name in alias_fields:
                    field_aliases = self.field_aliases.get(field_name)
                    first_alias = field_aliases[0]
                    if name != first_alias and field_name in fields_set:
                        continue
                    if fields_aliases_path := self.fields_alias_path.get(field_name):
                        if alias_path := fields_aliases_path.get(name):
                            field_value = search_dict_for_path(alias_path, {name: value})
                            if field_value is not PydanticUndefined:
                                valid_data[field_name] = field_value
                                if add_to_fieldset:
                                    fields_set.add(field_name)
                        else:
                            valid_data[field_name] = value
                            if add_to_fieldset:
                                fields_set.add(field_name)
                    else:
                        valid_data[field_name] = value
                        if add_to_fieldset:
                            fields_set.add(field_name)

        return valid_data

    def _convert_data_to_valid_aliases(self, data: dict[str, Any]) -> dict[str, Any]:
        """Renames keys in data from field names to valid aliases."""

        valid_data = dict()
        fields_set = set()
        for field_name, aliases in self.field_aliases.items():
            value = data.get(field_name, PydanticUndefined)
            if value is not PydanticUndefined:
                fields_alias_path = self.fields_alias_path.get(field_name)
                for alias in aliases:
                    if field_name in fields_set:
                        break

                    if fields_alias_path:
                        if alias_path := fields_alias_path.get(alias):
                            alias_dict = create_dict_for_path(alias_path, value)
                            if valid_data.get(alias):
                                valid_data[alias].update(alias_dict[alias])
                            else:
                                valid_data.update(alias_dict)
                            fields_set.add(field_name)
                        else:
                            alias_dict = {alias: value}
                            valid_data.update(alias_dict)
                            fields_set.add(field_name)
                    else:
                        alias_dict = {alias: value}
                        valid_data.update(alias_dict)
                        fields_set.add(field_name)
        return valid_data

    def __call__(self) -> dict[str, Any]:
        """Generate settings data."""

        handler = self._get_main_handler(self.handler)
        self.data = handler()

        _handler_tree = copy.deepcopy(self.settings_class._handler_tree)
        _handler_parent_mode_dir = copy.deepcopy(self.settings_class._handler_parent_mode_dir)
        _handler_ordered_settings = copy.deepcopy(self.ordered_settings)
        _handler_parent_file_config = FileConfigSchema(**self.settings_class.computed_file_config)
        _handler_parent_env_config = EnvConfigSchema(**self.settings_class.computed_env_config)

        if self.settings_class.mode_dir is not None:
            _handler_parent_mode_dir.append(self.settings_class.mode_dir)
        read_config_data = {
            "_read_config": True,
            "_handler_value": True,
            "_handler_read_pyproject_toml_force": False,
            "_handler_search_base_dir": False,
            "_handler_parent_mode_dir": _handler_parent_mode_dir,
            "_handler_ordered_settings": _handler_ordered_settings,
            "_handler_parent_file_config": _handler_parent_file_config,
            "_handler_parent_env_config": _handler_parent_env_config,
        }
        for field in self.fields_is_settings:
            if not self.data.get(field):
                self.data[field] = {}
            self.data[field].update(read_config_data)
            self.data[field]["_handler_mode_dir_attr"] = field
            if self.config.env_case_sensitive:
                field_aliases = self.field_aliases[field]
            else:
                field_aliases = self.field_aliases_not_case_sensitive[field]
            product_tree = copy.deepcopy(_handler_tree)
            product_tree.append(field_aliases)
            self.data[field]["_handler_tree"] = product_tree

            if field in self.fields_defaults:
                instance_id = self.fields_defaults[field]
                self.data[field]["_instance_id"] = instance_id

            # Resolve default discriminator
            if discriminator := self.fields_discriminator.get(field):
                discriminator_key, discriminator_value = list(discriminator.items())[0]
                if not self.config.case_sensitive:
                    if not self.data[field].get(discriminator_key):
                        exist_discriminator_value = PydanticUndefined
                        for key, value in self.data[field].items():
                            if key.lower() == discriminator_key.lower():
                                exist_discriminator_value = value
                                self.data[field].pop(key)
                                break
                        if exist_discriminator_value is not PydanticUndefined:
                            self.data[field][discriminator_key] = exist_discriminator_value
                        elif discriminator_value is not PydanticUndefined:
                            self.data[field][discriminator_key] = discriminator_value
                else:
                    if not self.data[field].get(discriminator_key) and discriminator_value is not PydanticUndefined:
                        self.data[field][discriminator_key] = discriminator_value
        self.data = self._convert_data_to_valid_aliases(self.data)

        return self.data

    def _append_field_to_alias(self, alias: str, field: str) -> None:
        if not self.alias_fields.get(alias):
            self.alias_fields[alias] = []
        if field not in self.alias_fields[alias]:
            self.alias_fields[alias].append(field)

    def _append_alias_to_field(self, field: str, alias: str) -> None:
        if not self.field_aliases.get(field):
            self.field_aliases[field] = []
        if alias not in self.field_aliases[field]:
            self.field_aliases[field].append(alias)
        self._append_field_to_alias(alias, field)
        self._append_alias_not_case_sensitive_to_field(field, alias)

    def _append_field_to_alias_not_case_sensitive(self, alias: str, field: str) -> None:
        if not self.alias_fields_not_case_sensitive.get(alias):
            self.alias_fields_not_case_sensitive[alias] = []
        if field not in self.alias_fields_not_case_sensitive[alias]:
            self.alias_fields_not_case_sensitive[alias].append(field)

    def _append_alias_not_case_sensitive_to_field(self, field: str, alias: str) -> None:
        if not self.field_aliases_not_case_sensitive.get(field):
            self.field_aliases_not_case_sensitive[field] = []
        for als in (alias, alias.lower()):
            if als not in self.field_aliases_not_case_sensitive[field]:
                self.field_aliases_not_case_sensitive[field].append(als)
            self._append_field_to_alias_not_case_sensitive(als, field)

    def _append_fields_alias_path(self, field: str, alias_path: AliasPath | list[str | int]) -> None:
        if isinstance(alias_path, AliasPath):
            alias_path = alias_path.convert_to_aliases()
        first_arg = alias_path[0]
        self._append_alias_to_field(field, first_arg)
        # case_sensitive=True
        if self.fields_alias_path.get(field) is None:
            self.fields_alias_path[field] = dict()
        self.fields_alias_path[field][first_arg] = alias_path

        # case_sensitive=False
        if self.fields_alias_path_not_case_sensitive.get(field) is None:
            self.fields_alias_path_not_case_sensitive[field] = dict()
        self.fields_alias_path_not_case_sensitive[field][first_arg] = alias_path
        self.fields_alias_path_not_case_sensitive[field][first_arg.lower()] = alias_path

    def _extract_alias_info(self) -> None:
        """Extract information about aliases from settings_class."""

        for name, field in self.settings_class.model_fields.items():
            if field.validation_alias is None:
                self._append_alias_to_field(name, name)
                continue

            if isinstance(field.validation_alias, str):
                self._append_alias_to_field(name, field.validation_alias)
                continue

            validation_aliases: list[str | AliasPath] = (
                field.validation_alias.choices
                if isinstance(field.validation_alias, AliasChoices)
                else [field.validation_alias]
            )
            for alias in validation_aliases:
                if isinstance(alias, str):
                    self._append_alias_to_field(name, alias)
                    continue

                assert isinstance(alias, AliasPath)
                self._append_fields_alias_path(name, alias)

    def _extract_fields_info(self) -> None:
        """Extract fields info."""

        from arfi_settings import ArFiSettings

        for field_name, field in self.settings_class.model_fields.items():
            self.fields_names.add(field_name)
            unique_annotations = extract_unique_annotations(field.annotation)

            if ArFiSettings in unique_annotations:
                raise ArFiSettingsError(
                    f"class {self.settings_class.__class__.__name__}: "
                    f"field `{field_name}` cannot contain ArFiSettings type. "
                    f"Must be only subclass `ArFiSettings`."
                )

            if is_settings(field.annotation):
                self.fields_is_settings.append(field_name)
            if origin_is_union(get_origin(field.annotation)):
                if all([is_settings(arg) for arg in get_args(field.annotation)]):
                    self.fields_is_settings.append(field_name)

            if field_name in self.fields_is_settings:
                if issubclass(type(field.default), ArFiSettings):
                    instance_id = id(field.default)
                    self.fields_defaults[field_name] = instance_id
                if isinstance(field.discriminator, str):
                    discriminator_key = field.discriminator
                    discriminator_value = PydanticUndefined
                    if field.default is not PydanticUndefined:
                        discriminator_value = getattr(field.default, discriminator_key)
                    self.fields_discriminator[field_name] = {discriminator_key: discriminator_value}

            if is_pydantic(field.annotation):
                self.fields_is_pydantic.append(field_name)
                self.pydantic_single_fields[field_name] = self._search_field_keys_info(field.annotation)
            elif origin_is_union(get_origin(field.annotation)):
                if all([is_pydantic(arg) for arg in get_args(field.annotation)]):
                    self.fields_is_pydantic.append(field_name)
                    list_pydantic_aliases_info = []
                    for model in get_args(field.annotation):
                        field_aliases_info_dict = self._search_field_keys_info(model)
                        list_pydantic_aliases_info.append(field_aliases_info_dict)
                    self.pydantic_aliases_info[field_name] = list_pydantic_aliases_info

            if field_name not in self.fields_is_pydantic:
                if allow_json_parse_failure(field):
                    self.allowed_json_parse_failure_fields.add(field_name)

    def _search_field_keys_info(
        self, model: type[BaseModel]
    ) -> tuple[list[dict[str, list]], dict[str, list[str | int]]]:
        """Searches field keys info."""

        list_keys_info = []
        dict_alias_path = dict()
        for field_name, field in model.model_fields.items():
            field_keys = {
                "aliases": [],
                "alias_path": [],
                "keys": [],
            }
            aliases = []
            alias_path = dict()
            if validation_alias := field.validation_alias:
                if isinstance(validation_alias, str):
                    aliases.append(validation_alias)
                    if not self.config.env_case_sensitive:
                        alias_lower = validation_alias.lower()
                        if alias_lower not in aliases:
                            aliases.append(alias_lower)
                else:
                    validation_aliases: list[str | AliasPath] = (
                        field.validation_alias.choices
                        if isinstance(field.validation_alias, AliasChoices)
                        else [field.validation_alias]
                    )
                    for alias in validation_aliases:
                        if isinstance(alias, str):
                            aliases.append(alias)
                            if not self.config.env_case_sensitive:
                                alias_lower = alias.lower()
                                if alias_lower not in aliases:
                                    aliases.append(alias_lower)
                        else:
                            if isinstance(alias, AliasPath):
                                alias = alias.convert_to_aliases()
                            first_arg = alias[0]
                            aliases.append(first_arg)
                            alias_path[first_arg] = alias
                            dict_alias_path[first_arg] = alias
                            if not self.config.env_case_sensitive:
                                alias_lower = first_arg.lower()
                                if alias_lower not in aliases:
                                    aliases.append(alias_lower)
                                    alias_path[alias_lower] = alias
                                    dict_alias_path[alias_lower] = alias
            else:
                aliases.append(field_name)
                if not self.config.env_case_sensitive:
                    alias_lower = field_name.lower()
                    if alias_lower not in aliases:
                        aliases.append(alias_lower)
            field_keys["aliases"] = aliases
            field_keys["alias_path"] = alias_path
            if is_pydantic(field.annotation):
                field_aliases_info_dict = self._search_field_keys_info(field.annotation)
                field_keys["keys"] = field_aliases_info_dict["list_keys_info"]
            list_keys_info.append(field_keys)

        list_nested_keys = self._search_field_nested_keys(list_keys_info)
        field_aliases_info_dict = dict(
            model_name=model.__name__,
            list_keys_info=list_keys_info,
            dict_alias_path=dict_alias_path,
            list_nested_keys=list_nested_keys,
        )
        return field_aliases_info_dict

    def _search_field_nested_keys(self, list_keys_info: list[dict[str, list]]) -> list[str]:
        """Searches field nested keys."""

        list_nested_keys = []
        env_nested_delimiter = self.config.env_nested_delimiter
        if env_nested_delimiter:
            for field_keys in list_keys_info:
                aliases = field_keys["aliases"]
                alias_path = field_keys["alias_path"]
                nested_aliases = []
                if field_keys["keys"]:
                    nested_aliases = self._search_field_nested_keys(field_keys["keys"])
                if nested_aliases:
                    list_aliases = [aliases, nested_aliases]
                    list_aliases_str = []
                    for combo in itertools.product(*list_aliases):
                        if combo[0] in alias_path:
                            continue
                        else:
                            combo_str = f"{env_nested_delimiter}".join(combo)
                        list_aliases_str.append(combo_str)
                    list_aliases_str.extend(aliases)
                    list_nested_keys.extend(list_aliases_str)
                else:
                    list_nested_keys.extend(aliases)
        return list_nested_keys

    @classmethod
    def _is_exist_main_handler(cls, name: str) -> bool:
        """Check is exist main handler."""

        name = cls._normalize_handler_name(name, "main")
        return hasattr(cls, name)

    @classmethod
    def _is_exist_ordered_settings_handler(cls, name: str) -> bool:
        """Check is exist ordered_settings handler."""

        name = cls._normalize_handler_name(name, "ordered_settings")
        return hasattr(cls, name)

    @classmethod
    def _is_exist_ext_handler(cls, name: str) -> bool:
        """Check is exist extensions handler."""

        name = cls._normalize_handler_name(name, "ext")
        return hasattr(cls, name)

    @classmethod
    def _validate_main_handler(cls, handler: str) -> str:
        """Validate name and check exist main handler."""

        if not handler or not isinstance(handler, str):
            raise ArFiSettingsError(f"{cls.__name__}: attribute `handler` must be not empty string")
        if not handler.endswith("_main_handler"):
            raise ArFiSettingsError(f"{cls.__name__}: attribute `handler` must end with `_main_handler`")
        if not cls._is_exist_main_handler(handler):
            raise ArFiSettingsError(f"{cls.__name__}: `{handler}` is not defined")
        return handler

    @classmethod
    def _validate_ordered_settings_handlers(cls, ordered_settings: list[str], settings_class: type) -> list[str]:
        """Returns a list of valid ordered_settings handlers."""

        if not ordered_settings:
            raise ArFiSettingsError(f"{settings_class.__class__.__name__}: `ordered_settings` is empty")
        valid_ordered_settings = []
        for handler_name in ordered_settings:
            handler_name = cls._normalize_handler_name(handler_name, "ordered_settings")
            if not cls._is_exist_ordered_settings_handler(handler_name):
                raise ArFiSettingsError(f"{cls.__name__}: `{handler_name}` is not defined")
            valid_ordered_settings.append(handler_name)
        if "init_kwargs_ordered_settings_handler" not in valid_ordered_settings:
            warnings.warn(
                f"\033[33m\n"
                f"For instance of {settings_class.__class__.__name__}():\n"
                f"Reverse inheritance is disabled because `init_kwargs` is missing in `ordered_settings`"
                f"\033[0m",
                category=Warning,
                stacklevel=4,
            )
        return valid_ordered_settings

    def _validate_conf_custom_ext_handler(
        self,
        conf_custom_ext_handler: str | dict[str, str] | None,
    ) -> dict[str, str]:
        """Validate `conf_custom_ext_handler` and return valid dict."""

        valid_conf_custom_ext_handler = {}
        error_message = (
            f"{self.settings_class.__class__.__name__}: `conf_ext` contains empty extension, "
            f"but `conf_custom_ext_handler` is not defined"
        )
        if conf_custom_ext_handler is None or conf_custom_ext_handler == "":
            if "" in self.config.conf_ext:
                raise ArFiSettingsError(error_message)
            return valid_conf_custom_ext_handler
        if isinstance(conf_custom_ext_handler, str):
            conf_custom_ext_handler = {"": conf_custom_ext_handler}
        if not isinstance(conf_custom_ext_handler, dict):
            raise ArFiSettingsError(
                f"{self.settings_class.__class__.__name__}: `conf_custom_ext_handler` "
                f"must be str, dict[str,str] or None. Current type: {type(conf_custom_ext_handler)}"
            )
        for ext, handler_name in conf_custom_ext_handler.items():
            assert isinstance(ext, str), (
                f"{self.settings_class.__class__.__name__}: Not valid type 'ext' in `conf_custom_ext_handler`. "
                f"Must be str. Current type: {type(ext)}"
            )
            handler_name = handler_name.lstrip(".")
            if ext and isinstance(ext, str):
                ext = ext.lstrip(".")
            handler_name = self._normalize_handler_name(handler_name, "ext")
            if not self._is_exist_ext_handler(handler_name):
                raise ArFiSettingsError(f"{self.__class__.__name__}: `{handler_name}` is not defined")
            valid_conf_custom_ext_handler[ext] = handler_name

        if "" in self.config.conf_ext and not valid_conf_custom_ext_handler.get("", False):
            raise ArFiSettingsError(error_message)
        self.config.conf_custom_ext_handler = valid_conf_custom_ext_handler
        return valid_conf_custom_ext_handler

    def _validate_conf_ext(self, conf_ext: str | list[str]) -> list[str]:
        """Validate conf_ext."""

        valid_conf_ext = []
        error_message = (
            f"{self.settings_class.__class__.__name__}: `conf_ext` "
            f"must be str, list[str] or empty string. Current: {conf_ext}"
        )
        if isinstance(conf_ext, str):
            conf_ext = conf_ext.lstrip(".")
            if not conf_ext:
                return [""]
            return [conf_ext]
        elif isinstance(conf_ext, list):
            for ext in conf_ext:
                if isinstance(ext, str):
                    ext = ext.lstrip(".")
                    if ext not in valid_conf_ext:
                        valid_conf_ext.append(ext)
                else:
                    raise ArFiSettingsError(error_message)
        else:
            raise ArFiSettingsError(error_message)
        return valid_conf_ext

    def _get_main_handler(self, name: str) -> Callable:
        name = self._normalize_handler_name(name, "main")
        if not self._is_exist_main_handler(name):
            raise ArFiSettingsError(f"{self.__class__.__name__}: `{name}` is not defined")
        return self.__getattribute__(name)

    def _get_ordered_settings_handler(self, name: str) -> Callable:
        name = self._normalize_handler_name(name, "ordered_settings")
        if not self._is_exist_ordered_settings_handler(name):
            raise ArFiSettingsError(f"{self.__class__.__name__}: `{name}` is not defined")
        return self.__getattribute__(name)

    def _find_ext_handler(self, file_path: Path) -> (Callable | None, Path):
        """Find and return ext handler."""

        source_file_path = file_path
        if ext := file_path.suffix:
            ext = ext.lstrip(".")
            ext = self.conf_custom_ext_handler.get(ext, ext)
            ext = ext.lstrip(".")
            handler = self._get_ext_handler(ext)
            return handler, file_path

        assert isinstance(self.config.conf_ext, list) and self.config.conf_ext

        for ext in self.config.conf_ext:
            if not ext:
                file_path = file_path.with_suffix("")
                if self.reader_class.is_exist_file(file_path):
                    name_custom_ext_handler = self.conf_custom_ext_handler.get("")
                    if name_custom_ext_handler is None:
                        raise ArFiSettingsError(f"Missing non extension handler for file: `{file_path.as_posix()}`")
                    handler = self._get_ext_handler(name_custom_ext_handler)
                    return handler, file_path
            else:
                ext = ext.lstrip(".")
                file_ext = f".{ext}"
                file_path = file_path.with_suffix(file_ext)
                if self.reader_class.is_exist_file(file_path):
                    name_custom_ext_handler = self.conf_custom_ext_handler.get(ext)
                    if name_custom_ext_handler:
                        ext = name_custom_ext_handler.lstrip(".")
                    handler = self._get_ext_handler(ext)
                    return handler, file_path
        return None, source_file_path

    def _get_ext_handler(self, name: str) -> Callable:
        name = self._normalize_handler_name(name, "ext")
        if not self._is_exist_ext_handler(name):
            raise ArFiSettingsError(f"{self.__class__.__name__}: `{name}` is not defined")
        return self.__getattribute__(name)

    @staticmethod
    def _normalize_handler_name(name: str, suffix: str) -> str:
        """Normalize handler name."""

        try:
            assert name and isinstance(name, str), "Handler `name` must be not empty string"
            assert not name.startswith("_"), "Handler `name` must not start with `_`"
        except AssertionError as e:
            raise ArFiSettingsError(e) from e
        if not suffix.endswith("_handler"):
            suffix = f"{suffix}_handler"
        suffix = suffix.lstrip("_")
        try:
            assert suffix in ["main_handler", "ordered_settings_handler", "ext_handler"], "Unknown handler suffix"
        except AssertionError as e:
            raise ArFiSettingsError(e) from e
        if not name.endswith(suffix):
            name = f"{name}_{suffix}"
        return name

    def toml_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        """Handles settings from .toml file."""

        reader = self.reader_class(
            file_path=file_path,
            file_encoding=self.config.conf_file_encoding,
            ignore_missing=self.config.conf_ignore_missing,
        )
        data = reader.read()
        data["__case_sensitive"] = self.config.conf_case_sensitive
        return data

    def yaml_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        """Handles settings from .yaml file."""

        reader = self.reader_class(
            file_path=file_path,
            file_encoding=self.config.conf_file_encoding,
            ignore_missing=self.config.conf_ignore_missing,
        )
        data = reader.read() or {}
        data["__case_sensitive"] = self.config.conf_case_sensitive
        return data

    def yml_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        """Handles settings from .yml file."""

        reader = self.reader_class(
            file_path=file_path,
            file_encoding=self.config.conf_file_encoding,
            ignore_missing=self.config.conf_ignore_missing,
        )
        data = reader.read() or {}
        data["__case_sensitive"] = self.config.conf_case_sensitive
        return data

    def json_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        """Handles settings from .json file."""

        reader = self.reader_class(
            file_path=file_path,
            file_encoding=self.config.conf_file_encoding,
            ignore_missing=self.config.conf_ignore_missing,
        )
        data = reader.read()
        data["__case_sensitive"] = self.config.conf_case_sensitive
        return data

    def cli_ordered_settings_handler(self) -> dict[str, Any]:
        """Handles settings from CLI."""

        data: dict[str, Any] = {}
        if self.config.cli:
            reader = self.reader_class(is_cli=True)
            data = reader.read()
            data["__case_sensitive"] = self.config.case_sensitive
        return data

    def init_kwargs_ordered_settings_handler(self) -> dict[str, Any]:
        """Handles settings from init_kwargs."""

        return self.init_kwargs

    def env_ordered_settings_handler(self) -> dict[str, Any]:
        """Handles settings from environment."""

        data: dict[str, Any] = {}
        reader = self.reader_class(
            is_env=True,
        )
        reader_data = reader.read()
        reader_data["__case_sensitive"] = self.config.env_case_sensitive
        data = self._convert_env_data_by_fields_names(data=reader_data, handler="env")
        return data

    def env_file_ordered_settings_handler(self) -> dict[str, Any]:
        """Handles settings from .env file."""

        data: dict[str, Any] = {}
        for file_path in self.config.env_path:
            reader = self.reader_class(
                file_path=file_path,
                is_env_file=True,
                file_encoding=self.config.env_file_encoding,
                ignore_missing=self.config.env_ignore_missing,
            )
            reader_data = reader.read()
            reader_data["__case_sensitive"] = self.config.env_case_sensitive
            env_file_data = self._convert_env_data_by_fields_names(
                data=reader_data,
                handler="env_file",
                env_file=file_path,
            )
            data = deep_update(data, env_file_data)

        return data

    def _convert_env_data_by_fields_names(
        self,
        data: dict[str, Any],
        handler: Literal["env_file", "env"],  # for feature debug
        env_file: Path | None = None,  # for feature debug
    ) -> dict[str, Any]:
        """Converts data from environment to data with fields names."""

        valid_data: dict[str, Any] = dict()
        fields_set = set()
        case_sensitive = data.get("__case_sensitive", self.config.case_sensitive)
        lower_data = dict()
        if case_sensitive:
            dict_fields_alias = self.field_aliases
            dict_fields_alias_path = self.fields_alias_path
        else:
            dict_fields_alias = self.field_aliases_not_case_sensitive
            dict_fields_alias_path = self.fields_alias_path_not_case_sensitive
            for key, value in data.items():
                if isinstance(key, str):
                    key = key.lower()
                if key not in lower_data:
                    lower_data[key] = value
        env_prefix = self.config.env_prefix
        env_nested_delimiter = self.config.env_nested_delimiter
        handler_tree = self.settings_class._handler_tree

        source_parents_prefixis = [""]
        if env_nested_delimiter and handler_tree:
            source_parents_prefixis = []

            for combo in itertools.product(*handler_tree):
                combo_str = f"{env_nested_delimiter}".join(combo)
                parent_pref = f"{combo_str}{env_nested_delimiter}"
                source_parents_prefixis.append(parent_pref)
        source_parents_prefixis = source_parents_prefixis or [""]
        parents_prefixis = []
        for parent_prefix in source_parents_prefixis:
            parents_prefixis.append(f"{parent_prefix}{env_prefix}")

        for field_name, aliases in dict_fields_alias.items():
            fields_alias_path = dict_fields_alias_path.get(field_name)

            found_value = self._search_exact_env_value(
                field_name=field_name,
                aliases=aliases,
                parents_prefixis=parents_prefixis,
                env_nested_delimiter=env_nested_delimiter,
                data=data,
                lower_data=lower_data,
                fields_set=fields_set,
                fields_alias_path=fields_alias_path,
            )

            # TODO: Combine fields_is_settings и fields_is_pydantic. Take out only the discriminator !!!
            if field_name in self.fields_is_settings:
                found_value = self._search_env_value_arfi_settings_fields(
                    field_name=field_name,
                    aliases=aliases,
                    parents_prefixis=parents_prefixis,
                    env_nested_delimiter=env_nested_delimiter,
                    found_value=found_value,
                    data=data,
                    lower_data=lower_data,
                )
            elif field_name in self.fields_is_pydantic:
                if isinstance(found_value, str):
                    found_value = json.loads(found_value)
                if field_name in self.pydantic_single_fields:
                    found_value = self._search_env_value_pydantic_single_field(
                        field_name=field_name,
                        aliases=aliases,
                        parents_prefixis=parents_prefixis,
                        env_nested_delimiter=env_nested_delimiter,
                        found_value=found_value,
                        data=data,
                    )
            else:
                if found_value is not PydanticUndefined:
                    try:
                        found_value = json.loads(found_value)
                    except (ValueError, json.decoder.JSONDecodeError) as e:
                        if field_name in self.allowed_json_parse_failure_fields:
                            pass
                        else:
                            raise e

            if found_value is not PydanticUndefined:
                valid_data[field_name] = found_value
        return valid_data

    def _search_exact_env_value(
        self,
        field_name: str,
        aliases: list[str],
        parents_prefixis: list[str],
        env_nested_delimiter: str,
        data: dict[str, Any],
        lower_data: dict[str, Any],
        fields_set: set[str],
        fields_alias_path: dict[str, AliasPath | list[str | int]],
    ) -> Union[dict[str, Any], PydanticUndefined]:
        """Searches exact value in environment."""

        found_value = PydanticUndefined
        for prefix in parents_prefixis:
            for alias in aliases:
                search_alias = f"{prefix}{alias}"
                if field_name in fields_set:
                    break

                value = data.get(search_alias, PydanticUndefined)
                if not self.config.env_case_sensitive and value is PydanticUndefined:
                    if prefix:
                        for k, v in data.items():
                            if k.startswith(prefix):
                                if k.lower() == search_alias.lower():
                                    value = v

                    if value is PydanticUndefined:
                        search_alias = f"{prefix}{alias.lower()}"
                        value = lower_data.get(search_alias, PydanticUndefined)

                if value is not PydanticUndefined:
                    if fields_alias_path:
                        if alias_path := fields_alias_path.get(alias):
                            value = json.loads(value)
                            value_dict = {alias: value}
                            field_value = search_dict_for_path(
                                alias_path,
                                value_dict,
                                self.config.env_case_sensitive,
                            )
                            found_value = field_value
                            fields_set.add(field_name)
                        else:
                            found_value = value
                            fields_set.add(field_name)
                    else:
                        found_value = value
                        fields_set.add(field_name)
                    break
            if value is not PydanticUndefined:
                break
        return found_value

    def _search_env_value_arfi_settings_fields(
        self,
        field_name: str,
        aliases: list[str],
        parents_prefixis: list[str],
        env_nested_delimiter: str,
        found_value: Union[dict, PydanticUndefined],
        data: dict[str, Any],
        lower_data: dict[str, Any],
    ) -> Union[dict[str, Any], PydanticUndefined]:
        """Searches value in arfi_settings fields."""

        if isinstance(found_value, str):
            found_value = json.loads(found_value)
            assert isinstance(found_value, dict)
        if field_name in self.pydantic_single_fields:
            # convert exact value
            if found_value is not PydanticUndefined:
                assert isinstance(found_value, dict)
                found_value = self._convert_env_found_value_key(
                    list_keys_info=self.pydantic_single_fields[field_name]["list_keys_info"],
                    found_value=found_value,
                    field_name=field_name,
                )
            # search nested key-value
            found_value = self._search_env_value_pydantic_single_field(
                field_name=field_name,
                aliases=aliases,
                parents_prefixis=parents_prefixis,
                env_nested_delimiter=env_nested_delimiter,
                found_value=found_value,
                data=data,
            )
        else:
            list_pydantic_aliases_info = self.pydantic_aliases_info[field_name]
            for field_aliases_info_dict in reversed(list_pydantic_aliases_info):
                # Search velue of nested key
                nested_key_dict = self._search_nested_key_value(
                    field_name=field_name,
                    aliases=aliases,
                    parents_prefixis=parents_prefixis,
                    env_nested_delimiter=env_nested_delimiter,
                    found_value=found_value,
                    data=data,
                    field_aliases_info_dict=field_aliases_info_dict,
                )
                if nested_key_dict:
                    if found_value is PydanticUndefined:
                        found_value = dict()
                    found_value = deep_update(found_value, nested_key_dict)

        # Search discriminator
        discriminator = self.fields_discriminator.get(field_name)
        if discriminator:
            if found_value is PydanticUndefined:
                found_value = dict()
            discriminator_key = list(discriminator.keys())[0]
            alias = aliases[0]
            for PREFIX in parents_prefixis:
                if env_nested_delimiter:
                    search_alias = f"{PREFIX}{alias}{env_nested_delimiter}{discriminator_key}"
                else:
                    search_alias = f"{PREFIX}{alias}_{discriminator_key}"

                value = data.get(search_alias, PydanticUndefined)
                if not self.config.env_case_sensitive and value is PydanticUndefined:
                    value = lower_data.get(search_alias.lower(), PydanticUndefined)
                if value is not PydanticUndefined:
                    found_value[discriminator_key] = value
                    break
        return found_value

    def _search_env_value_pydantic_single_field(
        self,
        field_name: str,
        aliases: list[str],
        parents_prefixis: list[str],
        env_nested_delimiter: str,
        found_value: Union[dict, PydanticUndefined],
        data: dict[str, Any],
    ) -> Union[dict[str, Any], PydanticUndefined]:
        """Searches value in pydantic single fields."""

        if found_value is not PydanticUndefined:
            assert isinstance(found_value, dict)
            found_value = self._convert_env_found_value_key(
                list_keys_info=self.pydantic_single_fields[field_name]["list_keys_info"],
                found_value=found_value,
                field_name=field_name,
            )

        # Search velue of nested key
        nested_key_dict = self._search_nested_key_value(
            field_name=field_name,
            aliases=aliases,
            parents_prefixis=parents_prefixis,
            env_nested_delimiter=env_nested_delimiter,
            found_value=found_value,
            data=data,
            field_aliases_info_dict=self.pydantic_single_fields[field_name],
        )

        if nested_key_dict:
            if found_value is PydanticUndefined:
                found_value = dict()
            found_value = deep_update(found_value, nested_key_dict)
        return found_value

    def _search_nested_key_value(
        self,
        field_name: str,
        aliases: list[str],
        parents_prefixis: list[str],
        env_nested_delimiter: str,
        found_value: Union[dict, PydanticUndefined],
        data: dict[str, Any],
        field_aliases_info_dict: dict[str, Any],
    ) -> dict[str, Any]:
        """Search nested key value in environment variable."""

        list_keys_info = field_aliases_info_dict["list_keys_info"]
        list_nested_keys = field_aliases_info_dict["list_nested_keys"]
        dict_alias_path = field_aliases_info_dict["dict_alias_path"]
        nested_key_lower = {i.lower() for i in list_nested_keys}

        nested_key_dict = dict()
        for prefix in reversed(parents_prefixis):
            for alias in reversed(aliases):
                start_key_prefix = f"{prefix}{alias}{env_nested_delimiter}"
                env_find_data = dict()
                for env_key, env_value in data.items():
                    if env_key.startswith(start_key_prefix):
                        env_nested_key = env_key[len(start_key_prefix) :]
                        if env_nested_key.lower() in nested_key_lower:
                            env_find_data[env_key] = env_value
                    elif not self.config.case_sensitive:
                        env_key_lower = env_key.lower()
                        if env_key_lower.startswith(start_key_prefix):
                            env_nested_key_lower = env_key_lower[len(start_key_prefix) :]
                            if env_nested_key_lower in nested_key_lower:
                                env_find_data[env_key] = env_value
                if env_find_data:
                    if self.config.case_sensitive:
                        for nested_key in list_nested_keys:
                            alias_path_key = nested_key.split(env_nested_delimiter)[0]
                            path_alias = dict_alias_path.get(alias_path_key, [])
                            for env_key, env_value in env_find_data.items():
                                search_key = f"{start_key_prefix}{nested_key}"
                                if env_key.startswith(search_key):
                                    key_path = nested_key.split(nested_key)
                                    found_dict = create_dict_for_path(key_path, env_value)
                                    found_dict = self._convert_env_found_value_key(
                                        list_keys_info=list_keys_info,
                                        found_value=found_dict,
                                        field_name=field_name,
                                        is_alias_path=path_alias,
                                    )
                                    nested_key_dict = deep_update(nested_key_dict, found_dict)
                    else:
                        for nested_key in reversed(list_nested_keys):
                            is_alias_path = False
                            alias_path_key = nested_key.split(env_nested_delimiter)[0]
                            if dict_alias_path.get(alias_path_key):
                                is_alias_path = True
                            exact_match_dict = dict()
                            middle_match_dict = dict()
                            lower_match_dict = dict()
                            for env_key, env_value in env_find_data.items():
                                env_nested_key = env_key[len(start_key_prefix) :]

                                if env_key.startswith(start_key_prefix):
                                    if nested_key == env_nested_key:
                                        key_path = env_nested_key.split(env_nested_delimiter)
                                        found_dict = create_dict_for_path(key_path, env_value)
                                        found_dict = self._convert_env_found_value_key(
                                            list_keys_info=list_keys_info,
                                            found_value=found_dict,
                                            field_name=field_name,
                                            is_alias_path=is_alias_path,
                                        )
                                        exact_match_dict = deep_update(exact_match_dict, found_dict)
                                    elif nested_key.lower() == env_nested_key.lower():
                                        key_path = env_nested_key.split(env_nested_delimiter)
                                        found_dict = create_dict_for_path(key_path, env_value)
                                        found_dict = self._convert_env_found_value_key(
                                            list_keys_info=list_keys_info,
                                            found_value=found_dict,
                                            field_name=field_name,
                                            is_alias_path=is_alias_path,
                                        )
                                        middle_match_dict = deep_update(middle_match_dict, found_dict)
                                elif env_key.lower().startswith(start_key_prefix):
                                    if nested_key == env_nested_key:
                                        key_path = env_nested_key.split(env_nested_delimiter)
                                        found_dict = create_dict_for_path(key_path, env_value)
                                        found_dict = self._convert_env_found_value_key(
                                            list_keys_info=list_keys_info,
                                            found_value=found_dict,
                                            field_name=field_name,
                                            is_alias_path=is_alias_path,
                                        )
                                        middle_match_dict = deep_update(middle_match_dict, found_dict)
                                    elif nested_key.lower() == env_nested_key.lower():
                                        key_path = env_nested_key.split(env_nested_delimiter)
                                        found_dict = create_dict_for_path(key_path, env_value)
                                        found_dict = self._convert_env_found_value_key(
                                            list_keys_info=list_keys_info,
                                            found_value=found_dict,
                                            field_name=field_name,
                                            is_alias_path=is_alias_path,
                                        )
                                        lower_match_dict = deep_update(lower_match_dict, found_dict)
                                else:
                                    raise ValueError(f"Unresolved nested key: {nested_key}")

                            nested_key_dict = deep_update(nested_key_dict, lower_match_dict)
                            nested_key_dict = deep_update(nested_key_dict, middle_match_dict)
                            nested_key_dict = deep_update(nested_key_dict, exact_match_dict)

        return nested_key_dict

    def _convert_env_found_value_key(
        self,
        list_keys_info: list[dict[str, list]],
        found_value: str | dict[str, Any],
        field_name: str = "",
        is_alias_path: bool = False,
    ) -> dict[str, Any]:
        """Convert found environment variable value to model field names."""

        valid_data: dict[str, Any] = dict()
        found_value_lower = dict()

        if isinstance(found_value, str):
            found_value = json.loads(found_value)

        assert isinstance(found_value, dict)

        if not self.config.env_case_sensitive:
            for k, v in found_value.items():
                k = k.lower()
                if k not in found_value_lower:
                    found_value_lower[k] = v
        for field_keys in list_keys_info:
            aliases = field_keys["aliases"]
            alias_path = field_keys["alias_path"]
            keys = field_keys["keys"]
            main_alias = aliases[0]
            result_value = PydanticUndefined

            find_dict = {}
            for alias in reversed(aliases):
                result_value = found_value.get(alias, PydanticUndefined)
                if result_value is PydanticUndefined and not self.config.env_case_sensitive:
                    alias_lower = alias.lower()
                    result_value = found_value_lower.get(alias_lower, PydanticUndefined)

                if alias in alias_path:
                    if isinstance(result_value, str):
                        result_value = json.loads(result_value)
                if result_value is not PydanticUndefined:
                    if keys and not is_alias_path and alias not in alias_path:
                        result_value = self._convert_env_found_value_key(
                            list_keys_info=keys,
                            found_value=result_value,
                            field_name=alias,
                        )
                if result_value is not PydanticUndefined:
                    if alias in alias_path:
                        if isinstance(result_value, str):
                            result_value = json.loads(result_value)
                        path_alias = alias_path[alias]
                        search_value = search_dict_for_path(
                            path_alias, {alias: result_value}, self.config.env_case_sensitive
                        )
                        if search_value is not PydanticUndefined:
                            result_value = create_dict_for_path(path_alias, search_value)
                        find_dict = deep_update(find_dict, result_value)
                    else:
                        if main_alias in alias_path:
                            path_alias = alias_path[main_alias]
                            result_value = create_dict_for_path(path_alias, result_value)
                            find_dict = deep_update(find_dict, result_value)
                        else:
                            find_dict[main_alias] = result_value
            if find_dict:
                valid_data = deep_update(valid_data, find_dict)

        return valid_data

    def secrets_ordered_settings_handler(self) -> dict[str, Any]:
        """Handles settings from secrets directory."""

        data: dict[str, Any] = {}
        if self.config.secrets_dir is None:
            return data
        data["__case_sensitive"] = self.config.case_sensitive
        if isinstance(self.config.secrets_dir, str):
            self.config.secrets_dir = Path(self.config.secrets_dir)

        assert isinstance(self.config.secrets_dir, Path)

        if not self.config.secrets_dir.is_dir():
            if self.config.ignore_missing:
                return data
            raise ArFiSettingsError(f"Missing secrets directory: `{self.config.secrets_dir.as_posix()}`")

        all_files = self.config.secrets_dir.rglob("*")
        for file in all_files:
            if not file.is_file():
                continue
            if file.suffix:
                continue
            file_name = file.stem
            try:
                data[file_name] = file.read_text(encoding=self.config.encoding).strip()
            except UnicodeDecodeError as e:
                raise ArFiSettingsError(f"Error reading file: `{file.as_posix()}`") from e

        return data

    def conf_file_ordered_settings_handler(self, mode: str | None = None) -> dict[str, Any]:
        """Handles settings from config file."""

        data: dict[str, Any] = {}
        for file_path in self.config.conf_path:
            if not file_path.is_absolute():
                if self.settings_class.BASE_DIR is not None:
                    base_dir = Path(self.settings_class.BASE_DIR).resolve()
                    file_path = Path(base_dir, file_path).resolve()
            if mode:
                file_path = file_path.parent / mode
            handler, file_path = self._find_ext_handler(file_path)
            if handler is None:
                if not self.config.conf_ignore_missing:
                    raise ArFiSettingsError(f"Missing file: `{file_path.as_posix()}`")
                continue
            data = deep_update(data, handler(file_path=file_path))

        return data

    @abstractmethod
    def default_main_handler(self) -> dict[str, Any]:
        """Main handler by default."""


class ArFiHandler(ArFiBaseHandler):
    """Handles source settings."""

    def default_main_handler(self) -> dict[str, Any]:
        """Main handler."""

        data: dict[str, Any] = {}
        mode = self.data.get("MODE", None)
        for ord_handler in reversed(self.ordered_settings):
            handler = self._get_ordered_settings_handler(ord_handler)
            handler_data = handler()
            current_mode = handler_data.get("MODE", None)
            if current_mode:
                mode = current_mode
            data[ord_handler] = handler_data

        mode_field = self.settings_class.model_fields.get("MODE")
        class_mode = mode_field.default
        mode = mode or class_mode
        if mode:
            if "conf_file_ordered_settings_handler" in self.ordered_settings:
                handler_data = self.conf_file_ordered_settings_handler(mode=mode)
                data["conf_file_ordered_settings_handler"] = deep_update(
                    data["conf_file_ordered_settings_handler"], handler_data
                )

        for ord_handler in reversed(self.ordered_settings):
            self.data = deep_update(self.data, data[ord_handler])
        return self.data
