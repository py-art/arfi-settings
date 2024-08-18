import copy
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic_core import PydanticUndefined

from .constants import ORDERED_SETTINGS, PYPROJECT_TOML_MAX_DEPTH
from .entity import (
    EnvConfigEntity as env,
    FileConfigEntity as conf,
    ModelConfigEntity as model,
)
from .errors import ArFiSettingsError
from .handlers import ArFiBaseHandler, ArFiHandler
from .schemes import (
    CONF_INCLUDE_EXLUDE_PARAMS,
    ENV_INCLUDE_EXLUDE_PARAMS,
    INCLUDE_EXLUDE_PARAMS,
    EnvConfigSchema,
    FileConfigSchema,
    PyProjectSchema,
    SettingsConfigSchema,
    SettingsParamsSchema,
)
from .types import (
    DEFAULT_PATH_SENTINEL,
    LIST_STR_SENTINEL,
    STR_SENTINEL,
    EnvConfigDict,
    FileConfigDict,
    GlobalConfigDict,
    MultiPathType,
    PathType,
)
from .utils import is_settings

if TYPE_CHECKING:
    from .main import ArFiSettings

init_settings = None


class InstanceConfig(BaseModel):
    root_dir: PathType | None = None
    base_dir: PathType | None = None
    instance: Optional[BaseModel] = None

    read_config: bool = True
    read_config_force: bool | None = None
    read_pyproject_toml: bool = True
    read_pyproject_toml_force: bool | None = None
    pyproject_toml_path: PathType | None = None
    mode_dir: PathType | None = DEFAULT_PATH_SENTINEL
    parent_mode_dir: PathType | None = DEFAULT_PATH_SENTINEL
    mode_dir_path: PathType = DEFAULT_PATH_SENTINEL
    computed_mode_dir: str = ""
    source_mode_dir: str = ""
    nested_mode_dir: PathType | None = DEFAULT_PATH_SENTINEL
    mode_dir_attr: str | None = None
    mode_dir_inherit_nested: bool = True
    mode_dir_inherit_parent: bool = True
    file_config_inherit_parent: bool = True
    env_config_inherit_parent: bool = True

    file_config: FileConfigDict = FileConfigDict()
    env_config: EnvConfigDict = EnvConfigDict()
    global_config: GlobalConfigDict = GlobalConfigDict()
    class_file_config: FileConfigSchema = FileConfigSchema()
    init_file_config: FileConfigSchema = FileConfigSchema()
    parent_file_config: FileConfigSchema = FileConfigSchema()
    computed_file_config: FileConfigDict = {}
    conf_path: list[Path] = []

    class_env_config: EnvConfigSchema = EnvConfigSchema()
    init_env_config: EnvConfigSchema = EnvConfigSchema()
    parent_env_config: EnvConfigSchema = EnvConfigSchema()
    computed_env_config: EnvConfigDict = {}
    env_path: list[Path] = []

    handler_class: type[ArFiBaseHandler] = ArFiHandler
    handler: str = "default_main_handler"
    handler_inherit_parent: bool = True
    ordered_settings: list[str] = ORDERED_SETTINGS
    ordered_settings_inherit_parent: bool = True

    settings_config: Optional[SettingsConfigSchema] = None
    class_settings_config: Optional[SettingsConfigSchema] = None
    settings_init_params: SettingsParamsSchema = SettingsParamsSchema()
    values_by_default: dict[str, Any] = {}
    init_kwargs: dict[str, Any] = {}
    handler_tree: list[list[str]] = []
    handler_parent_mode_dir: list[str | Path] = []

    modified_class_vars: set[str] = set()
    inherited_params: list[str] = []
    search_base_dir: bool = True
    init_params: PyProjectSchema = PyProjectSchema()

    _class_vars: ClassVar[set[str]] = {
        "instance",
        "class_file_config",
        "class_env_config",
        "class_settings_config",
        "handler_class",
        "arfi_dev_debug",
        "modified_class_vars",
        "init_kwargs",
        "file_config",
        "env_config",
        "global_config",
        "read_pyproject_toml_force",
        "init_params",
    }
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        validate_default=False,
        validate_return=False,
    )

    # TODO: append read arfi_dev_debug from ./config/arfi_dev_debug.toml
    arfi_dev_debug: bool = False
    arfi_debug: bool = False

    def load(
        self,
        instance: "ArFiSettings",
        _read_config: bool = None,
        _read_config_force: bool = None,
        _read_pyproject_toml: bool | None = None,
        _pyproject_toml_depth: int | None = None,
        _pyproject_toml_max_depth: int = PYPROJECT_TOML_MAX_DEPTH,
        _mode_dir: PathType | None = DEFAULT_PATH_SENTINEL,
        _mode_dir_inherit_nested: bool = None,
        _mode_dir_inherit_parent: bool = None,
        _file_config_inherit_parent: bool = None,
        _env_config_inherit_parent: bool = None,
        _conf_file: MultiPathType | None = DEFAULT_PATH_SENTINEL,
        _conf_dir: MultiPathType | None = DEFAULT_PATH_SENTINEL,
        _conf_ext: str | list[str, ...] = [],
        _conf_file_encoding: str | None = STR_SENTINEL,
        _conf_case_sensitive: bool = None,
        _conf_ignore_missing: bool = None,
        _conf_custom_ext_handler: str | dict[str, str] | None = STR_SENTINEL,
        _conf_include_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS], ...] = None,
        _conf_exclude_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS], ...] = None,
        _env_file: MultiPathType | None = DEFAULT_PATH_SENTINEL,
        _env_prefix: str = None,
        _env_prefix_as_mode_dir: bool = None,
        _env_prefix_as_nested_mode_dir: bool = None,
        _env_prefix_as_source_mode_dir: bool = None,
        _env_file_encoding: str | None = STR_SENTINEL,
        _env_case_sensitive: bool = None,
        _env_nested_delimiter: str = None,
        _env_ignore_missing: bool = None,
        _env_include_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS], ...] = None,
        _env_exclude_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS], ...] = None,
        _case_sensitive: bool = None,
        _ignore_missing: bool = None,
        _encoding: str | None = STR_SENTINEL,
        _secrets_dir: PathType | None = DEFAULT_PATH_SENTINEL,
        _include_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS], ...] = None,
        _exclude_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS], ...] = None,
        _handler: str = STR_SENTINEL,
        _handler_inherit_parent: bool = None,
        _ordered_settings: list[str, ...] = LIST_STR_SENTINEL,
        _ordered_settings_inherit_parent: bool = None,
        _cli: bool = None,
        **kwargs,
    ) -> None:
        """Load settings configuration and params."""

        global init_settings
        # Don't move to global scope !!!
        from .init_config import init_settings

        values = kwargs.get("values", {})
        self._setup_instance_and_default_value(instance, **values)

        _kwargs: dict = locals()
        _kwargs.pop("self")
        self.settings_init_params.update_exclude_default(**_kwargs)
        if not self.init_kwargs:
            self.init_kwargs = self.settings_init_params.model_dump(exclude_defaults=True)

        self._setup_params_from_handler(
            values,
            _mode_dir_inherit_parent,
            _file_config_inherit_parent,
            _env_config_inherit_parent,
            _ordered_settings_inherit_parent,
            _handler_inherit_parent,
        )
        if self.mode_dir == DEFAULT_PATH_SENTINEL:
            if self.mode_dir_attr and self.mode_dir_attr != DEFAULT_PATH_SENTINEL:
                self.mode_dir = self.mode_dir_attr
        self.source_mode_dir = self.instance_source_mode_dir

        _kwargs = self.settings_init_params.get_param_dict()
        _read_config = _kwargs.get("_read_config", _read_config)
        _read_config_force = _kwargs.get("_read_config_force", _read_config_force)
        self._setup_read_config(
            _read_config=_read_config,
            _read_config_force=_read_config_force,
        )
        handler = _kwargs.pop("_handler")
        if handler:
            self.handler = handler
        if self.values_by_default:
            self.values_by_default.update(values)
            values = self.values_by_default

        ################ PYPROJECT ################
        if _read_pyproject_toml is not None:
            self.read_pyproject_toml = _read_pyproject_toml

        if self._need_read_pyproject(
            _read_config=_read_config,
            _read_config_force=_read_config_force,
        ):
            init_settings.read_pyproject(
                read_pyproject_toml=self.read_pyproject_toml,
                pyproject_toml_depth=_pyproject_toml_depth,
                pyproject_toml_max_depth=_pyproject_toml_max_depth,
                class_name=instance.__class__.__name__,
                search_base_dir=self.search_base_dir,
            )
        if _read_pyproject_toml is not False:
            self.init_params = init_settings.init_params

        if self.pyproject_toml_path != init_settings.pyproject_toml_path:
            if self.pyproject_toml_path is not None:
                warnings.warn_explicit(
                    f"\033[33m\n"
                    f"Path to pyproject.toml has been changed !!!\n"
                    f"for instance {instance.__class__.__name__}()\n"
                    f"inside class {init_settings.main_config_class}\n"
                    f"    previous path:\n"
                    f"{self.pyproject_toml_path.as_posix()}\n"
                    f"    current path:\n"
                    f"{init_settings.pyproject_toml_path.as_posix()}\n"
                    f"Call once\n"
                    f"  from arfi_settings.init_config import init_settings\n"
                    f"  init_settings.read_pyproject(read_once=True)\n"
                    f"before import any instance or subclass `ArFiSettings` for fix it."
                    f"\033[0m",
                    category=Warning,
                    filename=init_settings.main_config_file.as_posix(),
                    lineno=init_settings.called_line,
                )

        self.pyproject_toml_path = init_settings.pyproject_toml_path
        self._setup_class_vars_from_pyproject_toml_or_by_default()
        self._setup_config_dict_variables_from_pyproject_toml_or_by_default()
        ################ END PYPROJECT ################

        if self.read_config:
            _kwargs["_read_config"] = self.read_config
            self._setup_params(**_kwargs)

        self.arfi_debug = init_settings.init_params.arfi_debug
        return values

    def _setup_read_config(
        self,
        _read_config: bool = None,
        _read_config_force: bool = None,
    ):
        """Setup read_config."""

        if _read_config is not None:
            self.read_config = _read_config
        if _read_config_force is not None:
            self.read_config_force = _read_config_force
        if self.read_config_force is not None:
            self.read_config = self.read_config_force

    def _need_read_pyproject(
        self,
        _read_config: bool = None,
        _read_config_force: bool = None,
    ) -> bool:
        """Checking whether the pyproject.toml file needs to be read."""

        need_read = self.read_pyproject_toml
        read_config_force = self.read_config_force

        if _read_config is not None:
            read_config_force = _read_config
        if _read_config_force is not None:
            read_config_force = _read_config_force
        if read_config_force is not None:
            need_read = read_config_force
        # from handler read_pyproject_toml_force always False
        if self.read_pyproject_toml_force is not None:
            need_read = self.read_pyproject_toml_force
        return need_read

    def _setup_params_from_handler(
        self,
        values: dict[str, Any],
        _mode_dir_inherit_parent: bool = None,
        _file_config_inherit_parent: bool = None,
        _env_config_inherit_parent: bool = None,
        _ordered_settings_inherit_parent: bool = None,
        _handler_inherit_parent: bool = None,
    ) -> None:
        """Setup params from handler."""

        if _handler_tree := values.get("_handler_tree"):
            self.handler_tree = _handler_tree
        if _handler_mode_dir_attr := values.get("_handler_mode_dir_attr"):
            self.mode_dir_attr = _handler_mode_dir_attr
        if _handler_parent_mode_dir := values.get("_handler_parent_mode_dir"):
            self.handler_parent_mode_dir = _handler_parent_mode_dir
            parent_mode_dir = Path(*_handler_parent_mode_dir).as_posix().strip(".")
            self.parent_mode_dir = parent_mode_dir or DEFAULT_PATH_SENTINEL
        if _handler_ordered_settings := values.get("_handler_ordered_settings"):
            if self.ordered_settings_inherit_parent and _ordered_settings_inherit_parent is not False:
                _init_ordered_settings_inherit_parent = self.init_kwargs.get("ordered_settings_inherit_parent")
                if _init_ordered_settings_inherit_parent is not False:
                    self.ordered_settings = [
                        handler_name.replace("_ordered_settings_handler", "")
                        for handler_name in _handler_ordered_settings
                    ]
        if _handler_parent_file_config := values.get("_handler_parent_file_config"):
            if self.file_config_inherit_parent and _file_config_inherit_parent is not False:
                self.parent_file_config = _handler_parent_file_config
        if _handler_parent_env_config := values.get("_handler_parent_env_config"):
            if self.env_config_inherit_parent and _env_config_inherit_parent is not False:
                self.parent_env_config = _handler_parent_env_config
        _handler_read_pyproject_toml_force = values.get("_handler_read_pyproject_toml_force")
        if _handler_read_pyproject_toml_force is not None:
            self.read_pyproject_toml_force = _handler_read_pyproject_toml_force
        _handler_search_base_dir = values.get("_handler_search_base_dir")
        if _handler_search_base_dir is not None:
            self.search_base_dir = _handler_search_base_dir
        if _handler_main_handler := values.get("_handler_main_handler"):
            if self.handler_inherit_parent and _handler_inherit_parent is not False:
                self.handler = _handler_main_handler

    def _setup_class_vars_from_pyproject_toml_or_by_default(self) -> None:
        """Re-reads variables depending on the current path of the pyproject.toml file."""

        pyproject_or_default_fields = self.init_params.model_fields
        # Fields explicitly set by the user in the class
        modified_class_vars = self.instance._modified_class_vars
        # for field_name in self.model_fields.keys():
        for field_name in self.model_fields.keys():
            if field_name in pyproject_or_default_fields:
                instance_field_name = f"_{field_name}"
                if hasattr(self.instance, instance_field_name):
                    if field_name not in modified_class_vars:
                        field_value = getattr(self.init_params, field_name)
                    else:
                        field_value = getattr(self.instance, instance_field_name)
                    if field_name == "handler":
                        if field_value != self.handler and self.handler != "default_main_handler":
                            field_value = self.handler
                    if field_name == "ordered_settings":
                        if field_value != self.ordered_settings and self.ordered_settings != ORDERED_SETTINGS:
                            field_value = self.ordered_settings
                    setattr(self, field_name, field_value)

        self.base_dir = init_settings.base_dir
        self.root_dir = init_settings.root_dir
        if not self.base_dir and not self.search_base_dir and self.instance.BASE_DIR:
            self.base_dir = self.instance.BASE_DIR

    def _setup_config_dict_variables_from_pyproject_toml_or_by_default(self) -> None:
        """Re-reads variables depending on the current path of the pyproject.toml file."""

        # Always reset the settings
        self.class_settings_config = SettingsConfigSchema()
        self.class_file_config = FileConfigSchema()
        self.class_env_config = EnvConfigSchema()

        global_config_keys = list(SettingsConfigSchema.model_fields.keys())
        file_config_keys = list(FileConfigSchema.model_fields.keys())
        env_config_keys = list(EnvConfigSchema.model_fields.keys())
        extra_keys = ["conf_path", "env_path"]
        # setup simple keys
        for key in global_config_keys:
            if key in extra_keys:
                continue
            if key in file_config_keys:
                value = self.file_config.get(key, PydanticUndefined)
                if value is PydanticUndefined:
                    value = self.global_config.get(key, getattr(self.init_params, key))
                setattr(self.class_file_config, key, value)
                setattr(self.class_settings_config, key, value)
            elif key in env_config_keys:
                value = self.env_config.get(key, PydanticUndefined)
                if value is PydanticUndefined:
                    value = self.global_config.get(key, getattr(self.init_params, key))
                setattr(self.class_env_config, key, value)
                setattr(self.class_settings_config, key, value)
            else:
                value = self.global_config.get(key, getattr(self.init_params, key))
                setattr(self.class_settings_config, key, value)

        # SETUP COMMON VALUES
        # ENCODING
        encoding = self.global_config.get(model.ENCODING, self.init_params.encoding)
        self.class_settings_config.encoding = encoding
        conf_file_encoding = self.file_config.get(conf.FILE_ENCODING, PydanticUndefined)
        if conf_file_encoding is PydanticUndefined:
            conf_file_encoding = self.global_config.get(conf.FILE_ENCODING, PydanticUndefined)
        if conf_file_encoding is PydanticUndefined:
            conf_file_encoding = self.init_params.conf_file_encoding or encoding
        self.class_file_config.conf_file_encoding = conf_file_encoding
        self.class_settings_config.conf_file_encoding = conf_file_encoding

        env_file_encoding = self.env_config.get(env.FILE_ENCODING, PydanticUndefined)
        if env_file_encoding is PydanticUndefined:
            env_file_encoding = self.global_config.get(env.FILE_ENCODING, PydanticUndefined)
        if env_file_encoding is PydanticUndefined:
            env_file_encoding = self.init_params.env_file_encoding or encoding
        self.class_env_config.env_file_encoding = env_file_encoding
        self.class_settings_config.env_file_encoding = env_file_encoding

        # CASE SENSITIVE
        case_sensitive = self.global_config.get(model.CASE_SENSITIVE, self.init_params.case_sensitive)
        self.class_settings_config.case_sensitive = case_sensitive
        conf_case_sensitive = self.file_config.get(conf.CASE_SENSITIVE, PydanticUndefined)
        if conf_case_sensitive is PydanticUndefined:
            conf_case_sensitive = self.global_config.get(conf.CASE_SENSITIVE, PydanticUndefined)
        if conf_case_sensitive is PydanticUndefined:
            conf_case_sensitive = self.init_params.conf_case_sensitive
        if conf_case_sensitive is None:
            conf_case_sensitive = case_sensitive
        self.class_file_config.conf_case_sensitive = conf_case_sensitive
        self.class_settings_config.conf_case_sensitive = conf_case_sensitive

        env_case_sensitive = self.env_config.get(env.CASE_SENSITIVE, PydanticUndefined)
        if env_case_sensitive is PydanticUndefined:
            env_case_sensitive = self.global_config.get(env.CASE_SENSITIVE, PydanticUndefined)
        if env_case_sensitive is PydanticUndefined:
            env_case_sensitive = self.init_params.env_case_sensitive
        if env_case_sensitive is None:
            env_case_sensitive = case_sensitive
        self.class_env_config.env_case_sensitive = env_case_sensitive
        self.class_settings_config.env_case_sensitive = env_case_sensitive

        # IGNORE MISSING
        ignore_missing = self.global_config.get(model.IGNORE_MISSING, self.init_params.ignore_missing)
        self.class_settings_config.ignore_missing = ignore_missing
        conf_ignore_missing = self.file_config.get(conf.IGNORE_MISSING, PydanticUndefined)
        if conf_ignore_missing is PydanticUndefined:
            conf_ignore_missing = self.global_config.get(conf.IGNORE_MISSING, PydanticUndefined)
        if conf_ignore_missing is PydanticUndefined:
            conf_ignore_missing = self.init_params.conf_ignore_missing
        if conf_ignore_missing is None:
            conf_ignore_missing = ignore_missing
        self.class_file_config.conf_ignore_missing = conf_ignore_missing
        self.class_settings_config.conf_ignore_missing = conf_ignore_missing

        env_ignore_missing = self.env_config.get(env.IGNORE_MISSING, PydanticUndefined)
        if env_ignore_missing is PydanticUndefined:
            env_ignore_missing = self.global_config.get(env.IGNORE_MISSING, PydanticUndefined)
        if env_ignore_missing is PydanticUndefined:
            env_ignore_missing = self.init_params.env_ignore_missing
        if env_ignore_missing is None:
            env_ignore_missing = ignore_missing
        self.class_env_config.env_ignore_missing = env_ignore_missing
        self.class_settings_config.env_ignore_missing = env_ignore_missing

        # check custom_ext_handler
        if not self.class_file_config.conf_ext or self.class_file_config.conf_ext == LIST_STR_SENTINEL:
            try:
                assert (
                    self.class_file_config.conf_custom_ext_handler
                ), "`conf_custom_ext_handler` must be defined if conf_ext is empty"
            except AssertionError as e:
                raise ArFiSettingsError(e) from e

        # setup include and exclude inherit parent params
        include_inherit_parent = self.class_settings_config.include_inherit_parent or []
        exclude_inherit_parent = self.class_settings_config.exclude_inherit_parent or []
        conf_include_inherit_parent = self.class_file_config.conf_include_inherit_parent or []
        conf_exclude_inherit_parent = self.class_file_config.conf_exclude_inherit_parent or []
        env_include_inherit_parent = self.class_env_config.env_include_inherit_parent or []
        env_exclude_inherit_parent = self.class_env_config.env_exclude_inherit_parent or []

        class_include_inherit_parent = []
        class_exclude_inherit_parent = []
        class_conf_include_inherit_parent = []
        class_conf_exclude_inherit_parent = []
        class_env_include_inherit_parent = []
        class_env_exclude_inherit_parent = []

        if not conf_exclude_inherit_parent:
            for e in exclude_inherit_parent:
                if e in CONF_INCLUDE_EXLUDE_PARAMS:
                    class_conf_exclude_inherit_parent.append(e)
        else:
            class_conf_exclude_inherit_parent.extend(conf_exclude_inherit_parent)

        if not env_exclude_inherit_parent:
            for e in exclude_inherit_parent:
                if e in ENV_INCLUDE_EXLUDE_PARAMS:
                    class_env_exclude_inherit_parent.append(e)
        else:
            class_env_exclude_inherit_parent.extend(env_exclude_inherit_parent)

        class_exclude_inherit_parent.extend(class_conf_exclude_inherit_parent)
        class_exclude_inherit_parent.extend(class_env_exclude_inherit_parent)

        for ci in conf_include_inherit_parent:
            if ci not in class_conf_exclude_inherit_parent:
                if class_conf_exclude_inherit_parent and ci in class_conf_exclude_inherit_parent:
                    continue
                class_conf_include_inherit_parent.append(ci)

        if not class_conf_include_inherit_parent:
            for i in include_inherit_parent:
                if i in CONF_INCLUDE_EXLUDE_PARAMS:
                    if class_conf_exclude_inherit_parent and i in class_conf_exclude_inherit_parent:
                        continue
                    class_conf_include_inherit_parent.append(i)

        for ei in env_include_inherit_parent:
            if ei not in class_env_exclude_inherit_parent:
                if class_env_exclude_inherit_parent and ei in class_env_exclude_inherit_parent:
                    continue
                class_env_include_inherit_parent.append(ei)

        if not class_env_include_inherit_parent:
            for i in include_inherit_parent:
                if i in ENV_INCLUDE_EXLUDE_PARAMS:
                    if class_env_exclude_inherit_parent and i in class_env_exclude_inherit_parent:
                        continue
                    class_env_include_inherit_parent.append(i)

        class_include_inherit_parent.extend(class_conf_include_inherit_parent)
        class_include_inherit_parent.extend(class_env_include_inherit_parent)
        self.class_file_config.conf_include_inherit_parent = class_conf_include_inherit_parent
        self.class_file_config.conf_exclude_inherit_parent = class_conf_exclude_inherit_parent
        self.class_env_config.env_include_inherit_parent = class_env_include_inherit_parent
        self.class_env_config.env_exclude_inherit_parent = class_env_exclude_inherit_parent
        self.class_settings_config.conf_include_inherit_parent = class_conf_include_inherit_parent
        self.class_settings_config.conf_exclude_inherit_parent = class_conf_exclude_inherit_parent
        self.class_settings_config.env_include_inherit_parent = class_env_include_inherit_parent
        self.class_settings_config.env_exclude_inherit_parent = class_env_exclude_inherit_parent
        self.class_settings_config.include_inherit_parent = class_include_inherit_parent
        self.class_settings_config.exclude_inherit_parent = class_exclude_inherit_parent

        self.settings_config = self.class_settings_config

    def _setup_instance_and_default_value(self, instance: "ArFiSettings", **values) -> None:
        """Setup default value from class."""

        if self.instance is not None:
            return
        # setup class constants
        self.instance = instance
        if isinstance(instance.handler, str):
            self.handler = instance.handler
        self.handler_inherit_parent = instance.handler_inherit_parent
        self.handler_class = instance.handler_class
        self.read_config = instance.read_config
        self.read_config_force = instance.read_config_force
        self.read_pyproject_toml = instance.read_pyproject_toml
        self.mode_dir = instance._mode_dir
        self.search_base_dir = instance._search_base_dir
        self.mode_dir_attr = instance._mode_dir_attr

        # setup class config
        self.file_config = instance.file_config
        self.env_config = instance.env_config
        self.global_config = GlobalConfigDict()
        for key, value in instance.model_config.items():
            if key in list(init_settings.init_params.model_fields.keys()):
                self.global_config[key] = value

        # setup default value
        self.values_by_default = dict(values) or {}

        # search nested mode_dir
        for base in type(instance).__bases__:
            if hasattr(base, "mode_dir"):
                self.nested_mode_dir = getattr(base, "mode_dir")
                break

    def _setup_params(
        self,
        _read_config: bool = None,
        _read_config_force: bool = None,
        _mode_dir: PathType | None = DEFAULT_PATH_SENTINEL,
        _mode_dir_inherit_nested: bool = None,
        _mode_dir_inherit_parent: bool = None,
        _file_config_inherit_parent: bool = None,
        _env_config_inherit_parent: bool = None,
        _conf_file: MultiPathType | None = DEFAULT_PATH_SENTINEL,
        _conf_dir: MultiPathType | None = DEFAULT_PATH_SENTINEL,
        _conf_ext: str | list[str, ...] = [],
        _conf_file_encoding: str | None = STR_SENTINEL,
        _conf_case_sensitive: bool = None,
        _conf_ignore_missing: bool = None,
        _conf_custom_ext_handler: str | dict[str, str] | None = STR_SENTINEL,
        _conf_include_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS], ...] = None,
        _conf_exclude_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS], ...] = None,
        _env_file: MultiPathType | None = DEFAULT_PATH_SENTINEL,
        _env_prefix: str = None,
        _env_prefix_as_mode_dir: bool = None,
        _env_prefix_as_nested_mode_dir: bool = None,
        _env_prefix_as_source_mode_dir: bool = None,
        _env_file_encoding: str | None = STR_SENTINEL,
        _env_case_sensitive: bool = None,
        _env_nested_delimiter: str = None,
        _env_ignore_missing: bool = None,
        _env_include_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS], ...] = None,
        _env_exclude_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS], ...] = None,
        _case_sensitive: bool = None,
        _ignore_missing: bool = None,
        _encoding: str | None = STR_SENTINEL,
        _secrets_dir: PathType | None = DEFAULT_PATH_SENTINEL,
        _include_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS], ...] = None,
        _exclude_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS], ...] = None,
        _handler_inherit_parent: bool = None,
        _ordered_settings: list[str, ...] = LIST_STR_SENTINEL,
        _ordered_settings_inherit_parent: bool = None,
        _cli: bool = None,
    ):
        """Load config params."""

        if _mode_dir != DEFAULT_PATH_SENTINEL:
            self.mode_dir = _mode_dir
        if _mode_dir_inherit_nested is not None:
            self.mode_dir_inherit_nested = _mode_dir_inherit_nested
        if _mode_dir_inherit_parent is not None:
            self.mode_dir_inherit_parent = _mode_dir_inherit_parent
        if _file_config_inherit_parent is not None:
            self.file_config_inherit_parent = _file_config_inherit_parent
        if _env_config_inherit_parent is not None:
            self.env_config_inherit_parent = _env_config_inherit_parent
        if _handler_inherit_parent is not None:
            self.handler_inherit_parent = _handler_inherit_parent
        # ORDERED_SETTINGS
        if _ordered_settings_inherit_parent is not None:
            self.ordered_settings_inherit_parent = _ordered_settings_inherit_parent
        _init_ordered_settings_inherit_parent = self.init_kwargs.get("ordered_settings_inherit_parent")
        if _init_ordered_settings_inherit_parent is not None:
            self.ordered_settings_inherit_parent = _init_ordered_settings_inherit_parent
        if self.ordered_settings_inherit_parent is False:
            if _ordered_settings != LIST_STR_SENTINEL:
                self.ordered_settings = _ordered_settings

        if _case_sensitive is not None:
            if _conf_case_sensitive is None:
                _conf_case_sensitive = _case_sensitive
            if _env_case_sensitive is None:
                _env_case_sensitive = _case_sensitive

        if _ignore_missing is not None:
            if _conf_ignore_missing is None:
                _conf_ignore_missing = _ignore_missing
            if _env_ignore_missing is None:
                _env_ignore_missing = _ignore_missing

        if _encoding is not STR_SENTINEL:
            if _conf_file_encoding is STR_SENTINEL:
                _conf_file_encoding = _encoding
            if _env_file_encoding is STR_SENTINEL:
                _env_file_encoding = _encoding

        exclude_inherit_parent = self.settings_init_params.exclude_inherit_parent
        include_inherit_parent = self.settings_init_params.include_inherit_parent

        if not _env_exclude_inherit_parent and exclude_inherit_parent:
            _env_exclude_inherit_parent = []
            for ee in exclude_inherit_parent:
                if ee in ENV_INCLUDE_EXLUDE_PARAMS:
                    _env_exclude_inherit_parent.append(ee)

        if not _env_include_inherit_parent and include_inherit_parent:
            _env_include_inherit_parent = []
            for ei in include_inherit_parent:
                if ei in ENV_INCLUDE_EXLUDE_PARAMS:
                    if _env_exclude_inherit_parent and ei in _env_exclude_inherit_parent:
                        continue
                    _env_include_inherit_parent.append(ei)

        if not _conf_exclude_inherit_parent and exclude_inherit_parent:
            _conf_exclude_inherit_parent = []
            for ce in exclude_inherit_parent:
                if ce in CONF_INCLUDE_EXLUDE_PARAMS:
                    _conf_exclude_inherit_parent.append(ce)

        if not _conf_include_inherit_parent and include_inherit_parent:
            _conf_include_inherit_parent = []
            for ci in include_inherit_parent:
                if ci in CONF_INCLUDE_EXLUDE_PARAMS:
                    if _conf_exclude_inherit_parent and ci in _conf_exclude_inherit_parent:
                        continue
                    _conf_include_inherit_parent.append(ci)

        self.init_file_config = FileConfigSchema(
            conf_file=_conf_file,
            conf_dir=_conf_dir,
            conf_ext=_conf_ext,
            conf_file_encoding=_conf_file_encoding,
            conf_case_sensitive=_conf_case_sensitive,
            conf_ignore_missing=_conf_ignore_missing,
            conf_custom_ext_handler=_conf_custom_ext_handler,
            conf_include_inherit_parent=_conf_include_inherit_parent,
            conf_exclude_inherit_parent=_conf_exclude_inherit_parent,
        )
        self.init_env_config = EnvConfigSchema(
            env_file=_env_file,
            env_prefix=_env_prefix,
            env_prefix_as_mode_dir=_env_prefix_as_mode_dir,
            env_prefix_as_nested_mode_dir=_env_prefix_as_nested_mode_dir,
            env_prefix_as_source_mode_dir=_env_prefix_as_source_mode_dir,
            env_file_encoding=_env_file_encoding,
            env_case_sensitive=_env_case_sensitive,
            env_nested_delimiter=_env_nested_delimiter,
            env_ignore_missing=_env_ignore_missing,
            env_include_inherit_parent=_env_include_inherit_parent,
            env_exclude_inherit_parent=_env_exclude_inherit_parent,
        )
        if self.init_file_config.conf_include_inherit_parent or self.init_env_config.env_include_inherit_parent:
            self.settings_init_params.include_inherit_parent = []
            if self.init_file_config.conf_include_inherit_parent:
                self.settings_init_params.conf_include_inherit_parent = (
                    self.init_file_config.conf_include_inherit_parent
                )
                self.settings_init_params.include_inherit_parent.extend(
                    self.init_file_config.conf_include_inherit_parent
                )
            if self.init_env_config.env_include_inherit_parent:
                self.settings_init_params.env_include_inherit_parent = self.init_env_config.env_include_inherit_parent
                self.settings_init_params.include_inherit_parent.extend(self.init_env_config.env_include_inherit_parent)

        if self.init_file_config.conf_exclude_inherit_parent or self.init_env_config.env_exclude_inherit_parent:
            self.settings_init_params.exclude_inherit_parent = []
            if self.init_file_config.conf_exclude_inherit_parent:
                self.settings_init_params.conf_exclude_inherit_parent = (
                    self.init_file_config.conf_exclude_inherit_parent
                )
                self.settings_init_params.exclude_inherit_parent.extend(
                    self.init_file_config.conf_exclude_inherit_parent
                )
            if self.init_env_config.env_exclude_inherit_parent:
                self.settings_init_params.env_exclude_inherit_parent = self.init_env_config.env_exclude_inherit_parent
                self.settings_init_params.exclude_inherit_parent.extend(self.init_env_config.env_exclude_inherit_parent)

        # Very important place !!!
        # here computes and updates the main settings config
        self._compute_include_exclude_inherit_parent()  # Important: must run before computes file and env config
        self.computed_file_config = self.instance_computed_file_config
        self.computed_env_config = self.instance_computed_env_config

        self.settings_config.update(**self.computed_file_config)
        self.settings_config.update(**self.computed_env_config)

        self.mode_dir_path = self.instance_mode_dir_path
        self.computed_mode_dir = self.instance_computed_mode_dir
        if _case_sensitive is not None:
            self.settings_config.case_sensitive = _case_sensitive
        if _ignore_missing is not None:
            self.settings_config.ignore_missing = _ignore_missing
        if _encoding is not STR_SENTINEL:
            self.settings_config.encoding = _encoding
        if _secrets_dir != DEFAULT_PATH_SENTINEL:
            self.settings_config.secrets_dir = _secrets_dir
        if _cli is not None:
            self.settings_config.cli = _cli
        self.conf_path = self.instance_conf_path
        self.env_path = self.instance_env_path
        self.settings_config.update(
            **dict(
                conf_path=self.conf_path,
                env_path=self.env_path,
            )
        )

    @property
    def instance_mode_dir_path(self) -> PathType:
        """Generate path to mode directory."""

        if self.parent_mode_dir and self.parent_mode_dir != DEFAULT_PATH_SENTINEL and self.mode_dir_inherit_parent:
            if self.nested_mode_dir and self.nested_mode_dir != DEFAULT_PATH_SENTINEL and self.mode_dir_inherit_nested:
                return Path(self.parent_mode_dir, self.nested_mode_dir, self.mode_dir or "")
            return Path(self.parent_mode_dir, self.mode_dir or "")
        elif self.nested_mode_dir and self.nested_mode_dir != DEFAULT_PATH_SENTINEL and self.mode_dir_inherit_nested:
            return Path(self.nested_mode_dir, self.mode_dir or "")
        else:
            return Path(self.mode_dir or "")

    @property
    def instance_computed_mode_dir(self) -> str:
        return self.instance_mode_dir_path.as_posix().strip(".")

    @property
    def instance_computed_nested_mode_dir(self) -> str:
        """Compute nested_mode_dir."""

        if self.nested_mode_dir and self.nested_mode_dir != DEFAULT_PATH_SENTINEL and self.mode_dir_inherit_nested:
            return Path(self.nested_mode_dir, self.mode_dir or "").as_posix().strip(".")
        else:
            return Path(self.mode_dir or "").as_posix().strip(".")

    @property
    def instance_source_mode_dir(self) -> str:
        if isinstance(self.mode_dir, Path):
            return self.mode_dir.as_posix()
        return self.mode_dir or ""

    @property
    def instance_conf_path(self) -> list[Path]:
        """Create full config path from file and dir settings."""

        conf_path = []
        conf_file = self.computed_file_config.get(conf.FILE)
        if not conf_file:
            return conf_path
        if isinstance(conf_file, (str, Path)):
            conf_file = [Path(conf_file)]
        try:
            assert isinstance(
                conf_file, (list, tuple)
            ), f"{self.instance.__class__.__name__}.file_config['{conf.FILE}'] type must be a arfi_settings.MultiPathType"
        except AssertionError as e:
            raise ArFiSettingsError(e) from e

        conf_dir = self.computed_file_config.get(conf.DIR) or ""
        if isinstance(conf_dir, (str, Path)):
            conf_dir = [Path(conf_dir)]
        try:
            assert isinstance(
                conf_dir, (list, tuple)
            ), f"{self.instance.__class__.__name__}.file_config['{conf.DIR}'] type must be a arfi_settings.MultiPathType"
        except AssertionError as e:
            raise ArFiSettingsError(e) from e

        for directory in conf_dir:
            directory = Path(directory).expanduser()
            for file in conf_file:
                file = Path(file).expanduser()
                path = Path(directory, self.instance_mode_dir_path, file).expanduser()
                conf_path.append(path)
        return conf_path

    @property
    def instance_env_path(self) -> list[Path]:
        """Create full env path from file and dir settings."""

        env_path = []
        env_file = self.computed_env_config.get(env.FILE)
        if not env_file:
            return env_path
        if isinstance(env_file, (str, Path)):
            env_file = [Path(env_file)]
        try:
            assert isinstance(
                env_file, (list, tuple)
            ), f"{self.instance.__class__.__name__}.env_config['{env.FILE}'] must be a arfi_settings.MultiPathType"
        except AssertionError as e:
            raise ArFiSettingsError(e) from e

        for file in env_file:
            path = Path(file).expanduser()
            env_path.append(path)
        return env_path

    @property
    def instance_computed_file_config(self) -> FileConfigDict:
        """Compute file_config."""

        file_config = copy.deepcopy(self.class_file_config)
        file_config.conf_include_inherit_parent = self.settings_config.conf_include_inherit_parent
        file_config.conf_exclude_inherit_parent = self.settings_config.conf_exclude_inherit_parent
        if self.file_config_inherit_parent:
            parent_file_config = self.parent_file_config.model_dump(exclude_defaults=True)
            if file_config.conf_include_inherit_parent:
                for key, value in parent_file_config.items():
                    if key in file_config.conf_include_inherit_parent:
                        if key not in ["conf_include_inherit_parent", "conf_exclude_inherit_parent"]:
                            setattr(file_config, key, value)
                            self.inherited_params.append(key)
            elif file_config.conf_exclude_inherit_parent:
                for key, value in parent_file_config.items():
                    if key not in file_config.conf_exclude_inherit_parent:
                        if key not in ["conf_include_inherit_parent", "conf_exclude_inherit_parent"]:
                            setattr(file_config, key, value)
                            self.inherited_params.append(key)
            else:
                for key, value in parent_file_config.items():
                    if key not in ["conf_include_inherit_parent", "conf_exclude_inherit_parent"]:
                        setattr(file_config, key, value)
                        self.inherited_params.append(key)

        init_file_config = self.init_file_config.model_dump(exclude_defaults=True)
        for key, value in init_file_config.items():
            if key not in ["conf_include_inherit_parent", "conf_exclude_inherit_parent"]:
                setattr(file_config, key, value)

        return file_config.conf_dict

    @property
    def instance_computed_env_config(self) -> EnvConfigDict:
        """Compute env_config."""

        env_config = copy.deepcopy(self.class_env_config)
        env_config.env_include_inherit_parent = self.settings_config.env_include_inherit_parent
        env_config.env_exclude_inherit_parent = self.settings_config.env_exclude_inherit_parent
        if self.env_config_inherit_parent:
            parent_env_config = self.parent_env_config.model_dump(exclude_defaults=True)
            if env_config.env_include_inherit_parent:
                for key, value in parent_env_config.items():
                    if key in env_config.env_include_inherit_parent:
                        if key not in ["env_include_inherit_parent", "env_exclude_inherit_parent"]:
                            setattr(env_config, key, value)
                            self.inherited_params.append(key)
            elif env_config.env_exclude_inherit_parent:
                for key, value in parent_env_config.items():
                    if key not in env_config.env_exclude_inherit_parent:
                        if key not in ["env_include_inherit_parent", "env_exclude_inherit_parent"]:
                            setattr(env_config, key, value)
                            self.inherited_params.append(key)
            else:
                for key, value in parent_env_config.items():
                    if key not in ["env_include_inherit_parent", "env_exclude_inherit_parent"]:
                        setattr(env_config, key, value)
                        self.inherited_params.append(key)

        init_env_config = self.init_env_config.model_dump(exclude_defaults=True)
        for key, value in init_env_config.items():
            if key not in ["env_include_inherit_parent", "env_exclude_inherit_parent"]:
                setattr(env_config, key, value)

        # search env prefix
        env_prefix = env_config.env_prefix
        found_env_prefix = ""
        if env_config.env_prefix_as_mode_dir:
            found_env_prefix = self.instance_computed_mode_dir.replace("/", "_").strip(".")
        if env_config.env_prefix_as_nested_mode_dir:
            found_env_prefix = self.instance_computed_nested_mode_dir.replace("/", "_").strip(".")
        if env_config.env_prefix_as_source_mode_dir:
            found_env_prefix = self.instance_source_mode_dir.replace("/", "_").strip(".")
        if found_env_prefix:
            env_prefix = f"{found_env_prefix}_"
        env_config.env_prefix = env_prefix

        return env_config.env_dict

    def _compute_include_exclude_inherit_parent(self) -> None:
        """Compute include and exclude inherit parent params and setup it to settings_config."""

        result_exclude = []
        result_include = []
        result_conf_exclude = []
        result_conf_include = []
        result_env_exclude = []
        result_env_include = []
        init_exclude = self.settings_init_params.exclude_inherit_parent
        init_include = self.settings_init_params.include_inherit_parent

        # ######### FILE EXCLUDE #########
        class_conf_exclude = self.class_file_config.conf_exclude_inherit_parent or []
        result_conf_exclude = class_conf_exclude
        parent_conf_exclude = self.parent_file_config.conf_exclude_inherit_parent or []
        init_conf_exclude = self.init_file_config.conf_exclude_inherit_parent
        if self.file_config_inherit_parent:
            aux_exclude = result_conf_exclude
            if init_conf_exclude:
                aux_exclude = init_conf_exclude
            elif init_exclude:
                res_exclude = []
                for ie in init_exclude:
                    if ie in CONF_INCLUDE_EXLUDE_PARAMS:
                        res_exclude.append(ie)
                if res_exclude:
                    aux_exclude = res_exclude
            if conf.CONF_EXCLUDE_INHERIT_PARENT not in aux_exclude and parent_conf_exclude:
                result_conf_exclude = parent_conf_exclude
        if init_conf_exclude is not None:
            result_conf_exclude = init_conf_exclude
        elif init_exclude is not None:
            res_exclude = []
            for ie in init_exclude:
                if ie in CONF_INCLUDE_EXLUDE_PARAMS:
                    res_exclude.append(ie)
            if res_exclude:
                result_conf_exclude = res_exclude
        self.settings_config.conf_exclude_inherit_parent = result_conf_exclude
        if self.file_config_inherit_parent:
            for key in ["conf_include_inherit_parent", "conf_exclude_inherit_parent"]:
                if key not in result_conf_exclude and key not in self.inherited_params:
                    self.inherited_params.append(key)

        # ######### FILE INCLUDE #########
        class_conf_include = self.class_file_config.conf_include_inherit_parent or []
        result_conf_include = class_conf_include
        parent_conf_include = self.parent_file_config.conf_include_inherit_parent or []
        init_conf_include = self.init_file_config.conf_include_inherit_parent
        if self.file_config_inherit_parent:
            if conf.CONF_INCLUDE_INHERIT_PARENT not in result_conf_exclude and parent_conf_include:
                result_conf_include = []
                for pci in parent_conf_include:
                    if pci not in result_conf_exclude:
                        result_conf_include.append(pci)
        if init_conf_include is not None:
            result_conf_include = []
            for ici in init_conf_include:
                if ici not in result_conf_exclude:
                    result_conf_include.append(ici)
        elif init_include is not None:
            res_include = []
            for ii in init_include:
                if ii in CONF_INCLUDE_EXLUDE_PARAMS:
                    res_include.append(ii)
            if res_include:
                result_conf_include = res_include
        aux_res = result_conf_include
        result_conf_include = []
        for rci in aux_res:
            if rci not in result_conf_exclude:
                result_conf_include.append(rci)
        self.settings_config.conf_include_inherit_parent = result_conf_include

        # ######### ENV EXCLUDE #########
        class_env_exclude = self.class_env_config.env_exclude_inherit_parent or []
        result_env_exclude = class_env_exclude
        parent_env_exclude = self.parent_env_config.env_exclude_inherit_parent or []
        init_env_exclude = self.init_env_config.env_exclude_inherit_parent
        if self.env_config_inherit_parent:
            aux_exclude = result_env_exclude
            if init_env_exclude:
                aux_exclude = init_env_exclude
            elif init_exclude:
                res_exclude = []
                for ie in init_exclude:
                    if ie in CONF_INCLUDE_EXLUDE_PARAMS:
                        res_exclude.append(ie)
                if res_exclude:
                    aux_exclude = res_exclude
            if env.ENV_EXCLUDE_INHERIT_PARENT not in aux_exclude and parent_env_exclude:
                result_env_exclude = parent_env_exclude
        if init_env_exclude is not None:
            result_env_exclude = init_env_exclude
        elif init_exclude is not None:
            res_exclude = []
            for ie in init_exclude:
                if ie in ENV_INCLUDE_EXLUDE_PARAMS:
                    res_exclude.append(ie)
            if res_exclude:
                result_env_exclude = res_exclude
        self.settings_config.env_exclude_inherit_parent = result_env_exclude
        if self.env_config_inherit_parent:
            for key in ["env_include_inherit_parent", "env_exclude_inherit_parent"]:
                if key not in result_env_exclude and key not in self.inherited_params:
                    self.inherited_params.append(key)

        # ######### ENV INCLUDE #########
        class_env_include = self.class_env_config.env_include_inherit_parent or []
        result_env_include = class_env_include
        parent_env_include = self.parent_env_config.env_include_inherit_parent or []
        init_env_include = self.init_env_config.env_include_inherit_parent
        if self.env_config_inherit_parent:
            if env.ENV_INCLUDE_INHERIT_PARENT not in result_env_exclude and parent_env_include:
                result_env_include = []
                for pei in parent_env_include:
                    if pei not in result_env_exclude:
                        result_env_include.append(pei)
        if init_env_include is not None:
            result_env_include = []
            for iei in init_env_include:
                if iei not in result_env_exclude:
                    result_env_include.append(iei)
        elif init_include is not None:
            res_include = []
            for ii in init_include:
                if ii in ENV_INCLUDE_EXLUDE_PARAMS:
                    res_include.append(ii)
            if res_include:
                result_env_include = res_include

        aux_res = result_env_include
        result_env_include = []
        for rei in aux_res:
            if rei not in result_env_exclude:
                result_env_include.append(rei)
        self.settings_config.env_include_inherit_parent = result_env_include

        # ######### RESULT EXCLUDE #########
        result_include.extend(result_conf_include)
        result_include.extend(result_env_include)
        result_exclude.extend(result_conf_exclude)
        result_exclude.extend(result_env_exclude)
        self.settings_config.include_inherit_parent = result_include
        self.settings_config.exclude_inherit_parent = result_exclude

        DEBUG_DICT = {
            "COMMON_INIT_CONFIG": {
                "init_exclude": init_exclude,
                "init_include": init_include,
            },
            "FILE_CONFIG": {
                "exclude": {
                    "class_conf_exclude": class_conf_exclude,
                    "parent_conf_exclude": parent_conf_exclude,
                    "init_conf_exclude": init_conf_exclude,
                    "result_conf_exclude": result_conf_exclude,
                },
                "include": {
                    "class_conf_include": class_conf_include,
                    "parent_conf_include": parent_conf_include,
                    "init_conf_include": init_conf_include,
                    "result_conf_include": result_conf_include,
                },
            },
            "ENV_CONFIG": {
                "exclude": {
                    "class_env_exclude": class_env_exclude,
                    "parent_env_exclude": parent_env_exclude,
                    "init_env_exclude": init_env_exclude,
                    "result_env_exclude": result_env_exclude,
                },
                "include": {
                    "class_env_include": class_env_include,
                    "parent_env_include": parent_env_include,
                    "init_env_include": init_env_include,
                    "result_env_include": result_env_include,
                },
            },
            "RESULT_CONFIG": {
                "result_include": result_include,
                "result_exclude": result_exclude,
            },
        }
        if self.arfi_dev_debug:
            # TODO: add debug mode
            import pprint

            pprint.pprint(DEBUG_DICT)

    def extract(self, instance: "ArFiSettings") -> None:
        """Setup config to instance."""

        for field_name in self.model_fields.keys():
            if field_name in self._class_vars:
                continue
            instance_field_name = f"_{field_name}"
            setattr(instance, instance_field_name, getattr(self, field_name))


class ConfigStorage:
    storage: dict[int, InstanceConfig] = dict()

    def get_config(self, instance: "ArFiSettings") -> InstanceConfig:
        """Create or return config for instance."""

        assert is_settings(type(instance)), f"type(instance) must be a subclass ArFiSettings, got {type(instance)}"
        instance_id = id(instance)
        instance_config = self.storage.get(instance_id, PydanticUndefined)
        if instance_config is PydanticUndefined:
            instance_config = InstanceConfig()
            self.storage[instance_id] = instance_config
        return instance_config


config_storage = ConfigStorage()
