# Основные настройки

## MODE

Тип: `#!python str | None`

Значение по умолчанию: `#!python None`

**Что делает**:

Задаёт режим работы, например `debug`, `test`, `docker`, `prod` и так далее, для конкретного класса настроек или для всего приложения в целом.
Значение этой переменной не фиксированное и зависит только от вашего воображения!

Это одна из главных и **КЛЮЧЕВЫХ** особенностей библиотеки `arfi_settings`, которая ставит данную библиотеку на порядок выше всех остальных python-библиотек в направлении чтения и обработки настроек!

Основная цель библиотеки `arfi_settings` - это упростить жизнь разработчикам! Но остальные возможности библиотеки полностью закрывают потребности разработчиков настольных приложений.

Принцип работы этого параметра и лёг в основу создания текущей библиотеки.

Изначально предполагалось, что задание переменной окружения `MODE="prod"` должно автоматически переключать поведение всего приложения. Но по мере развития библиотеки оказалось, что можно задавать режимы работы не только для всего приложения в целом, но и отдельно для каждого класса настроек!

Например, в процессе разработки можно с лёгкостью переключаться между локальной базой данных, базой данных на тестовом стенде и реальной продуктовой базой данных, изменив всего один параметр `MODE` для настроек базы данных, при этом сохраняя все текущие локальные настройки, например для `Redis` или `token` телеграм-бота, в котором тестируется приложение.

То есть можно локально тестировать действующее приложение или часть приложения на реальных данных не выкатывая в прод, а просто изменив параметры подключения одной переменной. И это работает из коробки!

Параметр `MODE` - это обычное поле модели `pydantic.BaseModel`, тип `str`. По этому его можно задавать хоть в командной строке, хоть в секретной директории, хоть в переменных окружения, хоть в самих файлах конфигурации. Всё зависит от того, как именно вы настроите своё приложение, и какой механизм чтения настроек будет в нём прописан!


Если явно задать этот параметр в классе настроек, то он будет переопределён в соответствии с механизмом, заложенным в разделе [Обработчики файлов конфигурации](handlers.md#обработчики-файлов-конфигурации). По этому нет смысла явно задавать этот параметр в классе настроек!

Как показала практика, проще всего задавать режим для всего приложение в командной строке при запуске приложения или в секретной директории.
А вот в переменных окружения или в файлах конфигурации проще задавать режимы чтения для конкретных настроек при разработке, потому что в командной строке или в секретной директории нет привязки переменной к конкретному классу настроек.

Применение режима `MODE` распространяется только на чтение конфигурации приложения из файлов!!! Но никто не запрещает вам создавать эти файлы в секретной директории на сервере - просто можно добавить последним значением в списке [conf_dir](#conf_dir) именно секретную директорию и все файлы, указанные в этой секретной директории, сохраняя ту же иерархию,что при чтении из обычной директорий, будут иметь приоритет над предыдущими, указанными в этой же переменной!


**Использование**:

По умолчанию читается файл с именем `config` из всех директорий, заданных параметром [conf_dir](#confdir) и с первым найденным расширением, указанным в [conf_ext](#conf_ext).

Пример:

Здесь мы говорим, что нужно читать файл из директории [conf_dir](#conf_dir) с именем `production`, а расширения этого файла задаются параметром [conf_ext](#conf_ext).

```txt title="/var/run/secrets/MODE"
production
```

Задаём секретный пароль:

```toml title="/var/run/secrets/production.toml"
my_secret_password = "very_secret_password"
```

Задаём пароль по умолчанию, если не передан в секретной директории или в переменных окружения:

```toml title="config/production.toml"
my_secret_password = "local_secret_password"
```

Задаём пароль, который будет иметь приоритет над паролем по умолчанию из файлов конфигурации, но не из файлов в секретной директории:

```txt title=".env"
MY_SECRET_PASSWORD="env_secret_password"
```

Задаём наивысший приоритет секретной директории для чтения настроек:

> **Заметка**: Здесь, в конкретном примере, значения, указанные в секретной директории главнее чем в файлах конфигураций и главнее чем переменные окружения, но параметры, переданные в командной строке, по прежнему имеют приоритет!

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    My_Secret_Password: str

    ordered_settings = [
        "cli",
        "secrets",                      # (1)!
        "init_kwargs",
        "env",
        "env_file",
        "conf_file",
    ]
    model_config = SettingsConfigDict(
        conf_dir = [
            "config",
            "/var/run/secrets",
        ],
    )


config = AppConfig()
print(config.My_Secret_Password)
#> very_secret_password
```

1. Подняли приоритет чтения настроек из секретной директории над всеми остальными, кроме `CLI`

Как задать режим чтения настроек глобально для всего проекта с помощью командной строки более подробно описано [здесь](cli.md)



## BASE_DIR

Тип: `#!python Path | str | None`

Значение по умолчанию: `#!python None`

**Что делает**:

Указывает на базовую директорию проекта. Автоматически определяется один раз для всего проекта. Не наследуется в концепции обратного наследования. Есть возможность указать вручную для конкретного класса.

**Принцип автоматического определения**:

При первой инициализации любого подкласса `ArFiSettings` происходит поиск в текущей директории файл `__init__.py`. Если этот файл найден, то поднимаемся на директорию выше и снова ищем файл `__init__.py`. Если такого файла нет, то поиск останавливается. Последняя директория, в которой был найден файл `__init__.py` - это будет базовая директория проекта.

**Использование**:

Структура проекта
```
~/my-awesome-project
├── src
│  └── my_awesome_project
│     ├── settings
│     │  ├── __init__.py
│     │  └── settings.py
│     ├── __init__.py
│     └── main.py
└── pyproject.toml
```

Автоматическое определение

```py title="my-awesome-project/src/my_awesome_project/settings/settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```

```py title="my-awesome-project/src/my_awesome_project/main.py"
from settings.settings import config


print(config.BASE_DIR)
#> /home/user/my-awesome-project/src/my_awesome_project
```

Ручное указание

```py title="my-awesome-project/src/my_awesome_project/settings/settings.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    BASE_DIR = "~/my-awesome-project/src/my_awesome_project"


config = AppConfig()
```

```py title="my-awesome-project/src/my_awesome_project/main.py"
from settings.settings import config


print(config.BASE_DIR)
#> /home/user/my-awesome-project/src/my_awesome_project
```


## read_config

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

Включает или отключает чтение конфигурации из всех источников, кроме `init_kwargs`

> При обратном наследовании этот параметр автоматически устанавливается в `True`. Для полного отключения чтения настроек используйте `read_config_forc=Falsee` в классе или в истансе класса.

**Использование**:

```py
from arfi_settings import ArFiSettings

class AppConfig(ArFiSettings):
    read_config = False
```
или
```py
from arfi_settings import ArFiSettings

class AppConfig(ArFiSettings):
    pass

config = AppConfig(_read_config=False)
```

## read_config_force

Тип: `#!python bool | None`

Значение по умолчанию: `#!python None`

**Что делает**:

Принудительно включает или отключает чтение конфигурации из всех источников, кроме `init_kwargs`. Имеет приоритет над [read_config](#read_config).

**Использование**:

```py
from arfi_settings import ArFiSettings

class AppConfig(ArFiSettings):
    read_config_force = False
```
или
```py
from arfi_settings import ArFiSettings

class AppConfig(ArFiSettings):
    pass

config = AppConfig(_read_config_force=False)
```

## read_pyproject_toml

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

Включает или отключает чтение собственных настроек `arfi-settings` по умолчанию из файла `pyproject.toml`.

**Использование**:

```py
from arfi_settings import ArFiSettings

class AppConfig(ArFiSettings):
    read_pyproject_toml = False
```
или
```py
from arfi_settings import ArFiSettings

class AppConfig(ArFiSettings):
    pass

config = AppConfig(_read_pyproject_toml=False)
```

## mode_dir

Тип: `#!python str | Path | None`

Значение по умолчанию: `#!python Path('')`

**Что делает**:

1. При чтении из файлов указывает из какой поддиректории читать настройки, а точнее участвует в создании пути до этой поддиректории.
2. При чтении переменных окружения может использоваться как префикс.

Если не задано в явном виде, то определяется автоматически по имени атрибута в классе-родителе в концепции обратного наследования.

> **Заметка**: Не наследуется классическим способом, потому что участвует в обратном наследовании.

Для более глубокого понимания назначения можно почитать описание параметров [conf_path](#conf_path) и [env_prefix_as_source_mode_dir](#env_prefix_as_source_mode_dir)

**Использование**:

```py
from arfi_settings import ArFiSettings

class AppSettings(ArFiSettings):
    pass

class AppConfig(ArFiSettings):
    app: AppSettings

config = AppConfig()
print(config.app.mode_dir)
#> app
print(config.app.conf_path)
#> [PosixPath('config/app/config')]
```

Если указать явно:

```py
from arfi_settings import ArFiSettings

class AppSettings(ArFiSettings):
    mode_dir = 'my_app'

class AppConfig(ArFiSettings):
    app: AppSettings

config = AppConfig()
print(config.app.mode_dir)
#> my_app
print(config.app.conf_path)
#> [PosixPath('config/my_app/config')]
```

Отключение:

```py
from arfi_settings import ArFiSettings

class AppSettings(ArFiSettings):
    mode_dir = ""
    # or
    # mode_dir = None

class AppConfig(ArFiSettings):
    app: AppSettings

config = AppConfig()
print(config.app.mode_dir)
#> "" or None
print(config.app.conf_path)
#> [PosixPath('config/config')]
```


## mode_dir_inherit_nested

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

Включает или отключает наследование атрибута `mode_dir` у подклассов. Настраивается именно в подклассах.

**Использование**:

```py
from arfi_settings import ArFiSettings

class Database(ArFiSettings):
    mode_dir = "db"

class Postgres(Database):
    mode_dir = "postgres"

class AppConfig(ArFiSettings):
    database: Postgres = Postgres()

config = AppConfig()
print(config.database.mode_dir)
#> db/postgres
print(config.database.conf_path)
#> [PosixPath('config/db/postgres/config')]
```

Отключаем наследование:

```py
from arfi_settings import ArFiSettings

class Database(ArFiSettings):
    mode_dir = "db"

class Postgres(Database):
    mode_dir = "postgres"
    mode_dir_inherit_nested = False

class AppConfig(ArFiSettings):
    database: Postgres = Postgres()

config = AppConfig()
print(config.database.mode_dir)
#> postgres
print(config.database.conf_path)
#> [PosixPath('config/postgres/config')]
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
mode_dir_inherit_nested = false
```


## mode_dir_inherit_parent

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

Включает или отключает наследование атрибута `mode_dir` от класса-родителя в концепции обратного наследования.
Настраивается в классах-детях.

**Использование**:

```py
from arfi_settings import ArFiSettings

class Child(ArFiSettings):
    pass

class Parent(ArFiSettings):
    mode_dir = "parent"
    child: Child

config = Parent()
print(config.child.mode_dir)
#> child
print(config.child.conf_path)
#> [PosixPath('config/parent/child/config')]
```

Отключаем наследование:

```py
from arfi_settings import ArFiSettings

class Child(ArFiSettings):
    mode_dir_inherit_parent = False

class Parent(ArFiSettings):
    mode_dir = "parent"
    child: Child

config = Parent()
print(config.child.mode_dir)
#> child
print(config.child.conf_path)
#> [PosixPath('config/child/config')]
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
mode_dir_inherit_parent = false
```

## file_config

Тип: `#!python arfi_settings.types.FileConfigDict`

Значение по умолчанию: `#!python arfi_settings.schemes.FileConfigSchema().conf_dict()`

**Что делает**:

Настройки, которые описывают правила чтения из файлов конфигурации.

**Использование**:

```py
from arfi_settings import ArFiSettings, FileConfigDict

class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_dir = "settings/config",
    )
```

### conf_dir

Тип: `#!python Union[Path, str, List[Union[Path, str]], Tuple[Union[Path, str], ...], None]`

Значение по умолчанию: `#!python "config"`

**Что делает**:

Указывает из какой директории или директорий читать файлы с настройками.
Если указан список директорий, то настройки, расположенные в последней директории, будут переопределять все настройки из предыдущих.

**Использование**:

```py
from arfi_settings import ArFiSettings, FileConfigDict

class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_dir = ["config", "/opt/my_app/config"],
    )

config = AppConfig()
print(config.conf_path)
#> [PosixPath('config/config'), PosixPath('/opt/my_app/config/config')]
```

Или

```py
from arfi_settings import ArFiSettings, SettingsConfigDict

class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        conf_dir = "/var/run/secrets/config",
    )


config = AppConfig()
print(config.conf_path)
#> [PosixPath('/var/run/secrets/config/config')]
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_dir = "settings/config"  # (1)!
```

1. Здесь устанавливается по умолчанию для всех классов, если это не переопределено в самом классе.


### conf_file

Тип: `#!python Union[Path, str, List[Union[Path, str]], Tuple[Union[Path, str], ...], None]`

Значение по умолчанию: `#!python "config"`

**Что делает**:

Определяет название файла из которого будут читаться настройки по умолчанию в заданных директориях `conf_dir`.
При чтении настроек к этому имени файла добавляется расширение из `arfi_settingd.constants.CONFIG_EXT_DEFAULT`.
То есть, если параметр `conf_file` не имеет расширения, то происходит поиск до первого найденного файла по порядку с раширением из `CONFIG_EXT_DEFAULT` или из переданного параметра [conf_ext](#confext) - `config.toml`, потом `config.yaml`, и т.д.
Если передано конкретное расширение, например, `conf_file="config.ini"`, то происходит поиск только по этому расширению и остальные расширения игнорируются.

> **Заметка**: Полный путь до файла конфигурации строится следующим образом:
[BASE_DIR](#BASE_DIR) / [conf_dir](#conf_dir) / [mode_dir_path](#mode_dir_path) / [conf_file](#conf_file)[.[conf_ext](#conf_ext)], где `BASE_DIR /` добавляется в начало пути только если `conf_dir` не является абсолютным путём.


**Использование**:

```py
from arfi_settings import ArFiSettings, FFileConfigDictileConfigDict

class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_file = "appconfig",   # (1)!
    )

config = AppConfig()
print(config.conf_path)
#> [PosixPath('config/appconfig')]
```

1. Будет произведён поиск по порядку до первого найденного из `config.toml`, `config.yaml`, и т.д.

Указание файла с конкретным расширением:

```py
from arfi_settings import ArFiSettings, FileConfigDict

class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_file = "appconfig.json",   # (1)!
    )

config = AppConfig()
print(config.conf_path)
#> [PosixPath('config/appconfig.json')]
```

1. Поиск файла только с конкретным расширением `config.json`. Остальные файлы с именем `confit.toml`, `config.yaml` и т.д. игнорируются.

Отменить чтение из файлов:

```py
from arfi_settings import ArFiSettings, FileConfigDict

class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_file = None,
        # or
        # conf_file = ""
    )

config = AppConfig()
print(config.conf_path)
#> []
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_file = "appconfig"  # (1)!
```

1. Здесь устанавливается имя файла по умолчанию для всех классов из которого будут читаться настройки по умолчанию, если это не переопределено в самом классе.

Отменить полностью чтение из файлов:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_file = ""  # (1)!
```

1. Отменяет чтение из файлов для всех классов, но Значение, заданное в классе отменяет значение по умолчанию, заданное здесь, в `pyproject.toml`


### conf_ext

Тип: `#!python str | list[str]`

Значение по умолчанию: `#!python ["toml", "yaml", "yml" "json"]`

**Что делает**:

Добавляет указанные расширения к названию файла [conf_file](#conffile) при поиске файла с настройками.
Можно указывать как список с расширениями, так и строку вида `"ini, toml, cfg"`
Можно указать пустую строку `conf_ext=""` или добавить в список пустую строку, например `["json", ""]`, для чтения файлов без расширения.
При добавлении чтения файлов без расширения, в обязательном порядке, должен быть указан обработчик файлов без расширения в параметре [conf_custom_ext_handler](#conf_custom_ext_handler) !!!

Порядок расширения из списка от первого к последнему определяет поиск файлов конфигурации - файл `conf_file`.`conf_ext` с первым найденным расширение из списка будет прочитан, а остальные проигнорированы.

**Использование**:

```py
from arfi_settings import ArFiSettings, FileConfigDict

class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_ext = "cfg, ini",
    )
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_ext = ["json"]  # (1)!
```

1. Будут читаться файлы только с расширением `*.json`, остальные будут проигнорированы.
Значения заданные в классе - переопределяют значения по умолчания из файла `pyproject.toml`


### conf_custom_ext_handler

Тип: `#!python str | dict[str, str] | None`

Значение по умолчанию: `#!python None`

**Что делает**:

Переопределяет обработчик для расширения или задаёт определённый обработчик для файлов без расширения.
Имя обработчика должно заканчиваться на `_ext_handler`

**Использование**:

```py
from typing import Any

from arfi_settings import ArFiHandler, ArFiSettings, FileConfigDict
from arfi_settings.types import PathType


class MyHandler(ArFiHandler):
    def cfg_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        data["__case_sensitive"] = self.config.conf_case_sensitive
        return data

    def my_empty_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        data: dict[str, Any] = self.toml_ext_handler(file_path)
        # Do something ...
        return data


class AppConfig(ArFiSettings):
    handler_class = MyHandler
    file_config = FileConfigDict(
        conf_ext=["asd", "", "cfg"],      # (1)!
        conf_custom_ext_handler={         # (2)!
            "": "my_empty_ext_handler",   # (3)!
            "asd": "toml",                # (4)!
        },
    )


config = AppConfig()
print(config.file_config)
#> {'conf_ext': ['asd', '', 'cfg'], 'conf_custom_ext_handler': {'': 'my_empty_ext_handler', 'asd': 'toml'}}
```

1. Задаём порядок поиска файлов с расширениями. Если существуют все 3 файла `config.asd`, `config` и `config.cfg`, то `config.asd` будет прочитан, а остальные проигнорированы.
2. Для расширения `cfg` обработчик явно можно не указывать, так как имя обработчика заканчивается на `_ext_handler`. Но можно и явно указать, например `{"cfg": "cfg_ext_handler"}` или `{"cfg": "cfg"}`
3. Здесь указываем обработчик для файлов без расширения. Вместо длинного названия `my_empty_ext_handler` можно написать коротко - `my_empty`.
4. Здесь указываем, что все файлы с расширением `*.asd` должны быть обработаны как `toml`.

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_custom_ext_handler = "yaml"  # (1)!
```

1. Здесь говорим, что все файлы без расширения читать как `yaml`-файлы.


### conf_file_encoding

Тип: `#!python str | None`

Значение по умолчанию: `#!python None  # utf-8`

**Что делает**:

Задаёт кодировку при чтении файлов конфигурации. Применяется сразу ко всем файлам, указанным в [conf_file](#conf_file)

**Использование**:
```py
from arfi_settings import ArFiSettings, FileConfigDict

class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_file_encoding="cp1251",
    )
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_file_encoding = "cp1251"  # (1)!
```

1. Задаём кодировку `cp1251` для всех файлов конфигурации


### conf_case_sensitive

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

По умолчанию при чтении из файлов конфигурации параметры читаются как регистронезависимые. Но сначала ищется точное совпадение. Если точное совпадение не найдено, то возвращается найденное значение в нижнем регистре, если и оно не найдено, то возвращается первое найденное значение, приведённое к нижнему регистру.

**Использование**:

- Поведение по умолчанию

```toml title="config/config.toml"
MY_PARAM = "MY_PARAM_UPPER"
My_Param = "My_Param_exactly_match"
my_param = "my_param_lower"
```

```py title="settings.py"
from arfi_settings import ArFiSettings, FileConfigDict

class AppConfig(ArFiSettings):
    My_Param: str
    file_config = FileConfigDict(
        conf_case_sensitive=False,  # (1)!
    )

config = AppConfig()
print(config.My_Param)
#> My_Param_exactly_match
```

1. Значение по умолчанию

- Если отсутствует точное совпадение

```toml title="config/config.toml"
MY_PARAM = "MY_PARAM_UPPER"
my_param = "my_param_lower"
```

```py title="settings.py"
from arfi_settings import ArFiSettings, FileConfigDict

class AppConfig(ArFiSettings):
    My_Param: str
    file_config = FileConfigDict(
        conf_case_sensitive=False,  # (1)!
    )

config = AppConfig()
print(config.My_Param)
#> my_param_lower
```

1. Значение по умолчанию

- Если отсутствует точное совпадение, но поиск чувствительный к регистру

```toml title="config/config.toml"
MY_PARAM = "MY_PARAM_UPPER"
my_param = "my_param_lower"
```

```py title="settings.py"
from arfi_settings import ArFiSettings, FileConfigDict

class AppConfig(ArFiSettings):
    My_Param: str
    file_config = FileConfigDict(
        conf_case_sensitive=True,  # (1)!
    )

config = AppConfig()
print(config.My_Param)
"""
Traceback (most recent call last):
  ...
pydantic_core._pydantic_core.ValidationError: 1 validation error for AppConfig
My_Param
  Field required [type=missing, input_value={}, input_type=dict]
"""
```

1. Чувствительный к регистру поиск. Требуется точное совпадение

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_case_sensitive = true  # (1)!
```

1. Читать только точное совпадение имён (чувствительное к регистру) во всех файлах конфигурации


### conf_ignore_missing

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

По умолчанию, если файлы, заданные в [conf_file](#conf_file) не существуют, то их чтение игнорируется.  Но если требуется, чтоб файл или файлы обязательно присутствовали, то необходимо параметр `conf_ignore_missing` установить в значение `False`.
Так же можно использовать в качестве своеобразного отладчика - в сообщении об ошибке будет указано какой именно файл и по какому пути отсутствует.

**Использование**:

Поведение по умолчанию. Отсутствие файла `config/appconfig.yml` не приводит к ошибке
```py
from arfi_settings import ArFiSettings, FileConfigDict


class AppConfig(ArFiSettings):
    my_param: str = "default_param"
    file_config = FileConfigDict(
        conf_file="appconfig.yml",
        conf_ignore_missing=True,  # (1)!
    )


config = AppConfig()
print(config.my_param)
#> default_param
```

1. Значение по умолчанию. Отсутствие файлов игнорируется.

При отсутствии файла `config/appconfig.yml` возбуждается ошибка
```py
from arfi_settings import ArFiSettings, FileConfigDict


class AppConfig(ArFiSettings):
    my_param: str = "default_param"
    file_config = FileConfigDict(
        conf_file="appconfig.yml",
        conf_ignore_missing=False,  # (1)!
    )


config = AppConfig()
print(config.my_param)
"""
Traceback (most recent call last):
    ...
arfi_settings.errors.ArFiSettingsError: File not found: `/home/user/my_awesome_project/config/appconfig.yml`
"""
```

1. Требуется обязательное наличие всех файлов, указанных в `conf_file`!

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_ignore_missing = false  # (1)!
```

1. Все файлы конфигурации должны существовать


### conf_exclude_inherit_parent

Тип: `#!python list[str]`

Значение по умолчанию: `#!python []`

**Что делает**:

В концепции обратного наследования запрещает наследование определённых собственных настроек от класса-родителя
Применяется только при чтении файлов конфигурации.

**Использование**:

Например мы хотим унаследовать от родителя все настройки, кроме `conf_dir` и `conf_file`
```py
from arfi_settings import ArFiSettings, FileConfigDict


class Child(ArFiSettings):
    file_config = FileConfigDict(
        conf_exclude_inherit_parent=[
            "conf_dir",
            "conf_file",
        ],
    )


class Parent(ArFiSettings):
    child: Child

    file_config = FileConfigDict(
        conf_dir=None,
        conf_file="appconfig.yml",
    )


config = Parent()
print(config.settings_config.conf_dir)
#> None
print(config.settings_config.conf_file)
#> appconfig.yml
print(config.conf_path)
#> [PosixPath('appconfig.yml')]
print(config.child.settings_config.conf_dir)
#> config
print(config.child.settings_config.conf_file)
#> config
print(config.child.conf_path)
#> [PosixPath('config/child/config')]
```

> **Важно**: Так как "обратно" наследуются абсолютно все параметры, то и `conf_exclude_inherit_parent` не сработает для `#!python Child`, если в классе `#!python Parent` тоже указан параметр `conf_exclude_inherit_parent`!!! Для этого его тоже нужно исключить из наследования. Пример:

```py
class Child(ArFiSettings):
    file_config = FileConfigDict(
        conf_exclude_inherit_parent=[
            "conf_dir",
            "conf_file",
            "conf_exclude_inherit_parent",
        ],
    )


class Parent(ArFiSettings):
    child: Child

    file_config = FileConfigDict(
        conf_dir=None,
        conf_file="appconfig.yml",
        conf_exclude_inherit_parent=[
            "conf_ext",
        ],
    )

config = Parent()
```

> **Полезно**: Для просмотра всех унаследованных параметров (собственных настроек) используйте свойство [inherited_params](#inherited_params) - `#!python print(config.inherited_params)`

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_exclude_inherit_parent=[
    "conf_file",                    # (1)!
    "conf_exclude_inherit_parent",  # (2)!
]
```

1. Не наследовать название файла, из которого происходит чтение настроек по умолчанию
2. Не наследовать исключённые параметры


### conf_include_inherit_parent

Тип: `#!python list[str]`

Значение по умолчанию: `#!python []`

**Что делает**:

В концепции обратного наследования запрещает наследование от класса-родителя всех собственных настроек, кроме указанных.
Применяется только при чтении файлов конфигураций.

**Использование**:

Например мы хотим унаследовать от родителя только расширения при чтении файлов:
```py
from arfi_settings import ArFiSettings, FileConfigDict


class Child(ArFiSettings):
    file_config = FileConfigDict(
        conf_include_inherit_parent=[
            "conf_ext",
        ],
    )


class Parent(ArFiSettings):
    child: Child

    file_config = FileConfigDict(
        conf_dir=None,
        conf_file="appconfig",
        conf_ext="toml, json",
    )


config = Parent()
print(config.settings_config.conf_dir)
#> None
print(config.settings_config.conf_file)
#> appconfig
print(config.settings_config.conf_ext)
#> ['toml', 'json']
print(config.conf_path)
#> [PosixPath('appconfig')]
print(config.child.settings_config.conf_dir)
#> config
print(config.child.settings_config.conf_file)
#> config
print(config.child.settings_config.conf_ext)
#> ['toml', 'json']
print(config.child.conf_path)
#> [PosixPath('config/child/config')]
```

> **Важно**: Так как "обратно" наследуются абсолютно все параметры, то и `conf_include_inherit_parent` не сработает для `#!python Child`, если в классе `#!python Parent` тоже указан параметр `conf_include_inherit_parent`!!! Для этого его нужно исключить из наследования. Пример:

```py
class Child(ArFiSettings):
    file_config = FileConfigDict(
        conf_include_inherit_parent=[
            "conf_ext",
        ],
        conf_exclude_inherit_parent=[
            "conf_include_inherit_parent",
        ],
    )


class Parent(ArFiSettings):
    child: Child

    file_config = FileConfigDict(
        conf_file_encoding="cp1251",
        conf_ext="toml, json",
        conf_include_inherit_parent=[
            "conf_file_encoding",
        ],
    )


config = Parent()
print(config.settings_config.conf_file_encoding)
#> cp1251
print(config.settings_config.conf_ext)
#> ['toml', 'json']
print(config.child.settings_config.conf_file_encoding)
#> None
print(config.child.settings_config.conf_ext)
#> ['toml', 'json']
```

> **Важно**: Параметр `conf_exclude_inherit_parent` имеет приоритет над `conf_include_inherit_parent` и тоже наследуется! Если какой-либо параметр указан и там и там, то этот параметр НЕ будет включен в список наследуемых:

```py
from arfi_settings import ArFiSettings, FileConfigDict


class Child(ArFiSettings):
    file_config = FileConfigDict(
        conf_include_inherit_parent=[
            "conf_ext",
        ],
        conf_exclude_inherit_parent=[
            "conf_include_inherit_parent",
        ],
    )


class Parent(ArFiSettings):
    child: Child

    file_config = FileConfigDict(
        conf_file_encoding="cp1251",
        conf_ext="toml, json",
        conf_include_inherit_parent=[
            "conf_file_encoding",
        ],
        conf_exclude_inherit_parent=[
            "conf_ext",
        ],
    )


config = Parent()
print(config.settings_config.conf_file_encoding)
#> cp1251
print(config.settings_config.conf_ext)
#> ['toml', 'json']
print(config.child.settings_config.conf_file_encoding)
#> cp1251
print(config.child.settings_config.conf_ext)
#> ['toml', 'yaml', 'yml', 'json']
```

Чтоб отключить такое поведение и добиться того же результата, что и в примере выше, нужно сделать следующее:

```py
from arfi_settings import ArFiSettings, FileConfigDict


class Child(ArFiSettings):
    file_config = FileConfigDict(
        conf_include_inherit_parent=[
            "conf_ext",
        ],
        conf_exclude_inherit_parent=[
            "conf_include_inherit_parent",
            "conf_exclude_inherit_parent",  # (1)!
        ],
    )


class Parent(ArFiSettings):
    child: Child

    file_config = FileConfigDict(
        conf_file_encoding="cp1251",
        conf_ext="toml, json",
        conf_include_inherit_parent=[
            "conf_file_encoding",
        ],
        conf_exclude_inherit_parent=[
            "conf_ext",
        ],
    )


config = Parent()
print(config.settings_config.conf_file_encoding)
#> cp1251
print(config.settings_config.conf_ext)
#> ['toml', 'json']
print(config.child.settings_config.conf_file_encoding)
#> None
print(config.child.settings_config.conf_ext)
#> ['toml', 'json']
```

1. Исключаем из наследования `conf_exclude_inherit_parent` параметр.

> **Полезно**: Для просмотра всех унаследованных параметров (собственных настроек) используйте свойство [inherited_params](#inherited_params) - `#!python print(config.inherited_params)`

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
conf_include_inherit_parent=[
    "conf_ext",                    # (1)!
]
conf_exclude_inherit_parent=[
    "conf_include_inherit_parent",
]
```

1. Наследовать только расширения файлов


## env_config

Тип: `#!python arfi_settings.types.EnvConfigDict`

Значение по умолчанию: `#!python arfi_settings.schemes.EnvConfigSchema().env_dict()`

**Что делает**:

Настройки, которые описывают правила чтения переменных окружения.

**Использование**:

```py
from arfi_settings import ArFiSettings, EnvConfigDict

class AppConfig(ArFiSettings):
    env_config = EnvConfigDict(
        env_nested_delimiter = "__",
    )
```

### env_file

Тип: `#!python Union[Path, str, List[Union[Path, str]], Tuple[Union[Path, str], ...], None]`

Значение по умолчанию: `#!python ".env"`

**Что делает**:

Файл или список файлов из которых будут читаться переменные окружения. Если указан список файлов, то значения, указанные в последнем файле из этого списка, будут переопределять переменные, указанные в предыдущих файлах. Файлы можно указывать строкой, через запятую.

**Поиск файлов**:

Сначала происходит поиск файла в главной директории проекта [root_dir](#root_dir). Если файл не найден, то поиск происходит в базовой директории проекта [BASE_DIR](#BASE_DIR)

**Использование**:

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class AppConfig(ArFiSettings):
    env_config = EnvConfigDict(
        env_file = ".env, .env.prod",
    )
```


Файл `pyproject.toml`:

- Указание нескольких файлов
```toml title="pyproject.toml"
[tool.arfi_settings]
env_file = [".env", ".env.local", ".env.production"]
```
- Отключение чтения переменных окружения из файла
```toml title="pyproject.toml"
[tool.arfi_settings]
env_file = ""
```


### env_prefix

Тип: `#!python str`

Значение по умолчанию: `#!python ""`

**Что делает**:

При поиске переменных окружение подставляет указанное значение в начало имени переменной.

**Использование**:

```txt title=".env"
APP_NAME="My Awesome App"
```

```py
from arfi_settings import ArFiSettings, EnvConfigDict

class AppConfig(ArFiSettings):
    NAME: str
    env_config = EnvConfigDict(
        env_prefix = "APP_",
    )

config = AppConfig()
print(config.NAME)
#> My Awesome App
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_prefix = "MyPrefix--"
```


### env_prefix_as_mode_dir

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

При поиске переменных окружение подставляет [computed_mode_dir](#computed_mode_dir) - вычисляемое значение параметра [mode_dir](#mode_dir) в начало имени переменной.

> **Внимание**: Переопределяет значение, указанное в [env_prefix](#env_prefix) !!!

**Использование**:

```txt title=".env"
PARENT_NESTED_APP_NAME="My Application Name"
```

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class NestedConfig(ArFiSettings):
    mode_dir = "nested"


class AppSettings(NestedConfig):
    name: str


class AppConfig(ArFiSettings):
    app: AppSettings

    mode_dir = "parent"
    env_config = EnvConfigDict(
        env_prefix_as_mode_dir = True,
    )


config = AppConfig()
print(config.app.mode_dir)
#> nested/app
print(config.app.computed_mode_dir)
#> parent/nested/app
print(config.app.settings_config.env_prefix)
#> parent_nested_app_
print(config.app.name)
#> My Application Name
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_prefix_as_mode_dir = true
```

### env_prefix_as_nested_mode_dir

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

При поиске переменных окружение подставляет [mode_dir](#mode_dir) в начало имени переменной.

> **Внимание**: Переопределяет значение, указанное в [env_prefix](#env_prefix) и в [env_prefix_as_mode_dir](#env_prefix_as_mode_dir) !!!

**Использование**:

```txt title=".env"
NESTED_APP_NAME="My Application Name"
```

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class NestedConfig(ArFiSettings):
    mode_dir = "nested"


class AppSettings(NestedConfig):
    name: str


class AppConfig(ArFiSettings):
    app: AppSettings

    mode_dir = "parent"
    env_config = EnvConfigDict(
        env_prefix_as_nested_mode_dir = True,
    )


config = AppConfig()
print(config.app.mode_dir)
#> nested/app
print(config.app.nested_mode_dir)
#> nested
print(config.app.settings_config.env_prefix)
#> nested_app_
print(config.app.name)
#> My Application Name
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_prefix_as_nested_mode_dir = true
```

### env_prefix_as_source_mode_dir

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

При поиске переменных окружение подставляет [mode_dir](#mode_dir) в начало имени переменной.

> **Внимание**: Переопределяет значение, указанное в [env_prefix](#env_prefix), [env_prefix_as_mode_dir](#env_prefix_as_mode_dir) и в [env_prefix_as_nested_mode_dir](#env_prefix_as_nested_mode_dir)!!!

**Использование**:

```txt title=".env"
APP_NAME="My Application Name"
```

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class NestedConfig(ArFiSettings):
    mode_dir = "nested"


class AppSettings(NestedConfig):
    name: str


class AppConfig(ArFiSettings):
    app: AppSettings

    mode_dir = "parent"
    env_config = EnvConfigDict(
        env_prefix_as_source_mode_dir = True,
    )


config = AppConfig()
print(config.app.mode_dir)
#> nested/app
print(config.app.source_mode_dir)
#> app
print(config.app.settings_config.env_prefix)
#> app_
print(config.app.name)
#> My Application Name
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_prefix_as_source_mode_dir = true
```

### env_nested_delimiter
Тип: `#!python str`

Значение по умолчанию: `#!python ""`

**Что делает**:

При классическом наследовании если классы наследуются от `#!python pydantic.BaseModel` - то в названии переменной окружения при множественном вложении используется разделитель `__`, который отделяет имена атрибутов или их алиасы друг от друга.

**Использование**:

```txt title=".env"
NAME="Travel map"
COUNTRY__NAME="Russia"
COUNTRY__CITY__NAME="Moscow"
COUNTRY__CITY__STREET__NAME="Arbat Street"
```

```py
from arfi_settings import ArFiSettings, EnvConfigDict
from pydantic import AliasChoices, BaseModel, Field


class Street(BaseModel):
    short_name: str = Field(..., validation_alias=AliasChoices("Name", "StName", "street_name"))


class City(BaseModel):
    name: str
    street: Street


class Country(ArFiSettings):
    name: str
    city: City

    env_config = EnvConfigDict(
        env_nested_delimiter="--*--",
        env_exclude_inherit_parent=[
            "env_nested_delimiter",
        ],
    )


class AppConfig(ArFiSettings):
    PROJECT_NAME: str = Field(..., alias="name")
    country: Country

    mode_dir = "parent"
    env_config = EnvConfigDict(
        env_nested_delimiter = "__",
    )


config = AppConfig()
print(config.PROJECT_NAME)
#> Travel map
print(config.country.name)
#> Russia
print(config.country.city.name)
#> Moscow
print(config.country.city.street.short_name)
#> Arbat Street
```

Прелесть обратного наследования заключается в том, что для классов-детей можно переопределять или задавать собственные настройки и они также будут работать.
Например здесь в классах `#!python AppConfig` и `#!python Country` указан совершенно разный `env_nested_delimiter`. По умолчанию главнее те настройки, которые указаны в самом классе.
По этому мы можем дописать файл `.env`, как показано ниже, и получим совершенно другой результат.

```txt title=".env"
NAME="Travel map"
COUNTRY__NAME="Russia"
COUNTRY__CITY__NAME="Moscow"
COUNTRY__CITY__STREET__NAME="Arbat Street"

COUNTRY--*--NAME="Belarus"
COUNTRY--*--CITY--*--NAME="Minsk"
COUNTRY--*--CITY--*--STREET--*--NAME="Niamiha Street"
```
```py
config = AppConfig()
print(config.PROJECT_NAME)
#> Travel map
print(config.country.name)
#> Belarus
print(config.country.city.name)
#> Minsk
print(config.country.city.street.short_name)
#> Niamiha Street
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_nested_delimiter = "__"
```

### env_file_encoding

Тип: `#!python str | None`

Значение по умолчанию: `#!python None  # utf-8`

**Что делает**:

Задаёт кодировку при чтении переменных окружения из файлов. Применяется сразу ко всем файлам, указанным в [env_file](#env_file)

**Использование**:
```py
from arfi_settings import ArFiSettings, EnvConfigDict

class AppConfig(ArFiSettings):
    env_config = FileConfigDict(
        env_file_encoding="cp1251",
    )
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_file_encoding = "cp1251"
```

### env_case_sensitive

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

Указывает нужно ли обращать внимание на регистр имени при чтении переменных окружения.
Хотя по умолчанию переменные читаются как регистронезависимые, но приоритет всегда отдаётся точному совпадению, даже при множественной вложенности моделей!

Никаких ошибок возбуждаться НЕ будет, даже если вы ошиблись в написании имени переменной! Все имена переменных, не соответствующие критериям поиска будут проигнорированы!

**Использование**:

На самом деле это достаточно сложная тема, так как алгоритмы поиска немного отличаются друг от друга в зависимости от вариантов вложенности моделей. Возможно позже в документации будет создана отдельная тема, посвящённая этому. В дальнейшем, в обязательном порядке, это будет включено в режим отладки. А пока постараюсь объяснить вкратце.

Есть всего 3 варианта условий множественной вложенности моделей:

1. Все вложенные модели наследуются от класса `#!python pydantic.BaseModel`. Это самый простой классический вариант.
2. Все вложенные модели наследуются от класса `#!python arfi_settings.ArFiSettings`.
3. Комбинация первых двух вариантов.

Сложность заключается в том, что если вложенные модели наследуются от `#!python arfi_settings.ArFiSettings`, то у каждой такой модели могут быть свои собственные настройки для чтения переменных окружения, которые имеют приоритет, но при этом так же будут применяться настройки, указанные в классе-родителе в парадигме обратного наследования.

При таком поведении значение для одного и того же атрибута класса можно указать множеством имён переменных окружения. А если у этого атрибута есть ещё и несколько алиасов, то при регисторонезависимом поиске количество вариантов имён переменных окружения возрастает в несколько раз.

Все эти алгоритмы поиска уже реализованы. Ниже будут рассмотрены первые 2 варианта.

1. Все вложенные модели наследуются от класса `#!python pydantic.BaseModel`.

    * **Исходная модель**:

    ```py title="settings.py"
    from arfi_settings import ArFiSettings, EnvConfigDict
    from pydantic import BaseModel


    class Street(BaseModel):
        Name: str


    class City(BaseModel):
        Street: Street


    class Country(BaseModel):
        City: City


    class AppConfig(ArFiSettings):
        Country: Country

        env_config = EnvConfigDict(
            env_case_sensitive=False,   # by default
            env_nested_delimiter="__",
        )
    ```

    * **Задача**:

    Нужно указать переменную окружения для `#!python Street.Name`.

    * **Решение**:

    Самое простое решение, которое сработает только при `#!pyhton env_case_sensitive=False`, которое установлено по умолчанию:
    ```txt title=".env"
    COUNTRY__CITY__STREET__NAME="Awesome Street"
    ```
    ```py title="settings.py"
    config = AppConfig()
    print(config.Country.City.Street.Name)
    #> Awesome Street
    ```

    Вариант, который ОДИНАКОВО сработает и при `#!pyhton env_case_sensitive=True` и при `#!pyhton env_case_sensitive=False`:
    ```txt title=".env"
    COUNTRY__CITY__STREET__NAME="Awesome Street"
    Country__City__Street__Name="Awesome Street exactly match aliases names"
    ```
    ```py title="settings.py"
    config = AppConfig()
    print(config.Country.City.Street.Name)
    #> Awesome Street exactly match aliases names
    ```

    При `#!pyhton env_case_sensitive=True` будет произведён поиск только по имени переменной `Country__City__Street__Name`, остальные переменные будут проигнорированы.

    Ниже приведены примеры всех возможных вариантов имён переменных окружения при регистронезависимом поиске, `#!pyhton env_case_sensitive=False`, указанные в порядке возрастания приоритета поиска. Где 0 - имеет самый низший приоритет, а 16 - наивысший.

    > **Заметка**: В приведённом конкретном примере у каждого атрибута есть 2 алиаса, по которым производится поиск - это его имя и его имя в нижнем регистре.

    ```txt title=".env"
    # Не имеют приоритета, потому что не совпадают ни с одним вариантом поиска,
    # но будут прочитаны, если нет совпадений с вариантами поиска
    COUNTRY__CITY__STREET__NAME="Awesome Street - 0"
    couNTry__citY__StreeT__nAMe="Awesome Street - 0"
    country__city__street__NAME="Awesome Street - 0"

    # Ниже варианты, по которым происходит поиск, в порядке повышения приоритета
    country__city__street__name="Awesome Street - 1"
    country__city__street__Name="Awesome Street - 2"
    country__city__street__Name="Awesome Street - 3"
    country__city__Street__Name="Awesome Street - 4"
    country__City__street__name="Awesome Street - 5"
    country__City__street__Name="Awesome Street - 6"
    country__City__Street__name="Awesome Street - 7"
    country__City__Street__Name="Awesome Street - 8"
    Country__city__street__name="Awesome Street - 9"
    Country__city__street__Name="Awesome Street - 10"
    Country__city__street__Name="Awesome Street - 11"
    Country__city__Street__Name="Awesome Street - 12"
    Country__City__street__name="Awesome Street - 13"
    Country__City__street__Name="Awesome Street - 14"
    Country__City__Street__name="Awesome Street - 15"
    Country__City__Street__Name="Awesome Street - 16"
    ```

    ```py title="settings.py"
    config = AppConfig()
    print(config.Country.City.Street.Name)
    #> Awesome Street - 16
    ```

2. Все вложенные модели наследуются от класса `#!python arfi_settings.ArFiSettings`.

    * **Исходная модель**:

    > **Заметка**: Разделители выбраны чисто из соображения наглядности.

    ```py title="settings.py"
    from arfi_settings import ArFiSettings, EnvConfigDict


    class Street(ArFiSettings):
        Name: str

        env_config = EnvConfigDict(
            env_case_sensitive=False,   # by default
            env_nested_delimiter="--*--",
        )


    class City(ArFiSettings):
        Street: Street

        env_config = EnvConfigDict(
            env_case_sensitive=False,   # by default
            env_nested_delimiter="--^--",
        )


    class Country(ArFiSettings):
        City: City

        env_config = EnvConfigDict(
            env_case_sensitive=False,   # by default
            env_nested_delimiter="--@--",
            env_exclude_inherit_parent=[
                "env_nested_delimiter",
            ],
        )


    class AppConfig(ArFiSettings):
        Country: Country

        env_config = EnvConfigDict(
            env_case_sensitive=False,   # by default
            env_nested_delimiter="__",
        )
    ```

    * **Задача**:

    Нужно указать переменную окружения для `#!python Street.Name`.

    * **Решение**:

    Самое простое решение, которое сработает только при `#!pyhton env_case_sensitive=False`, которое установлено по умолчанию:
    ```txt title=".env"
    COUNTRY__CITY__STREET__NAME="Awesome Street"
    ```
    ```py title="settings.py"
    config = AppConfig()
    print(config.Country.City.Street.Name)
    #> Awesome Street
    ```

    Вариант, который ОДИНАКОВО сработает и при `#!pyhton env_case_sensitive=True` и при `#!pyhton env_case_sensitive=False`:
    ```txt title=".env"
    COUNTRY__CITY__STREET__NAME="Awesome Street"
    Country--*--City--*--Street--*--Name="Awesome Street exactly match aliases names"
    ```

    ```py title="settings.py"
    config = AppConfig()
    print(config.Country.City.Street.Name)
    #> Awesome Street exactly match aliases names
    ```

    * **Отличия от первого варианта**:

    Здесь для каждой вложенной модели указан свой собственный разделитель.
    Порядок разрешения имён будет точно таким же как и в первом варианте при наследовании всех вложенных моделей от `#!python pydantic.BaseModel`.
    Но порядок приоритета разделителей определяется правилами обратного наследования. То есть чтоб указать имя переменной среды окружения для атрибута `#!python Street.Name` можно использовать любой разделитель из "`__`", "`--@--`", "`--^--`", "`--*--`", но разделитель "`--*--`" будет иметь наивысший приоритет, так как он указан непосредственно в классе `Street` и атрибут `Name` принадлежит именно к этому классу, а разделитель "`__`" будет иметь самый низший приоритет, так как он принадлежит классу-родителю в иерархии обратного наследование.

    Такое поведение реализуется в силу того, что ВСЕ вложенные модели наследуются от `#!python arfi_settings.ArFiSettings`, а значит для каждой вложенной модели происходить поиск переменных окружения и каждое найденное значение передаётся по иерархии выше от класса-родителя к классу-ребёнку в концепции обратного наследования!

    В приведённом ниже примере в именах переменных окружения порядок алиасов имеет наивысший приоритет не зависимо от выставленного значения чувствительности к регистру. Но здесь уже вступает в силу правило обратного наследования, которое задаёт приоритет разделителю:
    ```txt title=".env"

    Country__City__Street__Name="Awesome Street exactly match aliases names - 1"
    Country--@--City--@--Street--@--Name="Awesome Street exactly match aliases names - 2"
    Country--^--City--^--Street--^--Name="Awesome Street exactly match aliases names - 3"
    Country--*--City--*--Street--*--Name="Awesome Street exactly match aliases names - 4"
    ```

    ```py title="settings.py"
    config = AppConfig()
    print(config.Country.City.Street.Name)
    #> Awesome Street exactly match aliases names - 4
    ```

    Данное поведение можно отключить, просто запретив читать переменные окружения для класса `Country` и всех его потомков в концепции обратного наследования. То есть, чтоб переменные окружения читались только для класса `AppConfig`.

    Это можно сделать следующим образом, при наличии тех же самых переменных окружения, что указаны выше:
    ```py title="settings.py"
    class Country(ArFiSettings):
        City: City

        ordered_settings = [
            "cli",
            "init_kwargs",
            "secrets",
            "conf_file",
        ]


    config = AppConfig()
    print(config.Country.City.Street.Name)
    #> Awesome Street exactly match aliases names - 1
    ```

    Вариантов использования настолько много, что можно запутаться. По этому и планируется дальнейшее развитие режима отладки, чтоб хотя бы можно было посмотреть, какие варианты ожидает получить программа и какой вариант будет приоритетнее.


> **Важно**: Не стоит забывать, что в приведённых выше примерах, переменную окружения можно задать следующего вида:
`Country='{"City": {"Street": {"Name": "Awesome Street"}}}'` и на неё будут распространятся те же правила разрешения имён в зависимости от регистра!!!


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_case_sensitive = true
```

### env_ignore_missing

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

По умолчанию, если файлы, заданные в [env_file](#env_file) не существуют, то их чтение игнорируется.  Но если требуется, чтоб файл или файлы обязательно присутствовали, то необходимо параметр `env_ignore_missing` установить в значение `False`.
Так же можно использовать в качестве своеобразного отладчика - в сообщении об ошибке будет указано какой именно файл и по какому пути отсутствует.

**Использование**:

Поведение по умолчанию. Отсутствие файла `.env` не приводит к ошибке
```py
from arfi_settings import ArFiSettings, EnvConfigDict


class AppConfig(ArFiSettings):
    my_param: str = "default_param"
    env_config = EnvConfigDict(
        env_file=".env",            # by default
        env_ignore_missing=True,    # by default
    )


config = AppConfig()
print(config.my_param)
#> default_param
```

При отсутствии файла `.env` возбуждается ошибка
```py
from arfi_settings import ArFiSettings, EnvConfigDict


class AppConfig(ArFiSettings):
    my_param: str = "default_param"
    env_config = EnvConfigDict(
        env_file=".env",            # by default
        env_ignore_missing=False,
    )


config = AppConfig()
print(config.my_param)
"""
Traceback (most recent call last):
    ...
arfi_settings.errors.ArFiSettingsError: File not found: `/home/user/my_awesome_project/.env`
"""
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_ignore_missing = false
```


### env_exclude_inherit_parent

Тип: `#!python list[str]`

Значение по умолчанию: `#!python []`

**Что делает**:

В концепции обратного наследования запрещает наследование определённых собственных настроек от класса-родителя
Применяется только при чтении переменных окружения

**Использование**:

Например мы хотим унаследовать от родителя все настройки, кроме `env_file_encoding` и `env_nested_delimiter`
```py
from arfi_settings import ArFiSettings, EnvConfigDict


class Child(ArFiSettings):
    env_config = EnvConfigDict(
        env_exclude_inherit_parent=[
            "env_file_encoding",
            "env_nested_delimiter",
        ],
    )

class Parent(ArFiSettings):
    child: Child

    env_config = EnvConfigDict(
        env_file=".env, .env.prod",
        env_prefix="APP_",
        env_file_encoding="cp1251",
        env_nested_delimiter="__",
    )

config = Parent()
print(config.settings_config.env_file_encoding)
#> cp1251
print(config.settings_config.env_nested_delimiter)
#> "__"
print(config.child.settings_config.env_file_encoding)
#> None
print(config.child.settings_config.env_nested_delimiter)
#> ""
```

> **Важно**: Так как "обратно" наследуются абсолютно все параметры, то и `env_exclude_inherit_parent` не сработает для `#!python Child`, если в классе `#!python Parent` тоже указан параметр `env_exclude_inherit_parent`!!! Для этого его тоже нужно исключить из наследования. Пример:

```py
class Child(ArFiSettings):
    env_config = EnvConfigDict(
        env_exclude_inherit_parent=[
            "env_file_encoding",
            "env_nested_delimiter",
            "env_exclude_inherit_parent",
        ],
    )

class Parent(ArFiSettings):
    child: Child

    env_config = EnvConfigDict(
        env_file=".env, .env.prod",
        env_prefix="APP_",
        env_file_encoding="cp1251",
        env_nested_delimiter="__",
        env_exclude_inherit_parent=[
            "env_file",
        ],
    )

config = Parent()
```

> **Полезно**: Для просмотра всех унаследованных параметров (собственных настроек) используйте свойство [inherited_params](#inherited_params) - `#!python print(config.inherited_params)`

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_exclude_inherit_parent=[
    "env_prefix",
    "env_exclude_inherit_parent",
]
```


### env_include_inherit_parent

Тип: `#!python list[str]`

Значение по умолчанию: `#!python []`

**Что делает**:

В концепции обратного наследования запрещает наследование от класса-родителя всех собственных настроек, кроме указанных.
Применяется только при чтении переменных окружения.

**Использование**:

Например мы хотим унаследовать от родителя только префикс:

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class Child(ArFiSettings):
    env_config = EnvConfigDict(
        env_include_inherit_parent=[
            "env_prefix",
        ],
    )


class Parent(ArFiSettings):
    child: Child

    env_config = EnvConfigDict(
        env_file=".env, .env.prod",
        env_prefix="APP_",
        env_file_encoding="cp1251",
        env_nested_delimiter="__",
    )

config = Parent()
print(config.settings_config.env_file)
#> .env, .env.prod
print(config.settings_config.env_prefix)
#> APP_
print(config.settings_config.env_file_encoding)
#> cp1251
print(config.settings_config.env_nested_delimiter)
#> "__"
print(config.child.settings_config.env_file)
#> .env
print(config.child.settings_config.env_prefix)
#> APP_
print(config.child.settings_config.env_file_encoding)
#> None
print(config.child.settings_config.env_nested_delimiter)
#> ""
```

> **Важно**: Так как "обратно" наследуются абсолютно все параметры, то и `env_include_inherit_parent` не сработает для `#!python Child`, если в классе `#!python Parent` тоже указан параметр `env_include_inherit_parent`!!! Для этого его нужно исключить из наследования. Пример:

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class Child(ArFiSettings):
    env_config = EnvConfigDict(
        env_include_inherit_parent=[
            "env_prefix",
        ],
        env_exclude_inherit_parent=[
            "env_include_inherit_parent",
        ],
    )


class Parent(ArFiSettings):
    child: Child

    env_config = EnvConfigDict(
        env_file=".env, .env.prod",
        env_prefix="APP_",
        env_file_encoding="cp1251",
        env_nested_delimiter="__",
        env_include_inherit_parent=[
            "env_file",
        ],
    )

config = Parent()
print(config.settings_config.env_file)
#> .env, .env.prod
print(config.settings_config.env_prefix)
#> APP_
print(config.settings_config.env_file_encoding)
#> cp1251
print(config.settings_config.env_nested_delimiter)
#> "__"
print(config.child.settings_config.env_file)
#> .env
print(config.child.settings_config.env_prefix)
#> APP_
print(config.child.settings_config.env_file_encoding)
#> None
print(config.child.settings_config.env_nested_delimiter)
#> ""
```

> **Важно**: Параметр `env_exclude_inherit_parent` имеет приоритет над `env_include_inherit_parent` и тоже наследуется! Если какой-либо параметр указан и там и там, то этот параметр НЕ будет включен в список наследуемых:

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class Child(ArFiSettings):
    env_config = EnvConfigDict(
        env_include_inherit_parent=[
            "env_prefix",
        ],
        env_exclude_inherit_parent=[
            "env_include_inherit_parent",
        ],
    )


class Parent(ArFiSettings):
    child: Child

    env_config = EnvConfigDict(
        env_file=".env, .env.prod",
        env_prefix="APP_",
        env_include_inherit_parent=[
            "env_file",
        ],
        env_exclude_inherit_parent=[
            "env_prefix",
        ],
    )

config = Parent()
print(config.settings_config.env_file)
#> .env, .env.prod
print(config.settings_config.env_prefix)
#> APP_
print(config.child.settings_config.env_file)
#> .env, .env.prod
print(config.child.settings_config.env_prefix)
#> ""
```

Чтоб отключить такое поведение и добиться того же результата, что и в примере выше, нужно сделать следующее:

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class Child(ArFiSettings):
    env_config = EnvConfigDict(
        env_include_inherit_parent=[
            "env_prefix",
        ],
        env_exclude_inherit_parent=[
            "env_include_inherit_parent",
            "env_exclude_inherit_parent",   # (1)!
        ],
    )


class Parent(ArFiSettings):
    child: Child

    env_config = EnvConfigDict(
        env_file=".env, .env.prod",
        env_prefix="APP_",
        env_include_inherit_parent=[
            "env_file",
        ],
        env_exclude_inherit_parent=[
            "env_prefix",
        ],
    )

config = Parent()
print(config.settings_config.env_file)
#> .env, .env.prod
print(config.settings_config.env_prefix)
#> APP_
print(config.child.settings_config.env_file)
#> .env, .env.prod
print(config.child.settings_config.env_prefix)
#> ""
```

1. Исключаем из наследования `env_exclude_inherit_parent` параметр.

> **Полезно**: Для просмотра всех унаследованных параметров (собственных настроек) используйте свойство [inherited_params](#inherited_params) - `#!python print(config.inherited_params)`

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_include_inherit_parent=[
    "env_prefix",
]
env_exclude_inherit_parent=[
    "env_include_inherit_parent",
]
```


## model_config

Тип: `#!python arfi_settings.types.SettingsConfigDict`

Значение по умолчанию: `#!python arfi_settings.schemes.SettingsConfigSchema().config_model_dict()`

**Общая информация**:

Содержит все стандартные настройки `#!python pydantic.ConfigDict`, такие как `extra`, `arbitrary_types_allowed` и т.д. Поддерживает все настройки, входящие в `file_config` и `env_config`. А так же имеет дополнительные собственные настройки, относящиеся к `arfi-settings`.

**Что делает**:

Единое пространство для описания всех настроек модели.

> **Важно**: Настройки, указанные в `file_config` и `env_config` будут переопределять те же настройки, указанные в `model_config`.

**Использование**:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        conf_dir = "settings/config",
        env_file = ".env.prod",
    )


config = AppConfig()
print(config.conf_path)
#> [PosixPath('settings/config/config')]
```

### case_sensitive
Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

1. Задает значение для [conf_case_sensitive](#conf_case_sensitive), если сама переменная `conf_case_sensitive` не задана ни в [file_config](#file_config) ни в [model_config](#model_config).
2. Задает значение для [env_case_sensitive](#env_case_sensitive), если сама переменная `env_case_sensitive` не задана ни в [env_config](#env_config) ни в [model_config](#model_config).
3. Определяет регистрозависимый или регистронезависимый режим чтения имён файлов из секретной директории [secrets_dir](#secrets_dir).
4. Влияет на передачу переменных обработчиком от класса-родителя к классу-ребёнку в концепции обратного наследования. Так как на данный момент классу-ребёнку не известно откуда именно класс-родитель прочитал конкретную переменную (из файлов, из переменных окружения или из секретной директории), то настройки регистронезависимости, заданные в классе-ребёнке, не могут быть применены по отдельности к именам конкретных переменных, по этому при передаче переменных от одного обработчика к другому в данный момент применяется значение, указанное в общей переменной `case_sensitive`.
После доработки режима отладки возможно такое поведение изменится, и, при множественной вложенности моделей, при передаче переменных между обработчиками будут применяться точные настройки регистронезависимости, которые указаны в конкретном классе, к каждой переменной.

> **Заметка**: Значение, указанное в переменных `conf_case_sensitive` и `env_case_sensitive` всегда имеет приоритет над значение, указанным в переменной `case_sensitive`.

**Использование**:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
print(config.settings_config.case_sensitive)
#> False
print(config.settings_config.conf_case_sensitive)
#> False
print(config.settings_config.env_case_sensitive)
#> False


class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        case_sensitive = True,
    )


config = AppConfig()
print(config.settings_config.case_sensitive)
#> True
print(config.settings_config.conf_case_sensitive)
#> True
print(config.settings_config.env_case_sensitive)
#> True
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
case_sensitive = true
```


### ignore_missing

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

1. Задает значение для [conf_ignore_missing](#conf_ignore_missing), если сама переменная `conf_ignore_missing` не задана ни в [file_config](#file_config) ни в [model_config](#model_config).
2. Задает значение для [env_ignore_missing](#env_ignore_missing), если сама переменная `env_ignore_missing` не задана ни в [env_config](#env_config) ни в [model_config](#model_config).
3. Определяет игнорировать или нет отсутствие файлов в секретной директории [secrets_dir](#secrets_dir).

**Использование**:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        ignore_missing = False,
    )


config = AppConfig()
print(config.settings_config.ignore_missing)  # default True
#> False
print(config.settings_config.conf_ignore_missing)  # default True
#> False
print(config.settings_config.env_ignore_missing)  # default True
#> False
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
ignore_missing = false
```


### encoding

Тип: `#!python str | None`

Значение по умолчанию: `#!python None  # utf-8`

**Что делает**:

1. Задает значение для [conf_file_encoding](#conf_file_encoding), если сама переменная `conf_file_encoding` не задана ни в [file_config](#file_config) ни в [model_config](#model_config).
2. Задает значение для [env_file_encoding](#env_file_encoding), если сама переменная `env_file_encoding` не задана ни в [env_config](#env_config) ни в [model_config](#model_config).
3. Определяет кодировку при чтении файлов из секретной директории [secrets_dir](#secrets_dir).

**Использование**:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        encoding = "ISO-8859-1",
    )


config = AppConfig()
print(config.settings_config.encoding)  # default None
#> ISO-8859-1
print(config.settings_config.conf_file_encoding)  # default None
#> ISO-8859-1
print(config.settings_config.env_file_encoding)  # default None
#> ISO-8859-1
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
encoding = "utf-8"
```


### cli

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

Разрешает или запрещает чтение переменных из командной строки. Так как в большинстве случаев чтение переменных из командной строки не требуется, то по умолчание чтение отключено. При обратном наследовании НЕ наследуется, нужно включать для каждого класса отдельно, либо для всех классов сразу в файле `pyproject.toml`.

Более подробно о работе с переменными из командной строки написано [здесь](cli.md).

**Использование**:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict

class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        cli = True,
    )
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
cli = true            # (1)!
```

1. Включаем чтение переменных их командной строки для всех классов


### secrets_dir

Тип: `#!python str | None`

Значение по умолчанию: `#!python None`

**Что делает**:

Задаёт секретную директорию, откуда будут читаться значения для каждого атрибута класса. При этом имена файлов в этой директории должны соответствовать алиасам полей текущей модели. Зависимость от регистра при чтении имён файлов задаётся параметром [case_sensitive](#case_sensitive)

При обратном наследовании НЕ наследуется, нужно указывать для каждого класса отдельно, либо для всех классов сразу в файле `pyproject.toml`.

**Использование**:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict

class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        secrets_dir = "/var/run/secrets",
    )
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
secrets_dir = "/var/run/secrets"
```


### exclude_inherit_parent

Тип: `#!python list[str]`

Значение по умолчанию: `#!python []`

**Что делает**:

Общее место для указания настроек, которые нужно исключить из обратного наследования. Поддерживает все значения которые входят в [conf_exclude_inherit_parent](#conf_exclude_inherit_parent) и [env_exclude_inherit_parent](#env_exclude_inherit_parent).
При добавлении параметра в `exclude_inherit_parent`, он автоматически добавляется либо в `env_exclude_inherit_parent` либо в `conf_exclude_inherit_parent` в зависимости от того, к каким настройкам этот параметр относится.

При обратном наследовании НЕ наследуется.

**Использование**:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict

class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        exclude_inherit_parent = [
            "conf_file",
            "conf_custom_ext_handler",
            "conf_exclude_inherit_parent",
            "env_prefix",
            "env_include_inherit_parent",
        ],
    )
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
exclude_inherit_parent = ["env_prefix_as_source_mode_dir"]
```


### include_inherit_parent

Тип: `#!python list[str]`

Значение по умолчанию: `#!python []`

**Что делает**:

Общее место для указания только тех настроек, которые нужно наследовать от класса-родителя в концепции обратного наследования.
Поддерживает все значения которые входят в [conf_include_inherit_parent](#conf_include_inherit_parent) и [env_include_inherit_parent](#env_include_inherit_parent).

При добавлении параметра в `include_inherit_parent`, он автоматически добавляется либо в `env_include_inherit_parent` либо в `conf_include_inherit_parent` в зависимости от того, к каким настройкам этот параметр относится.

При обратном наследовании НЕ наследуется.

**Использование**:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict

class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        include_inherit_parent = [
            "conf_file",
            "conf_custom_ext_handler",
            "env_prefix",
            "env_file_encoding",
        ],
    )
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
include_inherit_parent = [
  "env_prefix",
  "conf_dir",
  "conf_file"
]
```


## file_config_inherit_parent

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

Включает или отключает обратное наследование всех параметров, относящихся к чтению из файлов конфигураций.
При отключении наследования все значения параметров устанавливаются по умолчанию, либо в значения, указанные в файле `pyproject.toml`

**Использование**:

```py
from arfi_settings import ArFiSettings, FileConfigDict


class Child(ArFiSettings):
    file_config_inherit_parent = False


class Parent(ArFiSettings):
    child: Child

    file_config = FileConfigDict(
        conf_dir = None,
        conf_file = "myconfig.json",
    )


config = Parent()
print(config.conf_path)
#> [PosixPath('myconfig.json')]
print(config.child.conf_path)
#> [PosixPath('config/child/config')]
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
file_config_inherit_parent = false
```


## env_config_inherit_parent

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

Включает или отключает обратное наследование всех параметров, относящихся к чтению из переменных окружения.
При отключении наследования все значения параметров устанавливаются по умолчанию, либо в значения, указанные в файле `pyproject.toml`

**Использование**:

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class Child(ArFiSettings):
    env_config_inherit_parent = False


class Parent(ArFiSettings):
    child: Child

    env_config = EnvConfigDict(
        env_file=None,
        env_prefix="APP_",
    )


config = Parent()
print(config.env_path)
#> []
print(config.env_prefix)
#> APP_
print(config.child.env_path)
#> [PosixPath('.env')]
print(config.child.env_prefix)
#> ""
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
env_config_inherit_parent = false
```


## ordered_settings

Тип: `#!python list[str]`

Значение по умолчанию: `#!python ["cli", "init_kwargs", "env", "env_file", "secrets", "conf_file"]`

**Что делает**:

Указывает порядок источников чтения настроек. Первый источник в списке наиболее приоритетный.
На самом деле в этом списке указываются имена обработчиков. Можно указать как короткое имя, как указано в значении по умолчанию, так и полное. Например:
```py
[
  "cli_ordered_settings_handler",
  "init_kwargs_ordered_settings_handler",
  "env_ordered_settings_handler",
  "env_file_ordered_settings_handler",
  "secrets_ordered_settings_handler",
  "conf_file_ordered_settings_handler",
]
```
Можно удалять, менять местами и добавлять собственные обработчики просто изменяя список.

Как создавать собственные обработчики написано [здесь](handlers.md)

**Использование**:

```py
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    ordered_settings = [
      "init_kwargs",
      "conf_file"
    ]
```

Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
ordered_settings = [
  "init_kwargs",
  "conf_file"
]
```


## ordered_settings_inherit_parent

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

Включает или отключает обратное наследование источников чтения настроек.
При отключении наследования значение параметра устанавливается по умолчанию, либо в значения, указанные в файле `pyproject.toml`

**Использование**:

```py
from arfi_settings import ArFiSettings


class Child(ArFiSettings):
    ordered_settings_inherit_parent = False


class Parent(ArFiSettings):
    child: Child

    ordered_settings = [
        "init_kwargs",
        "conf_file",
    ]


config = Parent()
print(config.ordered_settings)
#> ['init_kwargs', 'conf_file']
print(config.child.ordered_settings)
#> ['cli', 'init_kwargs', 'env', 'env_file', 'secrets', 'conf_file']
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
ordered_settings_inherit_parent = false
```

## handler_class

Тип: `#!python type(arfi_settings.ArFiHandler)`

Значение по умолчанию: `#!python arfi_settings.ArFiHandler`

**Что делает**:

Класс, который реализует механизм чтения настроек.
Можно создавать собственные классы наследуясь от `arfi_settings.ArFiHandler`.

Более подробно про обработчики написано [здесь](handlers.md)

**Использование**:

```py
from arfi_settings import ArFiSettings, ArFiHandler

class MyHandler(ArFiHandler):
    def default_main_handler(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        return data


class AppConfig(ArFiSettings):
    handler_class = MyHandler
```


## handler

Тип: `#!python str`

Значение по умолчанию: `#!python "default_main_handler"`

**Что делает**:

Это главный обработчик настроек, который запускается при инициализации класса и читает все настройки если значение параметра [read_config](#read_config) установлено в `#!python True`
По сути это название метода класса `arfi_settings.ArFiHandler`. Можно создавать собственные обработчики и назначать их каждому классу индивидуально.

Более подробно про обработчики написано [здесь](handlers.md)

**Использование**:

```txt title=".env"
PROJECT_NAME="Awesome project"
MY_PARAM="param_from_env"
```

```py
from typing import Any
from arfi_settings import ArFiSettings, ArFiHandler


class MyHandler(ArFiHandler):
    def awesome_main_handler(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        data["my_param"] = "param_from_awesome_handler"
        return data


ArFiSettings.handler_class = MyHandler


class AppSettings(ArFiSettings):
    my_param: str

    handler = "awesome_main_handler"      # (1)!


class AppConfig(ArFiSettings):
    PROJECT_NAME: str                     # (2)!
    app: AppSettings


config = AppConfig()
print(config.PROJECT_NAME)
#> Awesome project
print(config.app.my_param)
#> param_from_awesome_handler
```

1. Используется пользовательский обработчик. Нет доступа к переменным окружения
2. Используется обработчик по умолчанию


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
handler = "my_awesome_handler"
```


## handler_inherit_parent

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

Включает или отключает обратное наследование главного обработчика [handler](#handler)

**Использование**:

```py
from typing import Any
from arfi_settings import ArFiSettings, ArFiHandler


class MyHandler(ArFiHandler):
    def awesome_main_handler(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        data["my_param"] = "param_from_awesome_handler"
        return data


ArFiSettings.handler_class = MyHandler


class AppSettings(ArFiSettings):
    pass


class AppConfig(ArFiSettings):
    app: AppSettings

    handler = "awesome_main_handler"


config = AppConfig()
print(config.app.handler)
#> awesome_main_handler


class AppSettings(ArFiSettings):
    handler_inherit_parent = False


config = AppConfig()
print(config.app.handler)
#> default_main_handler
```


Файл `pyproject.toml`:

```toml title="pyproject.toml"
[tool.arfi_settings]
handler_inherit_parent = false
```


## Свойства (property)

### root_dir

Тип: `#!python Path | str | None`

Значение по умолчанию: `#!python None`

**Что делает**:

Указывает на главную директорию проекта. Автоматически определяется один раз для всего проекта. Нет возможности указать вручную.

**Принцип автоматического определения**:

Сначала происходит поиск файла `pyproject.toml` с максимальной глубиной поиска по умолчанию на 3 директории ВВЕРХ от файла, где происходит инициализация инстанса главных настроек. Если файл `pyproject.toml` найден, главной директорией проекта считается та, в которой лежит этот файл. Если файл `pyproject.toml` не найден, то главной директорией проекта считается родительская директория для [BASE_DIR](#BASE_DIR)

**Использование**:

Файл `pyproject.toml` существует

Структура проекта:
```
~/my-awesome-project
├── src
│  └── my_awesome_project
│     ├── __init__.py
│     └── main.py
└── pyproject.toml
```

```py title="~/my-awesome-project/src/my_awesome_project/main.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
print(config.root_dir)
#> /home/user/my-awesome-project
```

Файл `pyproject.toml` отсутствует

Структура проекта:
```
~/my-awesome-project
└── src
   └── my_awesome_project
      ├── __init__.py
      └── main.py
```

```py title="~/my-awesome-project/src/my_awesome_project/main.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
print(config.root_dir)
#> /home/user/my-awesome-project/src
```

### conf_path

Тип: `#!python list[Path]`

Значение по умолчанию: `#!python []`

**Что делает**:

Вычисляемое значение. На основе указанных параметров [conf_dir](#conf_dir), [mode_dir](#mode_dir) и [conf_file](#conf_file) вычисляет список путей к конфигурационным файлам для данного класса. При этом значения параметров, указанные в файле по последнему пути из этого списка всегда будут переопределять значения из предыдущих файлов.

Основной принцип построения путей:
```
conf_dir/mode_dir/conf_file
```
При сложной структуре в концепции обратного наследования пути строятся по следующему принципу:
```
conf_dir/parent_mode_dir/nested_mode_dir/source_mode_dir/conf_file
```
где:

- conf_dir - путь к директории конфигурации
- parent_mode_dir - вычисляемое значение `mode_dir` класса-родителя в концепции обратного наследования
- nested_mode_dir - точное значение `mode_dir` параметра класса, от которого наследуется текущий класс, в концепции классического наследования
- source_mode_dir - точное значение `mode_dir` параметра исходного класса
- conf_file - значение `conf_file`, указанное в исходном классе, т.е. имя файла конфигурации

**Использование**:

```py
from arfi_settings import ArFiSettings


class NestedConfig(ArFiSettings):
    mode_dir = "nested_mode_dir"


class ChildConfig(NestedConfig):
    mode_dir = "source_mode_dir"


class ParentConfig(ArFiSettings):
    mode_dir = "parent_mode_dir"
    child: ChildConfig


config = ParentConfig()
print(config.conf_path)
#> [PosixPath('config/parent_mode_dir/config')]
print(config.child.conf_path)
#> [PosixPath('config/parent_mode_dir/nested_mode_dir/source_mode_dir/config')]
```


### env_path

Тип: `#!python list[Path]`

Значение по умолчанию: `#!python []`

**Что делает**:

Вычисляемое значение. На основе заданного параметра [env_file](#env_file) вычисляет список путей к файлам с переменными окружения.

Под капотом, для каждого переданного файла, поиск происходит по следующим правилам, если передан относительный путь до файла:

- Сначала файл ищется в главной директории проекта [root_dir](#root_dir). Если файл найден, то поиск завершается.
- Если файл не найден в главной директории, то происходит поиск файла в базовой директории проекта [BASE_DIR](#BASE_DIR)

> **Заметка**: При включённом режиме отладки [arfi_debug](../about/debug_mode.md) можно увидеть абсолютные пути до файлов в результатах вывода отладочной информации..

**Использование**:

```py
from arfi_settings import ArFiSettings, EnvConfigDict


class AppConfig(ArFiSettings):
    env_config = EnvConfigDict(
        env_file = [
            ".env",
            ".env.prod",
        ],
    )


config = AppConfig()
print(config.env_path)
#> [PosixPath('.env'), PosixPath('.env.prod')]
```

### mode_dir_path

Тип: `#!python Path`

Значение по умолчанию: `#!python Path("")`

**Что делает**:

Вычисляемое значение. Возвращает путь до поддиректории, в которой будет производиться поиск файлов конфигурации для данного класса.

На основе этого пути строится полный путь до файлов конфигурации текущего класса по следующему принципу:

[BASE_DIR](#BASE_DIR) / [conf_dir](#conf_dir) / [mode_dir_path](#mode_dir_path) / [conf_file](#conf_file)[.[conf_ext](#conf_ext)]

> **Заметка**: В начало пути добавляется `BASE_DIR /` только в том случае, если `conf_dir` не является абсолютным путём.

**Использование**:

```py
from arfi_settings import ArFiSettings


class Base(ArFiSettings):
    mode_dir = "base"


class BaseConfig(Base):
    mode_dir = "base_config"


class SubAppSettings(BaseConfig):
    pass


class AppSettings(ArFiSettings):
    sub_app: SubAppSettings


class AppConfig(ArFiSettings):
    mode_dir = "dev"

    app: AppSettings


config = AppConfig()
print(repr(config.app.sub_app.mode_dir_path))
#> PosixPath('dev/app/base/base_config/sub_app')
print(config.app.sub_app.conf_path)
#> [PosixPath('config/dev/app/base/base_config/sub_app/config')]
```


### computed_mode_dir

Тип: `#!python str`

Значение по умолчанию: `#!python ""`

**Что делает**:

Вычисляемое значение. Возвращает название поддиректории, в которой будет производиться поиск файлов конфигурации для данного класса.

**Использование**:

```py
from arfi_settings import ArFiSettings


class Base(ArFiSettings):
    mode_dir = "base"


class BaseConfig(Base):
    mode_dir = "base_config"


class SubAppSettings(BaseConfig):
    pass


class AppSettings(ArFiSettings):
    sub_app: SubAppSettings


class AppConfig(ArFiSettings):
    mode_dir = "dev"

    app: AppSettings


config = AppConfig()
print(config.app.sub_app.computed_mode_dir)
#> dev/app/base/base_config/sub_app
print(config.app.sub_app.conf_path)
#> [PosixPath('config/dev/app/base/base_config/sub_app/config')]
```


### parent_mode_dir

Тип: `#!python str`

Значение по умолчанию: `#!python ""`

**Что делает**:

Вычисляемое значение. Возвращает название поддиректории класса-родителя в концепции обратного наследования.

**Использование**:

```py
from arfi_settings import ArFiSettings


class Base(ArFiSettings):
    mode_dir = "base"


class BaseConfig(Base):
    mode_dir = "base_config"


class SubAppSettings(BaseConfig):
    pass


class AppSettings(ArFiSettings):
    sub_app: SubAppSettings


class AppConfig(ArFiSettings):
    mode_dir = "dev"

    app: AppSettings


config = AppConfig()
print(config.app.sub_app.computed_mode_dir)
#> dev/app/base/base_config/sub_app
print(config.app.sub_app.parent_mode_dir)
#> dev/app
```

### nested_mode_dir

Тип: `#!python str`

Значение по умолчанию: `#!python ""`

**Что делает**:

Вычисляемое значение. Возвращает название поддиректории класса, от которого наследуется в классической концепции наследования.

**Использование**:

```py
from arfi_settings import ArFiSettings


class Base(ArFiSettings):
    mode_dir = "base"


class BaseConfig(Base):
    mode_dir = "base_config"


class SubAppSettings(BaseConfig):
    pass


class AppSettings(ArFiSettings):
    sub_app: SubAppSettings


class AppConfig(ArFiSettings):
    mode_dir = "dev"

    app: AppSettings


config = AppConfig()
print(config.app.sub_app.computed_mode_dir)
#> dev/app/base/base_config/sub_app
print(config.app.sub_app.nested_mode_dir)
#> base/base_config
```

### source_mode_dir

Тип: `#!python str`

Значение по умолчанию: `#!python ""`

**Что делает**:

Вычисляемое значение. Возвращает название собственной поддиректории.

**Использование**:

```py
from arfi_settings import ArFiSettings


class Base(ArFiSettings):
    mode_dir = "base"


class BaseConfig(Base):
    mode_dir = "base_config"


class SubAppSettings(BaseConfig):
    pass


class AppSettings(ArFiSettings):
    sub_app: SubAppSettings


class AppConfig(ArFiSettings):
    mode_dir = "dev"

    app: AppSettings


config = AppConfig()
print(config.app.sub_app.computed_mode_dir)
#> dev/app/base/base_config/sub_app
print(config.app.sub_app.source_mode_dir)
#> sub_app
```

### pyproject_toml_path

Тип: `#!python str | Path | None`

Значение по умолчанию: `#!python None`

**Что делает**:

Вычисляемое значение. Возвращает путь файла `pyproject.toml`.

**Использование**:

```py title="~/my_awesome_project/main.py"
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
print(config.pyproject_toml_path)   # (1)!
#> /home/user/my_awesome_project/pyproject.toml
```

1. При условии, что файл `pyproject.toml` существует в корне проекта.


### inherited_params

Тип: `#!pythonn list[str]`

Значение по умолчанию: `#!python []`

**Что делает**:

Отображает все собственные настройки, которые наследуются от класса-родителя в концепции обратного наследования.

**Использование**:

Все настройки, которые наследуются по умолчанию из `file_config` и `env_config` класса-родителя в концепции обратного наследования.
```py
import json
from arfi_settings import ArFiSettings


class AppSettings(ArFiSettings):
    pass


class AppConfig(ArFiSettings):
    app: AppSettings


config = AppConfig()
print(json.dumps(config.app.inherited_params, indent=4))
"""
[
    "conf_include_inherit_parent",
    "conf_exclude_inherit_parent",
    "env_include_inherit_parent",
    "env_exclude_inherit_parent",
    "conf_file",
    "conf_dir",
    "conf_ext",
    "conf_file_encoding",
    "conf_case_sensitive",
    "conf_ignore_missing",
    "conf_custom_ext_handler",
    "env_file",
    "env_prefix",
    "env_prefix_as_mode_dir",
    "env_prefix_as_nested_mode_dir",
    "env_prefix_as_source_mode_dir",
    "env_file_encoding",
    "env_case_sensitive",
    "env_nested_delimiter",
    "env_ignore_missing"
]
"""
```

Отключаем наследование части настроек:

```py
import json
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppSettings(ArFiSettings):
    model_config = SettingsConfigDict(
        include_inherit_parent=[
            "conf_file",
            "env_prefix",
        ],
        exclude_inherit_parent=[
            "conf_include_inherit_parent",
            "conf_exclude_inherit_parent",
            "env_include_inherit_parent",
            "env_exclude_inherit_parent",
        ],
    )


class AppConfig(ArFiSettings):
    app: AppSettings


config = AppConfig()
print(json.dumps(config.app.inherited_params, indent=4))
"""
[
    "conf_file",
    "env_prefix",
]
"""
```


### settings_config

Тип: `#!python pidantic.BaseModel`

Значение по умолчанию: `#!python arfi_settings.schemes.SettingsConfigSchema()`

**Что делает**:

Агрегирует все заданные собственные настройки, которые потом использует обработчик при чтении конфигурации.

**Использование**:

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        conf_dir=None,
        conf_file=[
            "appconfig.toml",
            "~/.config/myapp/config.toml",
            "/var/run/secrets/config.toml",
        ],
        env_file="/var/run/secrets/.my_environment",
        env_prefix="APP_",
        secrets_dir="/var/run/secrets",
        cli=True,
    )


config = AppConfig()
print(config.settings_config.model_dump_json(indent=4))
"""
{
    "env_file": "/var/run/secrets/.my_environment",
    "env_prefix": "APP_",
    "env_prefix_as_mode_dir": false,
    "env_prefix_as_nested_mode_dir": false,
    "env_prefix_as_source_mode_dir": false,
    "env_file_encoding": null,
    "env_case_sensitive": false,
    "env_nested_delimiter": "",
    "env_ignore_missing": true,
    "env_include_inherit_parent": [],
    "env_exclude_inherit_parent": [],
    "conf_file": "['appconfig.toml', '~/.config/myapp/config.toml', '/var/run/secrets/config.toml']",
    "conf_dir": null,
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
    "cli": true,
    "secrets_dir": "/var/run/secrets",
    "conf_path": [
        "appconfig.toml",
        "/home/user/.config/myapp/config.toml",
        "/var/run/secrets/config.toml"
    ],
    "env_path": [
        "/var/run/secrets/.my_environment"
    ],
    "include_inherit_parent": [],
    "exclude_inherit_parent": []
}
"""
```
