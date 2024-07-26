# Настройки `pyproject.toml`

## Описание

В файле `pyproject.toml` указываются ***настройки по умолчанию*** глобально для всего проекта.

Как это работает:

- При инициализации класса настроек, не инстанса класса, а именно при инициализации самого класса, сначала происходит поиск значений, указанных в этом классе.
- Если в классе значение переменной не задано, то значение берётся из файла `pyproject.toml`.
- Если значение переменной не задано в файле `pyproject.toml`, то берётся значение по умолчанию.

Таким образом приоритет значений выглядит так, в порядке возрастания:

- значение по умолчанию
- значение из файла `pyproject.toml`
- значение, заданное в классе
- значение переданное при инициализации инстанса класса


## Пример

Рассмотрим порядок приоритета значений, на примере кодировки файлов - параметр [encoding](config.md#encoding).

- Значение по умолчанию `None`, что при чтении файлов равносильно `utf-8`

```py
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
print(config.settings_config.encoding)
#> None
```

- Теперь создадим в корне проекта файл `pyproject.toml`

В нём укажем кодировку `#!toml encoding="cp1251"`.

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

Выполним опять предыдущий код и увидим, что значение кодировки по умолчанию поменялось

```py
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
print(config.settings_config.encoding)
#> cp1251
```

- Теперь укажем кодировку непосредственно в самом классе настроек, оставив файл `pyproject.toml` каким он был на предыдущем шаге.

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        encoding="ISO-8859-1",
    )


config = AppConfig()
print(config.settings_config.encoding)
#> ISO-8859-1
```

- Теперь укажем кодировку при инициализации инстанса

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        encoding="ISO-8859-1",
    )


config = AppConfig(_encoding="latin_1")
print(config.settings_config.encoding)
#> latin_1
```


## Переменные

Подробно описание этих переменных уже существует, по этому ниже будут указаны только ссылки на те переменные, которые можно задать в файле `pyproject.toml`.

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


## Поиск pyproject.toml

Расположение файла `pyproject.toml` определяется автоматически. По умолчанию поиск осуществляется максимум на 3 каталога вверх от файла, в котором происходить инициализация инстанса класса настроек (подкласса `arfi_settings.ArFiSettings`).

Если путь до файла `pyproject.toml` не определился автоматически, то можно вручную задать либо максимальную глубину поиска параметром `pyproject_toml_max_depth`, либо точную глубину параметром `pyproject_toml_depth`.

> **Заметка**: Если указаны оба параметра `pyproject_toml_max_depth` и `pyproject_toml_depth`, то параметр `pyproject_toml_depth` будет иметь приоритет.

Так же можно запретить поиск и чтение настроек по умолчанию из файла `pyproject.toml` индивидуально для класса или для экземпляра класса, установив параметр [read_pyproject_toml](config.md#read_pyproject_toml) в значение `False` или передав его при инициализации инстанса класса параметром `_read_pyproject_toml=False`.

Посмотреть, какой путь до файла определился автоматически можно с помощью свойства [pyproject_toml_path](config.md#pyproject_toml_path).

### По умолчанию

Ниже приведены примеры использования и стандартное поведение библиотеки.

- Самая простая структура проекта. Путь до файла определяется автоматически.

```
~/my_project/
├── __init__.py
├── main.py
├── settings.py
└── pyproject.toml
```

```py title="~/my_project/settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```

```py title="~/my_project/main.py"
from settings import config

print(config.pyproject_toml_path)
#> /home/user/my_project/pyproject.toml
```

Результат запуска в терминале:

```bash
$ pwd
/home/user/my_project
$ python main.py
/home/user/my_project/pyproject.toml
```

- Стандартная структура проекта. Путь до файла определяется автоматически.

```
~/my_project/
├── settings/
│  ├── __init__.py
│  └── settings.py
├── __init__.py
├── main.py
└── pyproject.toml
```

```py title="~/my_project/settings/settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```

```py title="~/my_project/main.py"
from settings.settings import config

print(config.pyproject_toml_path)
#> /home/user/my_project/pyproject.toml
```

Результат запуска в терминале:

```bash
$ pwd
/home/user/my_project
$ python main.py
/home/user/my_project/pyproject.toml
```

- Ещё одна стандартная структура проекта. Путь до файла определяется автоматически.

```
~/my-project/
├── my_project
│   ├── settings
│   │  ├── __init__.py
│   │  └── settings.py
│   ├── __init__.py
│   └── main.py
└── pyproject.toml
```

```py title="~/my-project/my_project/settings/settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```

```py title="~/my-project/my_project/main.py"
from settings.settings import config

print(config.pyproject_toml_path)
#> /home/user/my-project/pyproject.toml
```

Результат запуска в терминале:

```bash
$ pwd
/home/user/my-project
$ python my_project/main.py
/home/user/my-project/pyproject.toml
```

- Стандартная структура проекта, с наличием `src`. Путь до файла определяется автоматически.

```
~/my-project/
├── src
│  └── my_project
│     ├── settings
│     │  ├── __init__.py
│     │  └── settings.py
│     ├── __init__.py
│     └── main.py
└── pyproject.toml
```

```py title="~/my-project/src/my_project/settings/settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```

```py title="~/my-project/src/my_project/main.py"
from settings.settings import config

print(config.pyproject_toml_path)
#> /home/user/my-project/pyproject.toml
```

Результат запуска в терминале:

```bash
$ pwd
/home/user/my-project
$ python src/my_project/main.py
/home/user/my-project/pyproject.toml
```

- Сложная структура проекта. Путь до файла нужно указывать вручную

```

~/my-project/
├── src
│  └── my_project
│     ├── core
│     │  ├── settings
│     │  │  ├── __init__.py
│     │  │  └── settings.py
│     │  └── __init__.py
│     ├── __init__.py
│     └── main.py
└── pyproject.toml

```

```py title="~/my-project/src/my_project/core/settings/settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```

```py title="~/my-project/src/my_project/main.py"
from core.settings.settings import config

print(config.pyproject_toml_path)  # (1)!
#> None
```

1. Путь до файла НЕ определился автоматически

Результат запуска в терминале:

```bash
$ pwd
/home/user/my-project
$ python src/my_project/main.py
None
```

**Первый способ** (предпочтительный) с помощью встроенной команды `read_pyproject`:

> **Важно**: Команду `arfi_settings.init_settings.read_pyproject` необходимо вызывать перед импортом всех классов настроек! Проще всего это сделать в файле `__init__.py` в пакете, в котором расположен модуль, содержащий классы настроек.

- Меняем глубину поиска

```py title="~/my-project/src/my_project/core/settings/__init__.py"
from arfi_settings import init_settings

init_settings.read_pyproject(
    pyproject_toml_max_depth=10,  # (1)!
)
```

1. В конкретном примере точная глубина расположения файла равна 5. Поиск остановится сам, как только файл `pyproject.toml` будет найден.

- Или указываем точную глубину расположения файла `pyproject.toml`

```py title="~/my-project/src/my_project/core/settings/__init__.py"
from arfi_settings import init_settings

init_settings.read_pyproject(
    pyproject_toml_depth=5,
)
```

Результат запуска в терминале при указании `pyproject_toml_max_depth` или `pyproject_toml_depth`  будет одинаковым:
```bash
$ pwd
/home/user/my-project
$ python src/my_project/main.py
/home/user/my-project/pyproject.toml
```

**Второй способ** - с помощью передачи аргументов в момент инициализации инстанса настроек:

- Меняем глубину поиска

```py title="~/my-project/src/my_project/core/settings/settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig(
    _pyproject_toml_max_depth=10,  # (1)!
)
```

1. В конкретном примере точная глубина расположения файла равна 5. Поиск остановится сам, как только файл `pyproject.toml` будет найден.

- Или указываем точную глубину расположения файла `pyproject.toml`

```py title="~/my-project/src/my_project/core/settings/settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig(
    _pyproject_toml_depth=5,
)
```

### Частный случай

Иногда при разработке мы можем устанавливать дополнительные библиотеки, расширения или плагины, в редактируемом режиме в корень нашего проекта с помощью команды `pip install -e my_plagin`. Назовём их все условно "Плагины".

У каждого из этих плагинов может быть собственный файл `pyproject.toml`, содержащий настройки по умолчанию, а в корне нашего проекта - свой собственный файл `pyproject.toml`.

Если в каком нибудь плагине содержится инициализация подкласса `arfi_settings.ArFiSettings`, например в поле модели установлено значение по умолчанию путём инициализации инстанса, то в момент инициализации этого инстанса будет автоматически запущен механизм поиска файла `pyproject.toml`. Этот поиск вернёт путь до файла `pyproject.toml`, принадлежащий именно этому плагину. И все настройки по умолчанию для этого инстанса будут прочитаны из файла плагина. Далее, мы импортируем класс с настройками из плагина и уже инициализируем наш собственный инстанс конфигурации. В этот момент снова запускается поиск файла `pyproject.toml`, который возвращает путь до файла `pyproject.toml` расположенного уже в корне нашего проекта и все настройки по умолчанию для класса, импортированного из плагина, перечитаются в соответствии с параметрами по умолчанию, указанными в файле `pyproject.toml` который расположен в корне нашего проекта.

Так как это не стандартная ситуация, то будет выведено предупреждение, что обнаружено несколько файлов `pyproject.toml`. Так же в предупреждении будет отображено для какого именно инстанса перечитаны настройки по умолчанию и из какого именно файла `pyproject.toml` они прочитаны.

**Пример**:

Здесь плагин `my_plugin` установлен командой `pip install -e my_plugin`.

Структура проекта:

```
~/my-project/
├── my-plugin
│  ├── src
│  │  └── my_plugin
│  │     ├── settings
│  │     │  ├── config
│  │     │  │  └── config.toml
│  │     │  ├── __init__.py
│  │     │  └── settings.py
│  │     ├── __init__.py
│  │     └── main.py
│  └── pyproject.toml
├── config
│  └── config.toml
├── settings
│  ├── __init__.py
│  └── settings.py
├── __init__.py
├── main.toml
└── pyproject.py
```

Файлы плагина:

```toml title="~/my-project/src/my_plugin/pyproject.toml"
[tool.arfi_settings]
conf_dir = "settings/config"
```

```toml title="~/my-project/src/my_plugin/settings/config/config.toml"
[param]
my_pluging_param = "param_from_PLUGIN"
```

```py title="~/my-project/src/my_plugin/settings/settings.py"
from arfi_settings import ArFiSettings


class ParamSettings(ArFiSettings):
    my_pluging_param: str = "default_my_plugin_param"


class MyPluginSettings(ArFiSettings):
    param: ParamSettings = ParamSettings()


config = MyPluginSettings()

```

Файлы проекта:

```toml title="~/my-project/pyproject.toml"
[tool.ruff.lint.per-file-ignores]
"main.py" = ["E402"]  # (1)!

[tool.arfi_settings]
conf_dir = "config"
```

1. Чтоб линтер не ругался на порядок импортов в файле `main.py`

```toml title="~/my-project/config/config.toml"
[plugin.param]
my_pluging_param = "param_from_PROJECT"
```

```py title="~/my-project/settings/settings.py"
from arfi_settings import ArFiSettings
from my_plugin import MyPluginSettings


class AppConfig(ArFiSettings):
    plugin: MyPluginSettings


config = AppConfig()
```

В главном файле проекта Сначала читаем настройки по умолчанию из `pyproject.toml`, а только потом импортируем `config`. При этом передаём параметр `read_once=True`, чтоб не читать файл `pyproject.toml` при каждой инициализации инстанса класса `arfi_settings.ArFiSettings`.

```py title="~/my-project/main.py"
from arfi_settings.init_config import init_settings
init_settings.read_pyproject(read_once=True)  # (1)!

from settings.settings import config

print(config.plugin.param.my_pluging_param)
#> param_from_PROJECT
```

1. Сначала читаем настройки по умолчанию из `pyproject.toml`, а только потом импортируем `config`!!!

**Важно**:

Если сначала импортировать настройки, а только потом выполнить функцию `#!python init_settings.read_pyproject(read_once=True)`, то библиотека выдаст несколько предупреждений:

> **Заметка**: Предупреждения нужны только для того, чтоб сообщить разработчику, что он делает что-то не так. Если плагин установить как обычную библиотек, а не в режиме редактирования, то предупреждения появляться не будут. Так же предупреждения появляться не будут, если в плагине нет инициализации инстансов класса `arfi_settings.ArFiSettings`, то есть только прописаны сами классы настроек, а все параметры передаются в источниках конфигурации.

```py title="~/my-project/main.py"
from arfi_settings.init_config import init_settings
from settings.settings import config

init_settings.read_pyproject(read_once=True)  # (1)!


print(config.plugin.param.my_pluging_param)
"""
/home/user/my-project/settings/settings.py:9: Warning:
Path to pyproject.toml has been changed !!!
instance AppConfig()
    previous path:
/home/user/my-project/my-plugin/pyproject.toml
    current path:
/home/user/my-project/pyproject.toml
Call once
  from arfi_settings.init_config import init_settings
  init_settings.read_pyproject(read_once=True)
before import any instance or subclass `ArFiSettings` for fix it.
  config = AppConfig()
/home/user/my-project/settings/settings.py:9: Warning:
Path to pyproject.toml has been changed !!!
for instance ParamSettings()
inside class AppConfig
    previous path:
/home/user/my-project/my-plugin/pyproject.toml
    current path:
/home/user/my-project/pyproject.toml
Call once
  from arfi_settings.init_config import init_settings
  init_settings.read_pyproject(read_once=True)
before import any instance or subclass `ArFiSettings` for fix it.
  config = AppConfig()
param_from_PROJECT
"""
```

1. Не правильный порядок запуска функции!!!

Но так же можно просто отключить отображение предупреждений.

```py title="~/my-project/main.py"
import warnings
warnings.filterwarnings("ignore")

from settings.settings import config

print(config.plugin.param.my_pluging_param)
#> param_from_PROJECT
```

> **Важно**: Если запустить `#!python init_settings.read_pyproject(read_once=True)` в самом плагине, то это может привести к некорректной работе данной библиотеки, так как настройки по умолчанию будут читаться из файла `pyproject.toml`, расположенного в плагине !!! Для того, чтобы этого избежать нужно передать в функцию `read_pyproject` дополнительный аргумент `read_force=True`:
```py title="~/my-project/main.py"
import warnings
from arfi_settings.init_config import init_settings

warnings.filterwarnings("ignore")
init_settings.read_pyproject(read_once=True, read_force=True)

from settings.settings import config

print(config.plugin.param.my_pluging_param)
#> param_from_PROJECT
```
