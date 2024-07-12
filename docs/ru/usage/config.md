# Основные настройки

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

Тип: `#!python arfi_settings.types.FileConfig`
Значение по умолчанию: `#!python arfi_settings.schemes.FileConfigSchema().conf_dict()`

**Что делает**:

Настройки, которые описывают правила чтения из файлов конфигурации.

**Использование**:

```py
from arfi_settings import ArFiSettings, FileConfig

class AppConfig(ArFiSettings):
    file_config = FileConfig(
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

**Использование**:

```py
from arfi_settings import ArFiSettings, FileConfigDict

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


### conf_case_sensitive

Тип: `#!python bool`
Значение по умолчанию: `#!python False`

**Что делает**:

По умолчанию при чтении из файлов конфигурации параметры читаются как регистро-независимые. Но сначала ищется точное совпадение. Если точное совпадение не найдено, то возвращается найденное значение в нижнем регистре, если и оно не найдено, то возвращается первое найденное значение, приведённое к нижнему регистру.

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


### conf_exclude_inherit_parent

Тип: `#!python list[str]`
Значение по умолчанию: `#!python []`

**Что делает**:

В концепции обратного наследования запрещает наследование определённых собственных настроек от класса-родителя
Применяется только для чтения файлов.

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


### conf_include_inherit_parent

Тип: `#!python list[str]`
Значение по умолчанию: `#!python []`

**Что делает**:

В концепции обратного наследования запрещает наследование от класса-родителя всех собственных настроек, кроме указанных
Применяется только для чтения файлов.

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
