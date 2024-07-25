# Конфигурация приложения

Большинство настроек, касающихся чтения конфигурации, можно задать через переменную [model_config](../usage/config.md#model_config).

Но настройки для файлов и переменных окружения могут быть заданы отдельно в [file_config](../usage/config.md#file_config) и [env_config](../usage/config.md#env_config) соответственно.
Настройки, указанные в `file_config` и `env_config`, будут иметь приоритет и отменять настройки, указанные в `model_config`.

Все остальные настройки, такие как задание источников конфигурации, управление обратным наследование и многие другие подробно описаны [здесь](../usage/config.md#)

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
