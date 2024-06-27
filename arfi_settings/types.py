from pathlib import Path
from typing import List, Tuple, Union

from pydantic import ConfigDict
from pydantic._internal._config import config_keys
from typing_extensions import TypedDict

MultiPathType = Union[Path, str, List[Union[Path, str]], Tuple[Union[Path, str], ...]]
PathType = Union[Path, str]
DEFAULT_PATH_SENTINEL: PathType = Path("")
STR_SENTINEL: str = ""
SENTINEL = object()
LIST_STR_SENTINEL: list[str] = [""]


class PyProjectConfigDict(TypedDict, total=False):
    """Configuration settings for pyproject.toml."""

    mode_dir_inherit_nested: bool
    mode_dir_inherit_parent: bool
    file_config_inherit_parent: bool
    env_config_inherit_parent: bool

    conf_file: MultiPathType | None
    conf_dir: str | list[str] | None
    conf_ext: str | list[str]
    conf_file_encoding: str | None
    conf_case_sensitive: bool
    conf_ignore_missing: bool
    conf_custom_ext_handler: str | dict[str, str] | None
    conf_include_inherit_parent: list[str]
    conf_exclude_inherit_parent: list[str]

    env_file: str | list[str] | None
    env_prefix: str
    env_prefix_as_mode_dir: bool
    env_prefix_as_nested_mode_dir: bool
    env_prefix_as_source_mode_dir: bool
    env_file_encoding: str | None
    env_case_sensitive: bool
    env_nested_delimiter: str
    env_ignore_missing: bool
    env_include_inherit_parent: list[str]
    env_exclude_inherit_parent: list[str]

    case_sensitive: bool
    ignore_missing: bool
    encoding: str | None
    cli: bool
    secrets_dir: str | None

    handler: str
    handler_inherit_parent: bool
    ordered_settings: list[str]
    ordered_settings_inherit_parent: bool

    include_inherit_parent: list[str]
    exclude_inherit_parent: list[str]

    arfi_debug: bool


class FileConfigDict(TypedDict, total=False):
    """A TypedDict for configuring file settings."""

    conf_file: MultiPathType | None
    conf_dir: MultiPathType | None
    conf_ext: str | list[str]
    conf_file_encoding: str | None
    conf_case_sensitive: bool | None
    conf_ignore_missing: bool | None
    conf_custom_ext_handler: str | dict[str, str] | None
    conf_include_inherit_parent: list[str] | None
    conf_exclude_inherit_parent: list[str] | None


class EnvConfigDict(TypedDict, total=False):
    """A TypedDict for configuring environment settings."""

    env_file: MultiPathType | None
    env_prefix: str | None
    env_prefix_as_mode_dir: bool | None
    env_prefix_as_nested_mode_dir: bool | None
    env_prefix_as_source_mode_dir: bool | None
    env_file_encoding: str | None
    env_case_sensitive: bool | None
    env_nested_delimiter: str | None
    env_ignore_missing: bool | None
    env_include_inherit_parent: list[str] | None
    env_exclude_inherit_parent: list[str] | None


class GlobalConfigDict(TypedDict, total=False):
    """A TypedDict for configuring settings."""

    case_sensitive: bool
    ignore_missing: bool
    encoding: str | None
    cli: bool
    secrets_dir: PathType | None
    include_inherit_parent: list[str] | None
    exclude_inherit_parent: list[str] | None


class SettingsConfigDict(ConfigDict, FileConfigDict, EnvConfigDict, GlobalConfigDict, total=False):
    """A TypedDict for configuring settings."""


config_keys |= set(SettingsConfigDict.__annotations__.keys())


class SettingsParamsDict(TypedDict, total=False):
    """A TypedDict for configuring parameters settings."""

    read_config: bool
    read_config_force: bool
    mode_dir: PathType | None
    mode_dir_inherit_nested: bool
    mode_dir_inherit_parent: bool
    file_config_inherit_parent: bool
    env_config_inherit_parent: bool

    conf_file: MultiPathType | None
    conf_dir: MultiPathType | None
    conf_ext: str | list[str] | None
    conf_file_encoding: str | None
    conf_case_sensitive: bool
    conf_ignore_missing: bool
    conf_custom_ext_handler: str | dict[str, str] | None
    conf_include_inherit_parent: list[str]
    conf_exclude_inherit_parent: list[str]

    env_file: MultiPathType | None
    env_prefix: str
    env_prefix_as_mode_dir: bool
    env_prefix_as_nested_mode_dir: bool
    env_prefix_as_source_mode_dir: bool
    env_file_encoding: str | None
    env_case_sensitive: bool
    env_nested_delimiter: str
    env_ignore_missing: bool
    env_include_inherit_parent: list[str]
    env_exclude_inherit_parent: list[str]

    case_sensitive: bool
    ignore_missing: bool
    encoding: str | None
    cli: bool
    secrets_dir: PathType | None

    handler: str
    handler_inherit_parent: bool
    ordered_settings: list[str]
    ordered_settings_inherit_parent: bool
    include_inherit_parent: list[str]
    exclude_inherit_parent: list[str]
