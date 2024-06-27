from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .constants import (
    CONFIG_EXT_DEFAULT,
    ORDERED_SETTINGS,
)
from .entity import (
    EnvConfigEntity as env,
    FileConfigEntity as conf,
)
from .types import (
    DEFAULT_PATH_SENTINEL,
    LIST_STR_SENTINEL,
    STR_SENTINEL,
    EnvConfigDict,
    FileConfigDict,
    MultiPathType,
    PathType,
    SettingsConfigDict,
    SettingsParamsDict,
)

__all__ = [
    "EnvConfigSchema",
    "FileConfigSchema",
    "SettingsConfigSchema",
    "SettingsParamsSchema",
    "PyProjectSchema",
    "CONF_INCLUDE_EXLUDE_PARAMS",
    "ENV_INCLUDE_EXLUDE_PARAMS",
    "INCLUDE_EXLUDE_PARAMS",
]

CONF_INCLUDE_EXLUDE_PARAMS = [
    "conf_file",
    "conf_dir",
    "conf_ext",
    "conf_file_encoding",
    "conf_case_sensitive",
    "conf_ignore_missing",
    "conf_custom_ext_handler",
    "conf_include_inherit_parent",
    "conf_exclude_inherit_parent",
]
ENV_INCLUDE_EXLUDE_PARAMS = [
    "env_file",
    "env_prefix",
    "env_prefix_as_mode_dir",
    "env_prefix_as_nested_mode_dir",
    "env_prefix_as_source_mode_dir",
    "env_file_encoding",
    "env_case_sensitive",
    "env_nested_delimiter",
    "env_ignore_missing",
    "env_include_inherit_parent",
    "env_exclude_inherit_parent",
]
INCLUDE_EXLUDE_PARAMS = []
INCLUDE_EXLUDE_PARAMS.extend(CONF_INCLUDE_EXLUDE_PARAMS)
INCLUDE_EXLUDE_PARAMS.extend(ENV_INCLUDE_EXLUDE_PARAMS)


class PyProjectSchema(BaseModel):
    """Default settings for each instance of the class ArFiSettings."""

    # arfi settings
    mode_dir_inherit_nested: bool | None = True
    mode_dir_inherit_parent: bool | None = True
    file_config_inherit_parent: bool | None = True
    env_config_inherit_parent: bool | None = True
    handler: str = "default_main_handler"
    handler_inherit_parent: bool = True
    ordered_settings: list[str] = ORDERED_SETTINGS
    ordered_settings_inherit_parent: bool = True

    # File settings
    conf_file: MultiPathType | None = conf.DEFAULT
    conf_dir: str | list[str] | None = conf.DEFAULT
    conf_ext: str | list[str] = CONFIG_EXT_DEFAULT
    conf_file_encoding: str | None = None
    conf_case_sensitive: bool | None = None
    conf_ignore_missing: bool | None = None
    conf_custom_ext_handler: str | dict[str, str] | None = None
    conf_include_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS]] = []
    conf_exclude_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS]] = []

    # Environment settings
    env_file: str | list[str] | None = ".env"
    env_prefix: str = ""
    env_prefix_as_mode_dir: bool = False
    env_prefix_as_nested_mode_dir: bool = False
    env_prefix_as_source_mode_dir: bool = False
    env_file_encoding: str | None = None
    env_case_sensitive: bool | None = None
    env_ignore_missing: bool | None = None
    env_nested_delimiter: str = ""
    env_include_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS]] = []
    env_exclude_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS]] = []

    # Global settings
    case_sensitive: bool = False
    ignore_missing: bool = True
    encoding: str | None = None
    cli: bool = False
    secrets_dir: str | None = None
    include_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS]] = []
    exclude_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS]] = []

    arfi_debug: bool = False

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=False,
        validate_return=False,
    )


class UpdateMixin:
    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)


class FileConfigSchema(BaseModel, UpdateMixin):
    """Validation schema for configuring file settings."""

    conf_file: MultiPathType | None = DEFAULT_PATH_SENTINEL
    conf_dir: MultiPathType | None = DEFAULT_PATH_SENTINEL
    conf_ext: str | list[str] = []
    conf_file_encoding: str | None = STR_SENTINEL
    conf_case_sensitive: bool | None = None
    conf_ignore_missing: bool | None = None
    conf_custom_ext_handler: str | dict[str, str] | None = STR_SENTINEL
    conf_include_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS]] | None = None
    conf_exclude_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS]] | None = None

    @field_validator("conf_ext")
    @classmethod
    def str_conf_ext(cls, v: str | list[str]) -> str | list[str]:
        """Ensure that the conf_ext is a string or list of strings."""
        if isinstance(v, str):
            v = [ext.strip() for ext in v.split(",")] or LIST_STR_SENTINEL
        return v

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=False,
        validate_return=False,
    )

    @property
    def conf_dict(self) -> FileConfigDict:
        """Return a dictionary representation of the model."""
        return FileConfigDict(
            conf_file=self.conf_file if self.conf_file is not DEFAULT_PATH_SENTINEL else str(conf.DEFAULT),
            conf_dir=self.conf_dir if self.conf_dir is not DEFAULT_PATH_SENTINEL else str(conf.DEFAULT),
            conf_ext=self.conf_ext if self.conf_ext != [] else CONFIG_EXT_DEFAULT,
            conf_file_encoding=self.conf_file_encoding if self.conf_file_encoding is not STR_SENTINEL else None,
            conf_case_sensitive=self.conf_case_sensitive if self.conf_case_sensitive is not None else False,
            conf_ignore_missing=self.conf_ignore_missing if self.conf_ignore_missing is not None else True,
            conf_custom_ext_handler=(
                self.conf_custom_ext_handler if self.conf_custom_ext_handler is not STR_SENTINEL else None
            ),
            conf_include_inherit_parent=(
                self.conf_include_inherit_parent if self.conf_include_inherit_parent is not None else []
            ),
            conf_exclude_inherit_parent=(
                self.conf_exclude_inherit_parent if self.conf_exclude_inherit_parent is not None else []
            ),
        )


assert set(CONF_INCLUDE_EXLUDE_PARAMS) == set(FileConfigSchema.model_fields.keys())


class EnvConfigSchema(BaseModel, UpdateMixin):
    """Validation schema for configuring environment settings."""

    env_file: MultiPathType | None = DEFAULT_PATH_SENTINEL
    env_prefix: str | None = None
    env_prefix_as_mode_dir: bool | None = None
    env_prefix_as_nested_mode_dir: bool | None = None
    env_prefix_as_source_mode_dir: bool | None = None
    env_file_encoding: str | None = STR_SENTINEL
    env_case_sensitive: bool | None = None
    env_nested_delimiter: str | None = None
    env_ignore_missing: bool | None = None
    env_include_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS]] | None = None
    env_exclude_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS]] | None = None

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=False,
        validate_return=False,
    )

    @property
    def env_dict(self) -> dict:
        """Return a dictionary representation of the model."""
        return EnvConfigDict(
            env_file=self.env_file if self.env_file is not DEFAULT_PATH_SENTINEL else env.DEFAULT_ENV_FILE,
            env_prefix=self.env_prefix if self.env_prefix is not None else "",
            env_prefix_as_mode_dir=self.env_prefix_as_mode_dir if self.env_prefix_as_mode_dir is not None else False,
            env_prefix_as_nested_mode_dir=(
                self.env_prefix_as_nested_mode_dir if self.env_prefix_as_nested_mode_dir is not None else False
            ),
            env_prefix_as_source_mode_dir=(
                self.env_prefix_as_source_mode_dir if self.env_prefix_as_source_mode_dir is not None else False
            ),
            env_file_encoding=self.env_file_encoding if self.env_file_encoding is not STR_SENTINEL else None,
            env_case_sensitive=self.env_case_sensitive if self.env_case_sensitive is not None else False,
            env_nested_delimiter=self.env_nested_delimiter if self.env_nested_delimiter is not None else "",
            env_ignore_missing=self.env_ignore_missing if self.env_ignore_missing is not None else True,
            env_include_inherit_parent=(
                self.env_include_inherit_parent if self.env_include_inherit_parent is not None else []
            ),
            env_exclude_inherit_parent=(
                self.env_exclude_inherit_parent if self.env_exclude_inherit_parent is not None else []
            ),
        )


assert set(ENV_INCLUDE_EXLUDE_PARAMS) == set(EnvConfigSchema.model_fields.keys())


class SettingsConfigSchema(FileConfigSchema, EnvConfigSchema):
    """Validation schema for configuring model settings."""

    case_sensitive: bool | None = None
    ignore_missing: bool | None = None
    encoding: str | None = STR_SENTINEL
    cli: bool | None = None
    secrets_dir: PathType | None = DEFAULT_PATH_SENTINEL
    conf_path: list[Path] = []
    env_path: list[Path] = []
    include_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS]] | None = None
    exclude_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS]] | None = None

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=False,
        validate_return=False,
    )

    @property
    def config_model_dict(self) -> SettingsConfigDict:
        """Return a dictionary representation of the model."""
        settings_dict = SettingsConfigDict(
            case_sensitive=self.case_sensitive if self.case_sensitive is not None else False,
            ignore_missing=self.ignore_missing if self.ignore_missing is not None else True,
            encoding=self.encoding if self.encoding is not STR_SENTINEL else None,
            cli=self.cli if self.cli is not None else False,
            secrets_dir=self.secrets_dir if self.secrets_dir is not DEFAULT_PATH_SENTINEL else None,
            # secrets_dir=self.secrets_dir if self.secrets_dir != DEFAULT_PATH_SENTINEL else None,
            include_inherit_parent=self.include_inherit_parent if self.include_inherit_parent is not None else [],
            exclude_inherit_parent=self.exclude_inherit_parent if self.exclude_inherit_parent is not None else [],
        )
        settings_dict.update(self.conf_dict)
        settings_dict.update(self.env_dict)
        settings_dict.update(dict(conf_path=self.conf_path, env_path=self.env_path))
        return settings_dict


class SettingsParamsSchema(BaseModel):
    """Validation schema for init params."""

    # only params
    read_config: bool | None = Field(None, alias="_read_config")
    read_config_force: bool | None = Field(None, alias="_read_config_force")
    mode_dir: PathType | None = Field(DEFAULT_PATH_SENTINEL, alias="_mode_dir")
    mode_dir_inherit_nested: bool | None = Field(None, alias="_mode_dir_inherit_nested")
    mode_dir_inherit_parent: bool | None = Field(None, alias="_mode_dir_inherit_parent")
    file_config_inherit_parent: bool | None = Field(None, alias="_file_config_inherit_parent")
    env_config_inherit_parent: bool | None = Field(None, alias="_env_config_inherit_parent")

    # pyproject.toml params
    conf_file: MultiPathType | None = Field(DEFAULT_PATH_SENTINEL, alias="_conf_file")
    conf_dir: MultiPathType | None = Field(DEFAULT_PATH_SENTINEL, alias="_conf_dir")
    conf_ext: str | list[str] = Field([], alias="_conf_ext")
    conf_file_encoding: str | None = Field(STR_SENTINEL, alias="_conf_file_encoding")
    conf_case_sensitive: bool | None = Field(None, alias="_conf_case_sensitive")
    conf_ignore_missing: bool | None = Field(None, alias="_conf_ignore_missing")
    conf_custom_ext_handler: str | dict[str, str] | None = Field(STR_SENTINEL, alias="_conf_custom_ext_handler")
    conf_include_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS]] | None = Field(
        None, alias="_conf_include_inherit_parent"
    )
    conf_exclude_inherit_parent: list[Literal[*CONF_INCLUDE_EXLUDE_PARAMS]] | None = Field(
        None, alias="_conf_exclude_inherit_parent"
    )
    env_file: MultiPathType | None = Field(DEFAULT_PATH_SENTINEL, alias="_env_file")
    env_prefix: str | None = Field(None, alias="_env_prefix")
    env_prefix_as_mode_dir: bool | None = Field(None, alias="_env_prefix_as_mode_dir")
    env_prefix_as_nested_mode_dir: bool | None = Field(None, alias="_env_prefix_as_nested_mode_dir")
    env_prefix_as_source_mode_dir: bool | None = Field(None, alias="_env_prefix_as_source_mode_dir")
    env_file_encoding: str | None = Field(STR_SENTINEL, alias="_env_file_encoding")
    env_case_sensitive: bool | None = Field(None, alias="_env_case_sensitive")
    env_nested_delimiter: str | None = Field(None, alias="_env_nested_delimiter")
    env_ignore_missing: bool | None = Field(None, alias="_env_ignore_missing")
    env_include_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS]] | None = Field(
        None, alias="_env_include_inherit_parent"
    )
    env_exclude_inherit_parent: list[Literal[*ENV_INCLUDE_EXLUDE_PARAMS]] | None = Field(
        None, alias="_env_exclude_inherit_parent"
    )
    case_sensitive: bool | None = Field(None, alias="_case_sensitive")
    ignore_missing: bool | None = Field(None, alias="_ignore_missing")
    encoding: str | None = Field(STR_SENTINEL, alias="_encoding")
    cli: bool | None = Field(None, alias="_cli")
    secrets_dir: PathType | None = Field(DEFAULT_PATH_SENTINEL, alias="_secrets_dir")
    include_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS]] | None = Field(None, alias="_include_inherit_parent")
    exclude_inherit_parent: list[Literal[*INCLUDE_EXLUDE_PARAMS]] | None = Field(None, alias="_exclude_inherit_parent")
    handler: str = Field(STR_SENTINEL, alias="_handler")
    handler_inherit_parent: bool | None = Field(None, alias="_handler_inherit_parent")
    ordered_settings: list[str] = Field(LIST_STR_SENTINEL, alias="_ordered_settings")
    ordered_settings_inherit_parent: bool | None = Field(None, alias="_ordered_settings_inherit_parent")

    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        validate_default=False,
        validate_return=False,
    )

    @field_validator("conf_ext")
    @classmethod
    def str_conf_ext(cls, v: str | list[str] | None) -> str | list[str] | None:
        """Ensure that the conf_ext is a string or list of strings."""
        if isinstance(v, str):
            v = [ext.strip() for ext in v.split(",")] or LIST_STR_SENTINEL
        return v

    def get_param_dict(self, exclude_defaults=False) -> dict[str, Any]:
        params = self.model_dump(by_alias=True, exclude_defaults=exclude_defaults)
        return params

    @property
    def default_param_dict(self) -> SettingsParamsDict:
        return SettingsParamsDict(
            read_config=self.read_config if self.read_config is not None else True,
            read_config_force=self.read_config_force if self.read_config_force is not None else False,
            mode_dir=self.mode_dir,
            mode_dir_inherit_nested=self.mode_dir_inherit_nested if self.mode_dir_inherit_nested is not None else True,
            mode_dir_inherit_parent=self.mode_dir_inherit_parent if self.mode_dir_inherit_parent is not None else True,
            file_config_inherit_parent=(
                self.file_config_inherit_parent if self.file_config_inherit_parent is not None else True
            ),
            env_config_inherit_parent=(
                self.env_config_inherit_parent if self.env_config_inherit_parent is not None else True
            ),
            # file_config
            conf_file=self.conf_file if self.conf_file is not DEFAULT_PATH_SENTINEL else conf.DEFAULT,
            conf_dir=self.conf_dir if self.conf_dir is not DEFAULT_PATH_SENTINEL else conf.DEFAULT,
            conf_ext=self.conf_ext if self.conf_ext != [] else CONFIG_EXT_DEFAULT,
            conf_file_encoding=self.conf_file_encoding if self.conf_file_encoding is not STR_SENTINEL else None,
            conf_case_sensitive=self.conf_case_sensitive if self.conf_case_sensitive is not None else False,
            conf_ignore_missing=self.conf_ignore_missing if self.conf_ignore_missing is not None else True,
            conf_custom_ext_handler=(
                self.conf_custom_ext_handler if self.conf_custom_ext_handler is not STR_SENTINEL else None
            ),
            conf_include_inherit_parent=(
                self.conf_include_inherit_parent if self.conf_include_inherit_parent is not None else []
            ),
            conf_exclude_inherit_parent=(
                self.conf_exclude_inherit_parent if self.conf_exclude_inherit_parent is not None else []
            ),
            # env_config
            env_file=self.env_file if self.env_file is not DEFAULT_PATH_SENTINEL else env.DEFAULT_ENV_FILE,
            env_prefix=self.env_prefix if self.env_prefix is not None else "",
            env_prefix_as_mode_dir=self.env_prefix_as_mode_dir if self.env_prefix_as_mode_dir is not None else False,
            env_prefix_as_nested_mode_dir=(
                self.env_prefix_as_nested_mode_dir if self.env_prefix_as_nested_mode_dir is not None else False
            ),
            env_prefix_as_source_mode_dir=(
                self.env_prefix_as_source_mode_dir if self.env_prefix_as_source_mode_dir is not None else False
            ),
            env_file_encoding=self.env_file_encoding if self.env_file_encoding is not STR_SENTINEL else None,
            env_case_sensitive=self.env_case_sensitive if self.env_case_sensitive is not None else False,
            env_nested_delimiter=self.env_nested_delimiter if self.env_nested_delimiter is not None else "",
            env_ignore_missing=self.env_ignore_missing if self.env_ignore_missing is not None else True,
            env_include_inherit_parent=(
                self.env_include_inherit_parent if self.env_include_inherit_parent is not None else []
            ),
            env_exclude_inherit_parent=(
                self.env_exclude_inherit_parent if self.env_exclude_inherit_parent is not None else []
            ),
            # model_config
            case_sensitive=self.case_sensitive if self.case_sensitive is not None else False,
            ignore_missing=self.ignore_missing if self.ignore_missing is not None else True,
            encoding=self.encoding if self.encoding is not STR_SENTINEL else None,
            cli=self.cli if self.cli is not None else False,
            secrets_dir=self.secrets_dir if self.secrets_dir is not DEFAULT_PATH_SENTINEL else None,
            include_inherit_parent=self.include_inherit_parent if self.include_inherit_parent is not None else [],
            exclude_inherit_parent=self.exclude_inherit_parent if self.exclude_inherit_parent is not None else [],
            # handler settings
            handler=self.handler if self.handler is not STR_SENTINEL else "",
            handler_inherit_parent=self.handler_inherit_parent if self.handler_inherit_parent is not None else True,
            ordered_settings=self.ordered_settings if self.ordered_settings != LIST_STR_SENTINEL else ORDERED_SETTINGS,
            ordered_settings_inherit_parent=(
                self.ordered_settings_inherit_parent if self.ordered_settings_inherit_parent is not None else True
            ),
        )

    def update_exclude_default(self, **new_data):
        update_data = self.model_dump(by_alias=True)
        update_data.update(new_data)
        for key, value in self.model_validate(update_data).model_dump(exclude_defaults=True).items():
            setattr(self, key, value)
        return self
