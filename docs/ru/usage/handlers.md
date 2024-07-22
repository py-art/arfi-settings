# Обработчики


## Описание

В момент инициализации, перед валидацией данных конфигурации приложения с помощью `pydantic`, эти сами данные нужно как-то и откуда-то получить. Вот за извлечение этих самых данных и их предварительную сортировку по приоритету источника и отвечают обработчики.

Обработчики отвечают именно за обработку полученной информации из источников конфигурации. А вот чтоб её получить, обработчики сначала обращаются к [Читателям](readers.md), которые, как ни странно, читают эту информацию из различных источников. Обработчик передаёт читателю источник конфигурации и ряд дополнительных параметров, а читатель возвращает или не возвращает найденную конфигурацию.

Для каждого класса настроек (подкласса `arfi_settings.ArFiSettings`) указывается свой собственный класс-обработчик с помощью атрибута [handler_class](config.md#handler_class). По умолчанию классом-обработчиком для всех настроек является `arfi_settings.ArFiHandler`.

Можно создать свой собственные класс-обработчик и назначить его как отдельному классу настроек, так и всем классам настроек сразу. Более подробно об этом написано в разделе [Создание собственного класса обработчика](#_3)

Помимо класса-обработчика, в самом классе настроек с помощью атрибута [handler](config.md#handler) можно указать свой собственный, индивидуальный для данного класса, [Главный обработчик](#_7).

Сами обработчики реализованы в виде методов класса `arfi_settings.ArFiHandler`.

На данный момент обработчики делятся на несколько типов:

1. [Главный обработчик](#_7)
2. [Обработчики источников](#_10)
3. [Обработчики файлов конфигурации](#_13)
4. [Обработчики переменных окружения](#_16)
5. [Обработчик переменных из командной строки](#_19)
6. [Обработчик переменных из секретной директории](#_22)
7. [Обработчик переменных инициализации](#_25)

В дальнейшем, по мере добавления источников чтения конфигурации, этот список может быть расширен.


## Создание собственного класса обработчика

Создание собственного класса-обработчика целесообразно в том случае, если вам не хватает функционала по умолчания. Например, если нужно добавить новый источник конфигурации или добавить обработчик расширения файла или чтоб переопределить существующий обработчик.

> **Заметка**: Класс-обработчик НЕ наследуется в концепции обратного наследования, а назначается каждому классу настроек индивидуально, либо всем классам настроек глобально.

### Создание

При создании собственного класса-обработчика он может наследоваться от 2-х классов - от `arfi_settings.ArFiBaseHandler` и от `arfi_settings.ArFiHandler`.

- Наследование от `arfi_settings.ArFiHandler`

Это предпочтительный способ создания, так как в большинстве случаев не требуется переопределять [Главный обработчик](#главный-обработчик)

```py
from typing import Any
from arfi_settings import ArFiHandler


class MyHandler(ArFiHandler):
    """My awesome handler."""

    def awesome_main_handler(self) -> dict[str, Any]:
        """Additional main handler."""
        data: dict[str, Any] = {}
        # Do something ...
        return data

    def url_ordered_settings_handler(self) -> dict[str, Any]:
        """Read the configuration at the URL."""
        data: dict[str, Any] = {}
        # Do something ...
        return data
```

- Наследование от `arfi_settings.ArFiBaseHandler`

При наследовании от этого класса обязательно должен быть определён метод `default_main_handler` - [Главный обработчик](#главный-обработчик)

```py
from typing import Any
from arfi_settings import ArFiBaseHandler


class MyHandler(ArFiBaseHandler):
    def default_main_handler(self):
        data: dict[str, Any] = {}
        # Do something ...
        return data
```


### Назначение классу

Для каждого класса настроек можно назначить собственный класс-обработчик с помощью параметра [handler_class](config.md#handler_class):

```py
from typing import Any
from arfi_settings import ArFiSettings, ArFiHandler


class MyHandler(ArFiHandler):
    def url_ordered_settings_handler(self) -> dict[str, Any]:
        """Read the configuration at the URL."""
        data: dict[str, Any] = {}
        # Do something ...
        return data


class AppSettings(ArFiSettings):
    handler_class = MyHandler
    ordered_settings = [
        "url",
        "init_kwargs",
    ]


class AppConfig(ArFiSettings):
    app: AppSettings


config = AppConfig()
print(config.handler_class.__name__)
#> ArFiHandler
print(config.app.handler_class.__name__)
#> MyHandler
```


### Назначение глобально, всем классам

```py
from typing import Any
from arfi_settings import ArFiSettings, ArFiHandler


class MyHandler(ArFiHandler):
    def url_ordered_settings_handler(self) -> dict[str, Any]:
        """Read the configuration at the URL."""
        data: dict[str, Any] = {}
        # Do something ...
        return data


ArFiSettings.handler_class = MyHandler


class AppSettings(ArFiSettings):
    ordered_settings = [
        "url",
        "init_kwargs",
    ]


class AppConfig(ArFiSettings):
    app: AppSettings


config = AppConfig()
print(config.handler_class.__name__)
#> MyHandler
print(config.app.handler_class.__name__)
#> MyHandler
```


## Главный обработчик

Главный обработчик - это метод класса `arfi_settings.ArFiHandler`. Имя метода обязательно должно заканчиваться на `_main_handler`.

Этот обработчик запускается в момент инициализации класса настроек. По умолчанию в нём задаются источники и порядок чтения конфигурации, а так же реализован механизм чтения и предварительной обработки прочитанной конфигурации. Далее, полученные результаты передаются в саму модель `pydantic` для валидации значений.

В классе настроек главный обработчик задаётся параметром [handler](config.md#handler) и по умолчанию называется `default_main_handler`.


### По умолчанию

```py
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    handler = "default_main_handler"  # (1)!
```

1. Значение по умолчанию


### Собственный обработчик

Переопределение главного обработчика глобально

```py
from typing import Any
from arfi_settings import (
    ArFiSettings,
    ArFiHandler as ArFiHandlerSource,
)


class ArFiHandler(ArFiHandlerSource):
    def default_main_handler(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        data["test_param"] = "my_constant_value"
        return data


ArFiSettings.handler_class = ArFiHandler


class AppConfig(ArFiSettings):
    test_param: str = "default_value"

    ordered_settings = ["init_kwargs"]  # (1)!


data = {"test_param": "initial_value"}
config = AppConfig(**data)
print(config.test_param)
#> my_constant_value
```

1. НЕ влияет абсолютно ни на что, так как в главном обработчике не реализовано чтение конфигурации из источников, переданных в параметре `ordered_settings`


Создание собственного главного обработчика и назначение его определённому классу настроек

```txt title=".env"
TEST_PARAM=value_from_env_file
```

```py title="settings.py"
from typing import Any
from arfi_settings import (
    ArFiSettings,
    ArFiHandler as ArFiHandlerSource,
)


class ArFiHandler(ArFiHandlerSource):
    def awesome_main_handler(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        data["test_param"] = "my_constant_value_from_my_handler"
        return data


ArFiSettings.handler_class = ArFiHandler


class AppSettings(ArFiSettings):
    test_param: str

    handler = "awesome_main_handler"


class AppConfig(ArFiSettings):
    app: AppSettings
    test_param: str


config = AppConfig()
print(config.test_param)
#> value_from_env_file
print(config.app.test_param)
#> my_constant_value_from_my_handler
```


## Обработчики источников

Обработчики источников - это методы класса `arfi_settings.ArFiHandler`. Имя метода обязательно должно заканчиваться на `_ordered_settings_handler`. Для удобства в классе настроек имена обработчиков можно задавать короткими именами, без суффикса `_ordered_settings_handler`.

В каждом обработчике из источников по умолчанию реализован механизм чтения и предварительной обработки конфигурации.

Порядок чтения источников задан константой `arfi_settings.constants.ORDERED_SETTINGS` в порядке убывания приоритета:
```py title="arfi_settings/constants.py"
ORDERED_SETTINGS = [
    "cli",
    "init_kwargs",
    "env",
    "env_file",
    "secrets",
    "conf_file",
]
```

Для каждого класса настроек можно задать свой собственный порядок чтения настроек, просто переопределив список в параметре [ordered_settings](config.md#ordered_settings):

```py
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    ordered_settings = ["conf_file", "init_kwargs"]
```

> **Важно**: Чтоб настройки, прочитанные классом-родителем, в концепции обратного наследования, передавались детям в параметре [ordered_settings](config.md#ordered_settings) обязательно должен присутствовать источник `init_kwargs`. Если `init_kwargs` отсутствует в источниках, то конфигурация будет прочитана только для настроек, указанных в текущем классе, а все настройки, прочитанные родителями этого класса будут игнорироваться. При этом будет выведено предупреждение о том, что предыдущие настройки не будут учтены.


### По умолчанию

По умолчанию для удобства используются короткие имена обработчиков:

```py
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    ordered_settings = [
        "cli",
        "init_kwargs",
        "env",
        "env_file",
        "secrets",
        "conf_file",
    ]
```

То же самое, только используя полные имена обработчиков:

```py
from arfi_settings import ArFiSettings


class AppConfig(ArFiSettings):
    ordered_settings = [
        "cli_ordered_settings_handler",
        "init_kwargs_ordered_settings_handler",
        "env_ordered_settings_handler",
        "env_file_ordered_settings_handler",
        "secrets_ordered_settings_handler",
        "conf_file_ordered_settings_handler",
    ]
```


### Собственный обработчик

```py
from typing import Any
from arfi_settings import ArFiSettings, ArFiHandler


class MyHandler(ArFiHandler):
    def awesome_ordered_settings_handler(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        data["test_param"] = "my_constant_value_from_ordered_settings_handler"
        return data


class AppConfig(ArFiSettings):
    test_param: str

    handler_class = MyHandler
    ordered_settings = [
        "awesome",
        "init_kwargs",
    ]


config = AppConfig()
print(config.test_param)
#> my_constant_value_from_ordered_settings_handler
```


## Обработчики файлов конфигурации
Обработчики файлов конфигурации - это методы класса `arfi_settings.ArFiHandler`. Имя метода обязательно должно заканчиваться на `_ext_handler`. По умолчанию каждый обработчик начинается с названия расширения файла, для чтения которого он предназначен. Например, обработчик `json_ext_handler` отвечает за чтение и обработку файлов с расширением `.json`.

Для удобства использования в классе настроек в параметре [conf_ext](config.md#conf_ext) обработчики можно указывать короткими именами по названию расширения.

Для чтения и обработки файлов без расширения нужно в обязательном порядке назначить обработчик для таких файлов параметром [conf_custom_ext_handler](config.md#conf_custom_ext_handler).

По умолчанию поддерживается чтение и обработка нескольких расширений файлов, указанных в константе `arfi_settings.constants.CONFIG_EXT_DEFAULT`:

```py title="arfi_settings/constants.py"
CONFIG_EXT_DEFAULT = [
    "toml",
    "yaml",
    "yml",
    "json",
]
```

В классе настроек порядок поиска файлов конфигурации по расширению указывается в порядке приоритета параметром [conf_ext](config.md#conf_ext). Обработчики можно указывать как строкой, через запятую, так и списком строк.

```py
from arfi_settings import ArFiSettings, FileConfigDict


class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_ext="json",
    )


config = AppConfig()
print(config.settings_config.conf_ext)
```


### По умолчанию

Ниже приведено 2 равнозначных способа указания обработчиков файлов:

- Первый

```py
class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_ext="toml, yaml, yml, json",
    )
```

- Второй

```py
class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_ext=[
            "toml",
            "yaml",
            "yml",
            "json",
        ],
    )
```


### Собственный обработчик

Собственные обработчики предназначены для чтения и обработки файлов с расширениями, которых нет в списке по умолчанию.

Например нам нужно получить конфигурацию из файла с расширением `.cfg`. Для этого нам нужно создать читатель для файлов с расширением `.cfg`, потом создать свой обработчик и указать его в классе настроек.

Более подробно о создании собственных читателей написано [здесь](readers.md).

Для примера создадим 2 файла - `config.toml` и `config.cfg`, но порядок чтения настроек зададим параметром [conf_ext](config.md#conf_ext):

```toml title="config/config.toml"
test_param = "paramFromTomlFile"
```

```txt title="config/config.cfg"
MyAwesomeTestParam paramFromCfgFile
```

```py
import re
from typing import Any

from arfi_settings import (
    ArFiHandler,
    ArFiReader,
    ArFiSettings,
    ArFiSettingsError,
    FileConfigDict,
)
from arfi_settings.types import PathType


class MyReader(ArFiReader):
    """My awesome reader."""

    def cfg_reader(self) -> dict[str, Any]:
        """Reads settings from .cfg file."""

        data: dict[str, Any] = {}

        try:
            with open(self.file_path, encoding=self.file_encoding) as file:
                data_from_file = file.read()
        except FileNotFoundError as e:
            if self.ignore_missing:
                return {}
            raise ArFiSettingsError(f"File not found: `{self.file_path.resolve().as_posix()}`") from e

        param_from_cfg_file = re.search("^MyAwesomeTestParam (.+)", data_from_file)
        if param_from_cfg_file is not None:
            param_from_cfg_file = param_from_cfg_file.group(1).strip()
        else:
            param_from_cfg_file = ""
        data["test_param"] = param_from_cfg_file
        return data


class MyHandler(ArFiHandler):
    """My awesome handler."""

    reader_class = MyReader   # (1)!

    def cfg_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        """Handles settings from .cfg file."""

        reader = self.reader_class(
            file_path=file_path,
            file_encoding=self.config.conf_file_encoding,
            ignore_missing=self.config.conf_ignore_missing,
        )
        data = reader.read()
        data["__case_sensitive"] = self.config.conf_case_sensitive
        return data


class AppConfig(ArFiSettings):
    test_param: str

    handler_class = MyHandler   # (2)!
    file_config = FileConfigDict(
        conf_ext=[
            "cfg",              # (3)!
            "toml",
        ],
    )


config = AppConfig()
print(config.test_param)
#> paramFromCfgFile
```

1. Задаём обработчику собственный класс-читатель
2. Задаем класс-обработчик
3. Определяем порядок чтения расширений файлов. Файлы с расширением `.cfg` будут иметь приоритет над файлами с расширением `.toml`

Перед возвратом словаря из обработчика `cfg_ext_handler` нужно добавить в этот словарь параметр `__case_sensitive` и передать туда нужное значение. В примере выше `#!python self.config.conf_case_sensitive` - это значение в классе `AppConfig`, указанное параметром [conf_case_sensitive](config.md#conf_case_sensitive).
Если явно не передать параметр `__case_sensitive` в словарь, то значение будет взято из общего параметра [case_sensitive](config.md#case_sensitive) из самого класса настроек `AppConfig`


## Обработчики переменных окружения

Для переменных окружения существует 2 обработчика - `env_ordered_settings_handler` и `env_file_ordered_settings_handler`.
Первый читает и обрабатывает значения непосредственно из переменных окружения, а второй - из файлов с переменными окружения, которые задаются параметром [env_file](config.md#env_file).

Оба обработчика можно указывать короткими именами, так как они являются `Обработчиками источников`
### По умолчанию

```py
from arfi_settings import ArFiSettings

class AppConfig(ArFiSettings):
    ordered_settings = [
        "env",
        "env_file",
    ]
```
### Собственный обработчик

Создание собственных обработчиков для чтения переменных окружения на данный момент не предусмотрено.


## Обработчик переменных из командной строки

Обработчик переменных из командной строки реализован в виде метода `cli_ordered_settings_handler` класса `arfi_settings.ArFiHandler`.

По умолчанию переменные, указанные в командной строке являются самыми приоритетными. Это поведение можно изменить с помощью параметра [ordered_settings](config.md#ordered_settings).

Так же по умолчанию чтение из командной строки отключено. Чтоб включить чтение нужно выполнить 2 условия:

- Определить читатель. Подробнее об этом написано [здесь](cli.md)
- Установить значение параметра [cli](config.md#cli) в `#!python True`.


### По умолчанию

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    ordered_settings = [
        "cli",
    ]
    model_config = SettingsConfigDict(
      cli=False,
    )
config = AppConfig()
print(config.settings_config.cli)
#> False
```


### Собственный обработчик

Создание собственных обработчиков для чтения переменных из командной строки на данный момент не предусмотрено.


## Обработчик переменных из секретной директории

Обработчик переменных из секретной директории реализован в виде метода `secrets_ordered_settings_handler` класса `arfi_settings.ArFiHandler`.

Чтобы читать настройки из секретной директории необходимо указать эту секретную директорию параметром [secrets_dir](config.md#secrets_dir) и указать приоритет параметром [ordered_settings](config.md#ordered_settings).


### По умолчанию

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    ordered_settings = [
        "secrets",
    ]
    model_config = SettingsConfigDict(
        secrets_dir=None,
    )


config = AppConfig()
print(config.settings_config.secrets_dir)
#> None
```


### Собственный обработчик

Создание собственных обработчиков для чтения переменных из секретной директории на данный момент не предусмотрено.


## Обработчик переменных инициализации

Обработчик переменных инициализации реализован в виде метода `init_kwargs_ordered_settings_handler` класса `arfi_settings.ArFiHandler`.

Для этого обработчика предусмотрено только задание приоритета или отключение чтения с помощью параметра [ordered_settings](config.md#ordered_settings).

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppConfig(ArFiSettings):
    ordered_settings = [
        "init_kwargs",
    ]
```
