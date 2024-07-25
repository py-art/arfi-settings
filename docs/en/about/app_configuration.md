# Application Configuration

Most settings related to reading the configuration can be set via the [model_config](usage/config.md#model_config) variable.

But the settings for files and environment variables can be set separately in [file_config](../usage/config.md#file_config) and [env_config](../usage/config.md#env_config) respectively.
The settings specified in `file_config` and `env_config` will take precedence and override the settings specified in `model_config`.

All other settings such as specifying configuration sources, managing reverse inheritance and many others are described in detail [here](../usage/config.md#)

```py
from arfi_settings import ArFiSettings, EnvConfigDict, FileConfigDict, SettingsConfigDict


class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_case_sensitive=True,
    )
    env_config = EnvConfigDict(
        env_case_sensitive=False,
    )
    model_config = SettingsConfigDict(
        conf_case_sensitive=False,
        env_case_sensitive=True,
    )

config = AppConfig()
print(config.settings_config.conf_case_sensitive)
#> True
print(config.settings_config.env_case_sensitive)
#> False
```
