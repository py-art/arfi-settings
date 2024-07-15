# Режим отладки

> На данный момент имеет минимальный функционал. Находится на стадии разработки.


## arfi_debug

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

## Включение в файле `pyproject.toml`

```toml title="pyproject.toml"
[tool.arfi_settings]
arfi_debug = true
```

```py title="settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```

Запускаем в терминале:

```bash
$ python settings.py
```

Примерный результат вывода:

```
[PRE INIT] AppConfig
root_dir = /home/user/my_awesome_project
BASE_DIR = /home/user/my_awesome_project
pyproject_toml_path = /home/user/my_awesome_project/pyproject.toml
conf_path = [
    "/home/user/my_awesome_project/config/config"
]
env_path = [
    "/home/user/my_awesome_project/.env"
]
mode_dir_path = .
computed_mode_dir =
source_mode_dir = .
nested_mode_dir = .
parent_mode_dir = .
settings_config = {
    "env_file": ".env",
    "env_prefix": "",
    "env_prefix_as_mode_dir": false,
    "env_prefix_as_nested_mode_dir": false,
    "env_prefix_as_source_mode_dir": false,
    "env_file_encoding": null,
    "env_case_sensitive": false,
    "env_nested_delimiter": "",
    "env_ignore_missing": true,
    "env_include_inherit_parent": [],
    "env_exclude_inherit_parent": [],
    "conf_file": "config",
    "conf_dir": "config",
    "conf_ext": [
        "toml",
        "yaml",
        "yml",
        "json"
    ],
    "conf_file_encoding": null,
    "conf_case_sensitive": false,
    "conf_ignore_missing": true,
    "conf_custom_ext_handler": null,
    "conf_include_inherit_parent": [],
    "conf_exclude_inherit_parent": [],
    "case_sensitive": false,
    "ignore_missing": true,
    "encoding": null,
    "cli": false,
    "secrets_dir": null,
    "conf_path": [
        "config/config"
    ],
    "env_path": [
        ".env"
    ],
    "include_inherit_parent": [],
    "exclude_inherit_parent": []
}
values before handler:
{}


values after handler:
{}
```


## Включение в коде

> Полноценно включается только в файле `pyproject.toml`. Включение при инициализации класса выдаёт урезанную информацию.

```py title="settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig(_arfi_debug=True)
```

Запускаем в терминале:

```bash
$ python settings.py
```

Примерный результат вывода:

```
[PRE INIT] AppConfig
root_dir = /home/user/my_awesome_project
BASE_DIR = /home/user/my_awesome_project
pyproject_toml_path = /home/user/my_awesome_project/pyproject.toml
conf_path = [
    "/home/user/my_awesome_project/config/config"
]
env_path = [
    "/home/user/my_awesome_project/.env"
]
```
