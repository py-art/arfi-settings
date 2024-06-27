from enum import StrEnum


class FileConfigEntity(StrEnum):
    """Entity type of a file config settings."""

    DEFAULT = "config"
    FILE = "conf_file"
    DIR = "conf_dir"
    EXT = "conf_ext"
    FILE_ENCODING = "conf_file_encoding"
    CASE_SENSITIVE = "conf_case_sensitive"
    IGNORE_MISSING = "conf_ignore_missing"
    CUSTOM_EXT_HANDLER = "conf_custom_ext_handler"
    CONF_INCLUDE_INHERIT_PARENT = "conf_include_inherit_parent"
    CONF_EXCLUDE_INHERIT_PARENT = "conf_exclude_inherit_parent"


class EnvConfigEntity(StrEnum):
    """Entity type of an env config settings."""

    FILE = "env_file"
    PREFIX = "env_prefix"
    PREFIX_AS_MODE_DIR = "env_prefix_as_mode_dir"
    PREFIX_AS_NESTED_MODE_DIR = "env_prefix_as_nested_mode_dir"
    PREFIX_AS_SOURCE_MODE_DIR = "env_prefix_as_source_mode_dir"
    FILE_ENCODING = "env_file_encoding"
    CASE_SENSITIVE = "env_case_sensitive"
    NESTED_DELIMITER = "env_nested_delimiter"
    DEFAULT_ENV_FILE = ".env"
    IGNORE_MISSING = "env_ignore_missing"
    ENV_INCLUDE_INHERIT_PARENT = "env_include_inherit_parent"
    ENV_EXCLUDE_INHERIT_PARENT = "env_exclude_inherit_parent"


class ModelConfigEntity(StrEnum):
    """Entity type of a model config settings."""

    CASE_SENSITIVE = "case_sensitive"
    IGNORE_MISSING = "ignore_missing"
    ENCODING = "encoding"
    CLI = "cli"
    SECRETS_DIR = "secrets_dir"
    INCLUDE_INHERIT_PARENT = "include_inherit_parent"
    EXCLUDE_INHERIT_PARENT = "exclude_inherit_parent"
