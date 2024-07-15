# Настройки `pyproject.toml`

Здесь указаны переменные, которые можно настроить в файле `pyproject.toml`, глобально для всего проекта.

**Пример использования**:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_dir = [
  "settings/config",
  "~/.config/myapp",
  "/var/run/secrets/config",
]
conf_ext = "toml, json"
env_config_inherit_parent = false
env_file = ""
env_nested_delimiter = "__"
encoding = "cp1251"
secrets_dir = "/var/run/secrets"
ordered_settings = [
  "cli",
  "secrets",
  "init_kwargs",
  "env",
  "conf_file",
]
cli = true
```

Подробно описание этих переменных уже существует, по этому ниже будут указаны только ссылки.


- [mode_dir_inherit_nested](config.md#mode_dir_inherit_nested)
- [mode_dir_inherit_parent](config.md#mode_dir_inherit_parent)
- [conf_dir](config.md#conf_dir)
- [conf_file](config.md#conf_file)
- [conf_ext](config.md#conf_ext)
- [conf_custom_ext_handler](config.md#conf_custom_ext_handler)
- [conf_file_encoding](config.md#conf_file_encoding)
- [conf_case_sensitive](config.md#conf_case_sensitive)
- [conf_ignore_missing](config.md#conf_ignore_missing)
- [conf_exclude_inherit_parent](config.md#conf_exclude_inherit_parent)
- [conf_include_inherit_parent](config.md#conf_include_inherit_parent)
- [env_file](config.md#env_file)
- [env_prefix](config.md#env_prefix)
- [env_prefix_as_mode_dir](config.md#env_prefix_as_mode_dir)
- [env_prefix_as_nested_mode_dir](config.md#env_prefix_as_nested_mode_dir)
- [env_prefix_as_source_mode_dir](config.md#env_prefix_as_source_mode_dir)
- [env_nested_delimiter](config.md#env_nested_delimiter)
- [env_file_encoding](config.md#env_file_encoding)
- [env_case_sensitive](config.md#env_case_sensitive)
- [env_ignore_missing](config.md#env_ignore_missing)
- [env_exclude_inherit_parent](config.md#env_exclude_inherit_parent)
- [env_include_inherit_parent](config.md#env_include_inherit_parent)
- [case_sensitive](config.md#case_sensitive)
- [ignore_missing](config.md#ignore_missing)
- [encoding](config.md#encoding)
- [cli](config.md#cli)
- [secrets_dir](config.md#secrets_dir)
- [exclude_inherit_parent](config.md#exclude_inherit_parent)
- [include_inherit_parent](config.md#include_inherit_parent)
- [file_config_inherit_parent](config.md#file_config_inherit_parent)
- [env_config_inherit_parent](config.md#env_config_inherit_parent)
- [handler](config.md#handler)
- [handler_inherit_parent](config.md#handler_inherit_parent)
- [ordered_settings](config.md#ordered_settings)
- [ordered_settings_inherit_parent](config.md#ordered_settings_inherit_parent)
- [arfi_debug](../about/debug_mode.md#arfi_debug)
