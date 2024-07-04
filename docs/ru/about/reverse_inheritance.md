# Обратное наследование

**Обратное наследование** - этот термин введён специально.
Он наиболее полно описывает поведение при передаче собственных настроек конфигурации от одного класса другому.

Причиной появления термина `Обратное наследование` стало решение изначально заложенных в данную библиотеку [целей и задач](library_goals.md).

Смысл заключается в передаче собственных настроек от класса-родителя к классам-детям. Это как обычное наследование, только наоборот - отсюда и название.


## Пример стандартного поведения

```py title="settings.py"
from arfi_settings import ArFiSettings, SettingsConfigDict


class Grandson(ArFiSettings):
    pass


class Child(ArFiSettings):
    grandson: Grandson


class Parent(ArFiSettings):
    child: Child


config = Parent()

print(config.conf_path)
#> [PosixPath('config/config')]
print(config.child.grandson.conf_path)
#> [PosixPath('config/child/grandson/config')]
print(config.settings_config.env_nested_delimiter)
#> ""
print(config.child.grandson.settings_config.env_nested_delimiter)
#> ""


# Change settings in parent class
class Parent(ArFiSettings):  # (1)!
    child: Child
    model_config = SettingsConfigDict(
        conf_dir=None,
        conf_file=['appconfig.yaml', '~/.config/alacritty/alacritty.toml'],
        env_nested_delimiter="__",
    )


config = Parent()

print(config.conf_path)
#> [PosixPath('appconfig.yaml'), PosixPath('/home/user/.config/alacritty/alacritty.toml')]
print(config.child.grandson.conf_path)
#> [PosixPath('child/grandson/appconfig.yaml'), PosixPath('/home/user/.config/alacritty/alacritty.toml')]
print(config.settings_config.env_nested_delimiter)
#> "__"
print(config.child.grandson.settings_config.env_nested_delimiter)
#> "__"
```

1. Меняем настройки в родительском классе и они автоматически передаются и ребёнку и внуку

При этом если мы создадим другой класс-родитель `#!python OtherParent()` с аттрибутом `child` и переопределим в нём настройки, то эти настройки никак не повлияют на предыдущие настройки класса `#!python Parent()`

```py title="settings.py"

class OtherParent(ArFiSettings):
    child: Child
    model_config = SettingsConfigDict(
        env_nested_delimiter="@@@",
    )


other_config = OtherParent()

print(other_config.child.grandson.settings_config.env_nested_delimiter)
#> "@@@"
print(config.child.grandson.settings_config.env_nested_delimiter)
#> "__"
```

> **Замечание**: Даже если мы явно зададим в классе `#!python Grandson` какой-нибудь другой `env_nested_delimiter`, то он переопределится настройками, заданными в классах `#!python Parent` и `#!python OtherParent`


## Полная отмена обратного наследования настроек

В большинстве случаев обратное наследование очень полезно. Но иногда требуется отключить эту функцию для более тонкой настройки каждого класса.

Так как наследуются абсолютно все параметры, то каждый нужно отключать по отдельности.
Это можно сделать 2-я способами.

### Отключение в классе

```py title="settings.py"
from arfi_settings import ArFiSettings, EnvConfigDict, FileConfigDict


class Database(ArFiSettings):
    db_name: str

    ordered_settings_inherit_parents = False  # (3)!
    env_config_inherit_parents = False  # (5)!


class City(ArFiSettings):
    name: str


class AppSettings(ArFiSettings):
    city: City

    ordered_settings_inherit_parents = False  # (2)!
    file_config_inherit_parents = False  # (4)!


class AppConfig(ArFiSettings):
    project_name: str
    db: Database
    app: AppSettings

    ordered_settings = ["env"]  # (1)!
    env_config = EnvConfigDict(
        env_prefix="SUPER_",
        env_nested_delimiter="__",
    )
    file_config = FileConfigDict(
        conf_dir="/opt/my_app",
    )
```

1. Устанавливаем чтение настроек только из переменных окружения
2. Отменяем наследование, а значит читаем настройки из всех источников по умолчанию
3. Отменяем наследование, а значит читаем настройки из всех источников по умолчанию
4. Отменяем наследование настроек только для файлов, директория вернётся к стандартной `config/app`. Для переменных окружения настройки будут унаследованы
5. Отменяем наследование настроек только для переменных окружения. Директория чтения из файлов `/opt/my_app/db` будет унаследована.


### Отключение в файле `pyproject.toml`

``` toml title="pyproject.toml"
[tool.arfi_settings]              # (1)!
mode_dir_inherit_nested = false
mode_dir_inherit_parent = false
file_config_inherit_parent = false
env_config_inherit_parent = false
handler_inherit_parent = false
ordered_settings_inherit_parent = false
```

1. Полное отключение всего обратного наследования


## Частичная отмена обратного наследования

Когда нужно отключить наследование только одного или нескольких параметров, а остальные унаследовать от родителя, то это тоже можно решить двумя путями - через настройки конкретного класса или через глобальные настройки в файле `pyproject.toml`.

Параметры, переданные в общий параметр `exclude_inherit_parent` автоматически распределяются по категориям в `conf_exclude_inherit_parent` и `env_exclude_inherit_parent` и передаются выше по стеку обратного наследования.

Сами параметры `conf_exclude_inherit_parent` и `env_exclude_inherit_parent` тоже наследуются, поэтому их наследование можно отменить через общий параметр `exclude_inherit_parent`, который не наследуется.

> Посмотреть все унаследованные параметры можно с помощью `inherited_params` следующим образом:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppSettings(ArFiSettings):
    pass


class AppConfig(ArFiSettings):
    app: AppSettings

    model_config = SettingsConfigDict(
        encoding="cp1251",
        exclude_inherit_parent=[
            "conf_file",
            "conf_ext",
            "env_prefix",
            "conf_file_encoding",
        ],
    )


config = AppConfig()
print(config.app.inherited_params)
```


### Отключение в классе


```py
from arfi_settings import ArFiSettings, SettingsConfigDict, EnvConfigDict


class AppSettings(ArFiSettings):
    env_config = EnvConfigDict(
        env_exclude_inherit_parent=[
            "env_file_encoding",
      ]
    )


class AppConfig(ArFiSettings):
    app: AppSettings

    model_config = SettingsConfigDict(
        encoding="cp1251",
    )


config = AppConfig()

print(config.app.settings_config.conf_file_encoding)
#> cp1251
print(config.app.settings_config.env_file_encoding)
#> None
```


### Отключение в файле `pyproject.toml`

```toml title="pyproject.toml"
[tool.arfi_settings]
exclude_inherit_parent = ["env_file_encoding"]  # (1)!
```

1. Во всём проекте не будет наследоваться `env_file_encoding`, если это не переопределено в классе.

## Выбор наследования определённых параметров

Иногда нужно, чтоб унаследовался только один параметр (или несколько), например `conf_ext` - расширения для чтения файлов, а остальные параметры должны определятся в самих классах.

Для решения этой задачи введён общий параметр `include_inherit_parent`. А для более гибкой настройки еще 2 параметра - `conf_include_inherit_parent` и `env_include_inherit_parent`.

Задавать их так же можно как непосредственно в классе, так и в файле `pyproject.toml` для глобальной настройки.

> **Замечание**: Если параметр находится в `conf_exclude_inherit_parent`,  `env_exclude_inherit_parent` или в `exclude_inherit_parent`, то он не будет добавлен! Переменные `exclude_` имеют приоритет над переменными `include_`

### Выбор в классе

```py title="settings.py"
from arfi_settings import ArFiSettings, SettingsConfigDict, FileConfigDict


class AppSettings(ArFiSettings):
    file_config = FileConfigDict(
        conf_include_inherit_parent=["conf_ext"], # (1)!
        conf_exclude_inherit_parent=[
            "conf_include_inherit_parent",        # (2)!
            "conf_exclude_inherit_parent",        # (3)!
        ],
    )


class AppConfig(ArFiSettings):
    app: AppSettings

    model_config = SettingsConfigDict(
        conf_dir="test",
        conf_file="test.yaml",
        conf_ext=[".yml", "json"],
        exclude_inherit_parent=["conf_ext"],      # (4)!
    )


config = AppConfig()

print(config.app.settings_config.conf_ext)
#> ['yml', 'json']

# but
print(config.app.settings_config.conf_dir)   # (5)!
#> config
print(config.app.settings_config.conf_file)  # (6)!
#> config

print(config.app.inherited_params)           # (7)!
#> ['conf_ext', 'env_include_inherit_parent', 'env_exclude_inherit_parent', 'env_file', 'env_prefix', 'env_prefix_as_mode_dir', 'env_prefix_as_nested_mode_dir', 'env_prefix_as_source_mode_dir', 'env_file_encoding', 'env_case_sensitive', 'env_nested_delimiter', 'env_ignore_missing']
```

1. Указываем только тот параметр, который нам нужно наследовать
2. Запрещаем наследование пустого списка параметров `conf_include_inherit_parent` из класса `AppConfig`
3. Запрещаем наследование `conf_exclude_inherit_parent` из класса `AppConfig`, иначе `conf_ext` не унаследуется.
4. Запрещаем обратное наследование параметра `conf_ext`
5. `conf_dir` не наследуется
6. `conf_file` не наследуется
7. Проверяем, какие параметры наследуются из класса `AppConfig`


### Выбор в файле `pyproject.toml`

```toml title="pyproject.toml"
[tool.arfi_settings]
include_inherit_parent = ["conf_ext"]
exclude_inherit_parent = [
  "conf_include_inherit_parent",
  "conf_exclude_inherit_parent",
]
```
