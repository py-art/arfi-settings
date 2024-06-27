CONFIG_EXT_DEFAULT: list[str] = [
    "toml",
    "yaml",
    "yml",
    "json",
]
ORDERED_SETTINGS = [
    "cli",
    "init_kwargs",
    "env",
    "env_file",
    "secrets",
    "conf_file",
]
ARFI_DEBUG_FILE = "config/arfi_debug.toml"
ARFI_DEV_DEBUG_FILE = "config/arfi_dev_debug.toml"
PYPROJECT_TOML_MAX_DEPTH = 3
