import inspect
from pathlib import Path
from typing import Any, ClassVar, Literal

from pydantic import AliasChoices, BaseModel, Field

from .arfi_debug import debug
from .constants import (
    PYPROJECT_TOML_MAX_DEPTH,
)
from .descriptors import (
    BaseDirDescriptor,
    EnvConfigInheritParentDescriptor,
    FileConfigInheritParentDescriptor,
    HandlerDescriptor,
    HandlerInheritParentDescriptor,
    ModeDirDescriptor,
    ModeDirInheritNestedDescriptor,
    ModeDirInheritParentDescriptor,
    OrderedSettingsDescriptor,
    OrderedSettingsInheritParentDescriptor,
    ReadConfigDeskriptor,
    ReadConfigForceDeskriptor,
    ReadPyProjectTomlDeskriptor,
)
from .handlers import ArFiHandler
from .init_config import init_settings
from .schemes import (
    CONF_INCLUDE_EXLUDE_PARAMS,
    ENV_INCLUDE_EXLUDE_PARAMS,
    INCLUDE_EXLUDE_PARAMS,
    SettingsConfigSchema,
)
from .storage import config_storage
from .types import (
    DEFAULT_PATH_SENTINEL,
    LIST_STR_SENTINEL,
    SENTINEL,
    STR_SENTINEL,
    EnvConfigDict,
    FileConfigDict,
    MultiPathType,
    PathType,
    SettingsConfigDict,
)


class ArFiSettings(BaseModel):
    """Advanced pydantic settings."""

    MODE: str | None = Field(None, validation_alias=AliasChoices("MODE", "mode"))
    BASE_DIR: ClassVar[PathType | None] = None
    read_config: ClassVar[bool] = True
    read_config_force: ClassVar[bool] = None
    read_pyproject_toml: ClassVar[bool] = True
    mode_dir: ClassVar[PathType | None] = DEFAULT_PATH_SENTINEL
    mode_dir_inherit_nested: ClassVar[bool] = SENTINEL
    mode_dir_inherit_parent: ClassVar[bool] = SENTINEL
    file_config_inherit_parent: ClassVar[bool] = SENTINEL
    env_config_inherit_parent: ClassVar[bool] = SENTINEL
    file_config: ClassVar[FileConfigDict] = FileConfigDict()
    env_config: ClassVar[EnvConfigDict] = EnvConfigDict()
    handler_class: ClassVar[ArFiHandler] = ArFiHandler
    handler: ClassVar[str] = SENTINEL
    handler_inherit_parent: ClassVar[bool] = SENTINEL
    ordered_settings: ClassVar[list[str]] = SENTINEL
    ordered_settings_inherit_parent: ClassVar[bool] = SENTINEL

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        validate_default=True,
    )

    __slots__ = (
        "_read_config",
        "_read_config_force",
        "_read_pyproject_toml",
        "_init_file_config",
        "_init_env_config",
        "_settings_init_params",
        "_mode_dir",
        "_mode_dir_inherit_nested",
        "_mode_dir_inherit_parent",
        "_file_config_inherit_parent",
        "_env_config_inherit_parent",
        "_handler_inherit_parent",
        "_ordered_settings",
        "_ordered_settings_inherit_parent",
        "_values_by_default",
        "_handler_tree",
        "_handler_parent_mode_dir",
        "_mode_dir_attr",
        "_parent_mode_dir",
        "_parent_file_config",
        "_parent_env_config",
        "_handler",
        "_conf_path",
        "_env_path",
        "_computed_file_config",
        "_computed_env_config",
        "_settings_config",
        "_computed_mode_dir",
        "_mode_dir_path",
        "_nested_mode_dir",
        "_source_mode_dir",
        "_inherited_params",
        "_modified_class_vars",
        "_pyproject_toml_path",
        "_search_base_dir",
        "_base_dir",
        "_root_dir",
        "_arfi_debug",
    )

    __instances: ClassVar[dict] = dict()

    @property
    def settings_config(self) -> SettingsConfigSchema:
        if not hasattr(self, "_settings_config"):
            return None
        return self._settings_config

    @property
    def inherited_params(self) -> list[str]:
        if not hasattr(self, "_inherited_params"):
            return []
        return self._inherited_params

    # @computed_field
    @property
    def conf_path(self) -> list[Path]:
        """Full config path from file and dir settings."""
        if not hasattr(self, "_conf_path"):
            return []
        return self._conf_path

    # @computed_field
    @property
    def env_path(self) -> list[Path]:
        """Full env path from file and dir settings."""
        if not hasattr(self, "_env_path"):
            return []
        return self._env_path

    @property
    def mode_dir_path(self) -> PathType:
        """Generate path to mode directory."""
        if not hasattr(self, "_mode_dir_path"):
            return DEFAULT_PATH_SENTINEL
        return self._mode_dir_path

    @property
    def computed_mode_dir(self) -> str:
        if not hasattr(self, "_computed_mode_dir"):
            return STR_SENTINEL
        return self._computed_mode_dir

    @property
    def source_mode_dir(self) -> str:
        if not hasattr(self, "_source_mode_dir"):
            return STR_SENTINEL
        return self._source_mode_dir

    @property
    def nested_mode_dir(self) -> PathType | None:
        if not hasattr(self, "_nested_mode_dir"):
            return DEFAULT_PATH_SENTINEL
        return self._nested_mode_dir

    @property
    def parent_mode_dir(self) -> PathType | None:
        if not hasattr(self, "_parent_mode_dir"):
            return DEFAULT_PATH_SENTINEL
        return self._parent_mode_dir

    @property
    def computed_file_config(self) -> FileConfigDict:
        """Compute file_config."""
        if not hasattr(self, "_computed_file_config"):
            return FileConfigDict()
        return self._computed_file_config

    @property
    def computed_env_config(self) -> EnvConfigDict:
        """Compute env_config."""
        if not hasattr(self, "_computed_env_config"):
            return EnvConfigDict()
        return self._computed_env_config

    @property
    def pyproject_toml_path(self) -> PathType | None:
        """The path to pyproject.toml, defined during instance initialization."""
        if not hasattr(self, "_pyproject_toml_path"):
            return None
        return self._pyproject_toml_path

    @property
    def root_dir(self) -> PathType | None:
        return self._root_dir

    def __set_name__(self, owner, name):
        self._mode_dir_attr = name

    def __setattr__(self, attr, value):
        if attr in self.__slots__:
            object.__setattr__(self, attr, value)
        else:
            super().__setattr__(attr, value)

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._mode_dir_attr = None
        cls._modified_class_vars: set[str] = set()
        cls._search_base_dir = True
        cls._root_dir = None
        cls._base_dir = None
        cls._arfi_debug = False
        cls._setup_subclasses_descriptors()

    @classmethod
    def _setup_subclasses_descriptors(cls):
        """Validate and set class variables as descriptors"""

        # setup settings from users class, from pyproject.toml or by default
        for cls_var in init_settings.init_params.model_fields:
            if cls_var not in cls.__class_vars__:
                continue
            privat_name = f"_{cls_var}"
            value = getattr(cls, cls_var)
            if value is SENTINEL:
                value = getattr(init_settings.init_params, cls_var)
                setattr(cls, privat_name, value)
            else:
                cls._modified_class_vars.add(cls_var)
                setattr(cls, privat_name, value)
        cls._base_dir = cls.BASE_DIR
        if cls._base_dir is not None:
            cls._base_dir = Path(cls._base_dir).expanduser().resolve()
            cls._search_base_dir = False
        cls.BASE_DIR = BaseDirDescriptor(cls._base_dir)
        cls._read_config = cls.read_config
        cls.read_config = ReadConfigDeskriptor(cls._read_config)
        cls._read_config_force = cls.read_config_force
        cls.read_config_force = ReadConfigForceDeskriptor(cls._read_config_force)
        cls._read_pyproject_toml = cls.read_pyproject_toml
        cls.read_pyproject_toml = ReadPyProjectTomlDeskriptor(cls._read_pyproject_toml)
        cls._mode_dir = cls.mode_dir
        cls.mode_dir = ModeDirDescriptor(cls._mode_dir)
        cls.mode_dir_inherit_parent = ModeDirInheritParentDescriptor(cls._mode_dir_inherit_parent)
        cls.mode_dir_inherit_nested = ModeDirInheritNestedDescriptor(cls._mode_dir_inherit_nested)
        cls.file_config_inherit_parent = FileConfigInheritParentDescriptor(cls._file_config_inherit_parent)
        cls.env_config_inherit_parent = EnvConfigInheritParentDescriptor(cls._env_config_inherit_parent)
        cls.handler = HandlerDescriptor(cls._handler)
        cls.handler_inherit_parent = HandlerInheritParentDescriptor(cls._handler_inherit_parent)
        cls.ordered_settings = OrderedSettingsDescriptor(cls._ordered_settings)
        cls.ordered_settings_inherit_parent = OrderedSettingsInheritParentDescriptor(
            cls._ordered_settings_inherit_parent
        )

    def __new__(cls, _instance_id: int = None, **kwargs):
        """Create new instance or return existing."""

        curren_frame = inspect.currentframe()
        parrent_frame = curren_frame.f_back
        frame_scope = parrent_frame.f_locals
        co_name = parrent_frame.f_code.co_name

        given_instance = cls.__instances.get(_instance_id)
        if given_instance and not issubclass(type(given_instance), cls):
            given_instance = None

        if given_instance:
            instance = given_instance
            instance._read_config = True
        else:
            instance = super().__new__(cls)
            if "__qualname__" in frame_scope:
                instance._read_config = False
                instance._read_pyproject_toml = False
            if co_name not in ("__init__", "__deepcopy__"):
                cls.__instances[id(instance)] = instance

            if co_name == "__deepcopy__":
                instance._read_config = False
                instance._read_config_force = False
                instance._read_pyproject_toml = False

        return instance

    def _convert_debug_path(self, list_path: list[Path], mode: Literal["conf", "env"]) -> list[str]:
        result = []
        base_dir = self.BASE_DIR
        root_dir = self.root_dir
        if self.BASE_DIR is not None:
            base_dir = Path(self.BASE_DIR).resolve()
        if self.root_dir is not None:
            root_dir = Path(self.root_dir).resolve()
        for path in list_path:
            if mode == "conf":
                if base_dir is not None:
                    path = base_dir / path
            elif mode == "env":
                if root_dir is not None:
                    if Path(root_dir / path).is_file():
                        path = root_dir / path
                    else:
                        if base_dir is not None:
                            path = base_dir / path
                else:
                    if base_dir is not None:
                        path = base_dir / path
            result.append(path.resolve().as_posix())
        return result

    @staticmethod
    def _clear_value_from_handler_params(value: dict[str, Any]) -> dict[str, Any]:
        """Remove handler auxiliary params from value."""

        extra_fields = [
            "_instance_id",
            "_init_value",
            "_handler_value",
            "_handler_tree",
            "_handler_parent_mode_dir",
            "_handler_mode_dir_attr",
            "_handler_ordered_settings",
            "_handler_read_pyproject_toml_force",
            "_handler_search_base_dir",
        ]
        for field in extra_fields:
            if field in value:
                value.pop(field)
        return value

    def __init__(
        self,
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
        _arfi_debug: bool = False,
        **values: Any,
    ):
        _kwargs: dict = locals()
        _kwargs.pop("self")
        config = config_storage.get_config(self)
        values = config.load(instance=self, **_kwargs)
        config.extract(self)

        debug(self, "__init__", arfi_debug=_arfi_debug, mode="before", values=values)

        if self.read_config:
            handler = self.handler_class(
                settings_class=self,
                init_kwargs=values,
                handler=self.handler,
            )
            values = handler()
        values = self._clear_value_from_handler_params(values)

        debug(self, "__init__", values=values, mode="after")

        super().__init__(**values)
        config.extract(self)
