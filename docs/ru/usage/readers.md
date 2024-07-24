# Читатели

## Описание

Перед обработкой и валидацией значений сначала нужно конфигурацию приложения прочитать. За это и отвечают читатели.

Все читатели реализованы в виде методов класса `arfi_settings.ArFiReader`. Сам класс-читатель, по умолчанию `ArFiReader`, назначается каждому [классу-обработчику](handlers.md) `ArFiHandler` отдельно с помощью параметра `reader_class`.

Есть возможность создавать собственные читатели (методы класса `ArFiReader`), при этом должны соблюдаться несколько правил

- имя читателя должно заканчиваться на `_reader`
- любой читатель должен возвращать словарь типа `#!python dict[str, Any]`

Механизм работы реализован следующим образом:

- Обработчик инициализирует инстанс класса `#!python reader = ArFiReader(...)` с нужными [параметрами](#_7) инициализации
- Обработчик запускает [Главный читатель](#_8), метод `read`, для получения данных `#!python data = reader.read()`

На данный момент читатели делятся на несколько типов:

- [Главный читатель](#_8)
- [Читатели файлов конфигурации]()
- [Читатели переменных окружения]()
- [Читатель секретной директории]()
- [Читатель переменных командной строки]()

В дальнейшем, по мере добавления источников чтения конфигурации, этот список может быть расширен.


## Создание собственного класса читателя

Для расширение источников чтения конфигурации необходимо создавать свой собственный класс-читатель или расширять функционал существующего.
### Создание

Собственный класс-читатель можно создать 2-мя способами:

- Наследуясь от `arfi_settings.ArFiReader`. Это предпочтительный способ.

```py
from arfi_settings import ArFiReader

class MyReader(ArFiReader):
    """My awesome reader."""
```

- Наследуясь от `arfi_settings.ArFiBaseReader`.

При создании класса с помощью этого способа в обязательном порядке нужно определить метод `read` - Главный читатель.
Данный способ не рекомендуется, так как реализованные по умолчанию механизмы позволяют не переопределять Главный читатель при создании собственных.

```py
from typing import Any
from arfi_settings import ArFiBaseReader


class MyReader(ArFiBaseReader):
    """My awesome reader."""

    def read(self) -> dict[str, Any]:
        """Main reader."""
        data: dict[str, Any] = {}
        # Do something ...
        return data
```


### Назначение обработчику

```py
from typing import Any
from arfi_settings import ArFiHandler, ArFiReader, ArFiSettings


class MyReader(ArFiReader):
    """My awesome reader."""
    def awesome_reader(self) -> dict[str, Any]:
        """Custom reader."""
        data: dict[str, Any] = {}
        # Do something ...
        return data


class MyHandler(ArFiHandler):
    """My awesome handler."""
    reader_class = MyReader


class AppConfig(ArFiSettings):
    handler_class = MyHandler


config = AppConfig()
```

### Назначение глобально, всем обработчикам

```py
from typing import Any
from arfi_settings import ArFiHandler, ArFiReader, ArFiSettings


class MyReader(ArFiReader):
    """My awesome reader."""
    def awesome_reader(self) -> dict[str, Any]:
        """Custom reader."""
        data: dict[str, Any] = {}
        # Do something ...
        return data


ArFiHandler.reader_class = MyReader


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```


## Параметры инициализации

Параметры, переданные при инициализации класса-читателя влияют на смену источников чтения конфигурации в Главном читателе - методе `read()`.
### reader

Тип: `#!python str`

Значение по умолчанию: `#!python ""`

**Что делает**:

По сути это имя читателя, который нужно принудительно запустить. Для удобства можно передавать имя без суффикса `_reader`, но при создании самого читателя имя обязательно должно заканчиваться на `_reader`.

Если в обработчике при инициализации читателя передан этот параметр, то [Главный читатель](#_8) запустит именно переданный читатель, игнорируя все остальные параметры, такие как [is_env](#is_env), [is_cli](#is_cli) и т.п.

**Использование**:

```py
from typing import Any
from arfi_settings import ArFiHandler, ArFiReader, ArFiSettings


class MyReader(ArFiReader):
    def my_awesome_reader(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        data["test_param"] = "param_from_awesome_reader"
        return data


class MyHandler(ArFiHandler):
    reader_class = MyReader

    def my_awesome_handler(self) -> dict[str, Any]:
        reader = self.reader_class(reader="my_awesome")
        data = reader.read()
        return data

    def custom_ordered_settings_handler(self) -> dict[str, Any]:
        return self.my_awesome_handler()


class AppConfig(ArFiSettings):
    test_param: str

    handler_class = MyHandler
    ordered_settings = [
        "custom",
        "init_kwargs",
    ]


config = AppConfig()
print(config.test_param)
#> param_from_awesome_reader
```

### file_path

Тип: `#!python str | Path | None`

Значение по умолчанию: `#!python None`

**Что делает**:

Если читатель должен читать конфигурацию из файла, то сюда передаётся путь до этого файла.

Путь может быть только один. Если нужно читать из нескольких файлов, то этот механизм должен быть реализован в обработчике.

Если передан файл с расширением и при этом установлен параметр `#!python is_env_file=False` (по умолчанию), то будет произведён поиск необходимого читателя по имени этого расширения.
Например передан файл `appconfig.ini`. В этом случае производится поиск читателя с именем `ini_reader`
Если нужный читатель (метод) не определён в классе-читателе, то будет вызвано исключение.

Если передан файл без расширения, то обязательно должен быть передан читатель в параметре [reader](#reader):

```py
reader = ArFiReader(file_path="config/appconfig", reader="yaml")
data = reader.read()
```

Путь может быть как относительным, так и абсолютным.

Если передан относительный путь, то для файлов конфигурации и файлов с переменными окружения (если параметр [is_env_file](#is_env_file) установлен в значение `True`) механизм построения абсолютного пути отличается:

- Файл конфигурации - `#!python is_env_file=False`
```py
reader = ArFiReader(file_path="config.yml")
```

В начало пути подставляется предварительно найденное значение [BASE_DIR](config.md#BASE_DIR) и путь строится следующим образом:

```
BASE_DIR/config.yml
```

- Файл переменных окружения - `#!python is_env_file=True`

```py
reader = ArFiReader(file_path=".env", is_env_file=True)
```

Поиск файлов с переменными окружения сначала производится в [root_dir](config.md#root_dir) и затем в [BASE_DIR](config.md#BASE_DIR).

То есть сначала файл ищется по пути:

```
root_dir/.env
```

Если файл не найден, то файл ищется по пути:

```
BASE_DIR/.env
```


### file_encoding

Тип: `#!python str | None`

Значение по умолчанию: `#!python None  # utf-8`

**Что делает**:

По умолчанию все файлы читаются в кодировке `utf-8`. Если кодировка нужного файла отличается от значения по умолчанию, то этим параметром можно указать нужную:

```py
reader = ArFiReader(file_path="config/config.toml", file_encoding="cp1251")
```


### is_env_file

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

По умолчанию при инициализации класса-читателя все файлы считаются файлами конфигурации. Чтоб указать, что файл содержит переменные окружения нужно установить значение этого параметра в `True`.

Например:

```py
reader = ArFiReader(file_path=".env.prod", is_env_file=True)
```


### is_env

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

Передав параметр `is_env=True` мы говорим Главному читателю, что нужно читать параметры и их значения из переменных окружения.

```py
reader = ArFiReader(is_env=True)
data = reader.read()
```


### is_cli

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

Передав параметр `is_cli=True` мы говорим Главному читателю, что нужно читать параметры и их значения из командной строки.

> **Заметка**: Пока в классе-читателе не задан собственный читатель, [Читатель переменных командной строки](#_13) всегда возвращает пустой словарь. О том как задать собственный читатель более подробно написано [здесь](cli.md)

```py
reader = ArFiReader(is_cli=True)
data = reader.read()
```

### is_secret_file

Тип: `#!python bool`

Значение по умолчанию: `#!python False`

**Что делает**:

Передав параметр `is_secret_file=True` мы говорим Главному читателю, что нужно читать параметр и его значение из файла, расположенного в секретной директории.

```py
reader = ArFiReader(file_path="secret/my_secret_param", is_secret_file=True)
```


### ignore_missing

Тип: `#!python bool`

Значение по умолчанию: `#!python True`

**Что делает**:

Значение этого параметра, по умолчанию установленное в `True`, говорит читателю, что нужно или не нужно поднимать ошибку, если переданный для чтения файл отсутствует.
Если файл отсутствует, то Главный читатель возвращает пустой словарь или возбуждается исключение.

Распространяется только на чтение файлов, таких как файлы конфигурации, файлы с переменными окружения или файлы в секретной директории.

```py
reader = ArFiReader(file_path="config/NO_EXIST_FILE.toml", ignore_missing=True)
data = reader.read()
print(data)
#> {}
```


## Главный читатель

Реализован в виде метода `read` класса `arfi_settings.ArFiReader`. Именно он запускается любым обработчиком по умолчанию.

Внутри этого Главного читателя задан механизм запуска нужного читателя, в зависимости от параметров, переданных при инициализации класса-читателя.

### Собственный читатель

Нет необходимости переопределять Главный читатель, так как в собственном обработчике мы всё-равно явно прописываем какой именно метод класса-читателя нам нужно вызвать.

Например мы создали собственный класс-читатель с нужным методом:
```py
from typing import Any
from arfi_settings import ArFiReader


class MyReader(ArFiReader):
    def super_reader(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        data["my_param"] = "param_from_super_reader"
        return data
```

Далее мы можем создать собственный, например, Главный обработчик следующими способами:

При инициализации инстанса `ArFiReader` передать параметр `reader`
```py
from typing import Any
from arfi_settings import ArFiHandler


class MyHandler(ArFiHandler):
    reader_class = MyReader

    def super_main_handler(self) -> dict[str, Any]:
        reader = self.reader_class(reader="super")
        return reader.read()
```

Или напрямую вызвать наш собственный читатель

```py
from typing import Any
from arfi_settings import ArFiHandler, ArFiReader, ArFiSettings


class MyReader(ArFiReader):
    def super_reader(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        data["my_param"] = "param_from_super_reader"
        return data


class MyHandler(ArFiHandler):
    reader_class = MyReader

    def super_main_handler(self) -> dict[str, Any]:
        return self.reader_class().super_reader()


class AppConfig(ArFiSettings):
    my_param: str

    handler_class = MyHandler
    handler = "super_main_handler"


config = AppConfig()
print(config.my_param)
#> param_from_super_reader
```


## Читатели файлов конфигурации
Реализованы в виде методов класса `arfi_settings.ArFiReader`.

Имя метода всегда начинается с названия расширения и всегда заканчивается на `_reader`.

При инициализации класса-читателя путь до файла конфигурации передаётся параметром [file_path](#file_path). Далее, при запуске Главного обработчика, он, этот Главный обработчик (метод `read()`), выполняет следующие шаги:

- определяет расширение `ext`, переданного файла
- определяет имя читателя (метода класса `ArFiReader`), который необходимо запустить, по принципу `#!python f"{ext}_reader"`
- возвращает результат выполнения найденного читателя (метода)

Если нужный читатель не найден, то возбуждается исключение.

**Использование**:

Допустим нам нужно прочитать файл `config/appconfig.arfi` с придуманным расширением `.arfi`, но на самом деле данные, содержащиеся в нём, подчиняются формату сериализации `TOML`:

```txt title="config/appconfig.arfi"
test_param = "param_from_appconfig.arfi"
```

Это можно сделать несколькими способами:

- Сложный способ - создать собственный читатель и обработчик для этого расширения

```py
from typing import Any
from arfi_settings import (
    ArFiHandler,
    ArFiReader,
    ArFiSettings,
    FileConfigDict,
)
from arfi_settings.types import PathType


class MyReader(ArFiReader):
    def arfi_reader(self) -> dict[str, Any]:
        """Reads settings from *.arfi file."""
        data = self.toml_reader()
        # Do something ...
        return data


class MyHandler(ArFiHandler):
    reader_class = MyReader

    def arfi_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        """Handles settings from *.arfi file."""
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

    handler_class = MyHandler
    file_config = FileConfigDict(
        conf_file="appconfig",
        conf_ext="toml, arfi",
    )


config = AppConfig()
print(config.test_param)
#> param_from_appconfig.arfi
```

- Способ по-проще - создать только собственный обработчик для этого расширения и явно указать читатель

```py
from typing import Any
from arfi_settings import (
    ArFiHandler,
    ArFiSettings,
    FileConfigDict,
)
from arfi_settings.types import PathType


class MyHandler(ArFiHandler):
    def arfi_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        """Handles settings from *.arfi file."""
        reader = self.reader_class(
            reader="toml",
            file_path=file_path,
            file_encoding=self.config.conf_file_encoding,
            ignore_missing=self.config.conf_ignore_missing,
        )
        data = reader.read()
        data["__case_sensitive"] = self.config.conf_case_sensitive
        return data


class AppConfig(ArFiSettings):
    test_param: str

    handler_class = MyHandler
    file_config = FileConfigDict(
        conf_file="appconfig",
        conf_ext="toml, arfi",
    )


config = AppConfig()
print(config.test_param)
#> param_from_appconfig.arfi
```

- Способ ещё проще - создать только собственный обработчик для этого расширения, но вернуть результат существующего обработчика

```py
from typing import Any
from arfi_settings import (
    ArFiHandler,
    ArFiSettings,
    FileConfigDict,
)
from arfi_settings.types import PathType


class MyHandler(ArFiHandler):
    def arfi_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        """Handles settings from *.arfi file."""
        return self.toml_ext_handler(file_path=file_path)


class AppConfig(ArFiSettings):
    test_param: str

    handler_class = MyHandler
    file_config = FileConfigDict(
        conf_file="appconfig",
        conf_ext="toml, arfi",
    )


config = AppConfig()
print(config.test_param)
#> param_from_appconfig.arfi
```

- Самый простой способ - назначить обработчик для всех файлов с расширением `.arfi` с помощью параметра [conf_custom_ext_handler](config.md#conf_custom_ext_handler)

```py
from arfi_settings import ArFiSettings, FileConfigDict


class AppConfig(ArFiSettings):
    test_param: str

    file_config = FileConfigDict(
        conf_file="appconfig",
        conf_ext="toml, arfi",
        conf_custom_ext_handler={
            "arfi": "toml",
        },
    )


config = AppConfig()
print(config.test_param)
#> param_from_appconfig.arfi
```


## Читатели переменных окружения

Реализованы в виде методов класса `arfi_settings.ArFiReader`.

За чтение переменных окружения отвечает читатель `env_reader`. Чтоб читатель вернул значения из переменных окружения нужно при инициализации класса-читателя установить параметр [is_env](#is_env) в значение `True`

Пример:

```py title="main.py"
from arfi_settings import ArFiReader


reader = ArFiReader(is_env=True)
data = reader.read()
print("KEY =", data["SECRET_KEY"])
```

В терминале задаём переменную окружения `SECRET_KEY` и запускаем скрипт:

```bash
$ export SECRET_KEY="123"
$ python main.py
KEY = 123
```


За чтение переменных окружения из файла отвечает читатель `env_file_reader`. Чтоб читатель обработчик вернул значения из переменных окружения нужно при инициализации класса-читателя установить параметр [is_env](#is_env) в значение `True`. Если необходимо читать переменные окружения из нескольких файлов, то это реализовано в соответствующем обработчике. Читатель читает по одному файлу, который указан при инициализации.

Пример:

```txt title=".env.local"
SECRET_KEY="123"
```

```py title="main.py"
from arfi_settings import ArFiReader

reader = ArFiReader(file_path=".env.local", is_env_file=True)
data = reader.read()
print("KEY =", data["SECRET_KEY"])
#> KEY = 123
```


## Читатель секретной директории

Реализован в виде метода `secret_file_reader` класса `arfi_settings.ArFiReader`.
Чтоб читатель вернул значения из переменных окружения нужно при инициализации класса-читателя установить параметр [is_secret_file](#is_secret_file) в значение `True`

Файлы можно передавать как с расширением, так и без. Возвращает словарь вида `#!python {"Имя файла": "Содержимое файла в виде строки"}`.

Читает по одному файлу за раз.

Пример:

```txt title="/var/run/secrets/SECRET_KEY"
123
```

```py title="main.py"
from arfi_settings import ArFiReader

reader = ArFiReader(file_path="/var/run/secrets/SECRET_KEY", is_secret_file=True)
data = reader.read()
print(data)
#> {"SECRET_KEY": "123"}
```


## Читатель переменных командной строки

Реализован в виде метода `cli_reader` класса `arfi_settings.ArFiReader`.

Возвращает результат выполнения собственного, заданного пользователем, читателя. А так как по умолчанию собственный читатель не определён, то `cli_reader` возвращает по умолчанию пустой словарь.

Чтоб задать собственный читатель переменных из командной строки нужно воспользоваться встроенным в класс-читатель `ArFiReader` методом `setup_cli_reader`. Метод `setup_cli_reader` в качестве аргумента принимает один параметр - вызываемый объект, то есть объект, у которого реализован метод `__call__`. Результатом выполнения вызова этого объекта должен быть словарь вида `dict[str, Any]`.

Более подробно о том как создавать свой собственный читатель переменных из командной строки описано [здесь](cli.md)

Чтоб читатель вернул параметры и их значения из командной строки нужно при инициализации класса-читателя установить параметр [is_cli](#is_cli) в значение `True`

Пример:

```py title="main.py"
import argparse
from typing import Any
from arfi_settings import ArFiReader, ArFiSettings, SettingsConfigDict


def parse_args() -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--MODE",
        type=str,
        help="Application mode",
    )

    cli_options = parser.parse_args()
    data = dict(cli_options._get_kwargs())
    return data


ArFiReader.setup_cli_reader(parse_args)

reader = ArFiReader(is_cli=True)
data = reader.read()
print("data =", data)
#> {"MODE": "prod"}


class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(cli=True)


config = AppConfig()
print("MODE =", config.MODE)
#> prod
```

Запуск в терминале:
```bash
$ python main.py --MODE prod
data = {"MODE": "prod"}
MODE = prod
```
