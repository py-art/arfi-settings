# Параметры командной строки

Для того чтоб класс настроек смог читать параметры из командной строки должно быть выполнено 2 условия:

1. Должен быть включён режим чтения настроек из командной строки либо в конкретном классе настроек, либо в глобально для всех классов настроек в файле `pyproject.toml`.
2. Сам читатель должен быть создан, а так же задан с помощью метода `setup_cli_reader` либо глобально классу-читателю `ArFiReader`, либо конкретному классу-читателю, который используется для чтения настроек.

По умолчанию параметры из командной строки имеют наивысший приритет при чтении конфигурации. Это поведение можно изменить с помощью параметра [ordered_settings](config.md#ordered_settings)


## Активация режима чтения

Режим чтения `cli` НЕ наследуется от класса-родителя ребёнку в концепции обратного наследования!
### В классе настроек

```py
from arfi_settings import ArFiSettings, SettingsConfigDict


class AppSettings(ArFiSettings):
    model_config = SettingsConfigDict(
        cli=True,                           # (1)!
    )


class AppConfig(ArFiSettings):              # (2)!
    app: AppSettings
```

1. Параметры командной строки читаются для этого класса `AppSettings`
2. Параметры командной строки НЕ читаются для этого класса `AppConfig`


### Глобально для проекта

Так как в файле `pyproject.toml` задаются настройки по умолчанию для каждого класса настроек (подкласса `arfi_settings.ArFiSettings`), то эти настройки можно считать глобальными.

Но не стоит забывать, что настройки, заданные непосредственно в классе, переопределяют настройки по умолчанию, заданные в файле `pyproject.toml`.

```toml title="pyproject.toml"
[tool.arfi_settings]
cli = true
```

## Создание читателя

Для каждого читателя должно выполняться 2 условия:

1. Читатель должен быть вызываемым объектом, то есть в нём должен быть определён метод `__call__`. Простыми словами читатель может быть реализован в виде функции или класса.
2. При вызове читателя возвращаемым типом данных должен быть словарь, ключами которого являются только строки, а значением может быть что угодно - `#!python dict[str, Any]`.

### Читатель как функция

```py title="cli_readers.py"
import argparse
from typing import Any


def my_awesome_cli_reader() -> dict[str, Any]:
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
```
### Читатель как класс

```py title="cli_readers.py"
import argparse
from typing import Any


class MyAwesomeCliReader:
    def parse_args(self) -> dict[str, Any]:
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

    def __call__(self) -> dict[str, Any]:
        return self.parse_args()
```


## Назначение читателя

### Глобально

-  Если читатель является функцией

```py title="settings.py"
from arfi_settings import ArFiReader, ArFiSettings, SettingsConfigDict

from cli_readers import my_awesome_cli_reader


ArFiReader.setup_cli_reader(my_awesome_cli_reader)  # (1)!


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```

1. Передаём только саму функцию, НЕ вызывая её !!!


-  Если читатель является классом

```py title="settings.py"
from arfi_settings import ArFiReader, ArFiSettings, SettingsConfigDict

from cli_readers import my_awesome_cli_reader


ArFiReader.setup_cli_reader(MyAwesomeCliReader())  # (1)!


class AppConfig(ArFiSettings):
    pass


config = AppConfig()
```

1. Передаём инициализированный класс, по сути инстанс класса.


### Собственному классу-читателю

```py title="settings.py"
import argparse
from typing import Any

from arfi_settings import ArFiHandler, ArFiReader, ArFiSettings, SettingsConfigDict
from pydantic import Field


def my_awesome_cli_reader() -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--MODE",
        type=str,
        help="Application mode",
    )
    parser.add_argument(
        "--name",
        type=str,
        action="store",
        default="cli_reader_as_func",
        help="Cli reader name",
    )
    cli_options = parser.parse_args()
    data = dict(cli_options._get_kwargs())
    return data


class MyAwesomeCliReader:
    def parse_args(self) -> dict[str, Any]:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            argument_default=argparse.SUPPRESS,
        )
        parser.add_argument(
            "--MODE",
            type=str,
            help="Application mode",
        )
        parser.add_argument(
            "--name",
            type=str,
            action="store",
            default="CliReaderAsClass",
            help="Cli reader name",
        )
        cli_options = parser.parse_args()
        data = dict(cli_options._get_kwargs())
        return data

    def __call__(self) -> dict[str, Any]:
        return self.parse_args()


class MyReader(ArFiReader):
    """Custom reader."""


# setup global cli reader
ArFiReader.setup_cli_reader(MyAwesomeCliReader())
# setup custom cli reader
MyReader.setup_cli_reader(my_awesome_cli_reader)


class MyHandler(ArFiHandler):
    """Custom handler."""

    reader_class = MyReader


class ChildSettings(ArFiSettings):
    cli_reader: str = Field(alias="name")
    model_config = SettingsConfigDict(cli=True)


class AppSettings(ArFiSettings):
    cli_reader: str = Field(alias="name")
    child: ChildSettings

    handler_class = MyHandler
    model_config = SettingsConfigDict(cli=True)


class AppConfig(ArFiSettings):
    cli_reader: str = Field(alias="name")
    app: AppSettings

    model_config = SettingsConfigDict(cli=True)


config = AppConfig()
# after run in terminal as
# python settings.py --MODE prod
print(f"{config.MODE = }")
#> config.MODE = 'prod'
print(f"{config.cli_reader = }")
#> config.cli_reader = 'CliReaderAsClass'
print(f"{config.app.MODE = }")
#> config.app.MODE = 'prod'
print(f"{config.app.cli_reader = }")
#> config.app.cli_reader = 'cli_reader_as_func'
print(f"{config.app.child.MODE = }")
#> config.app.child.MODE = 'prod'
print(f"{config.app.child.cli_reader = }")
#> config.app.child.cli_reader = 'CliReaderAsClass'
```

Запускаем в терминале:

```bash
$ python settings.py --MODE prod
config.MODE = 'prod'
config.cli_reader = 'CliReaderAsClass'
config.app.MODE = 'prod'
config.app.cli_reader = 'cli_reader_as_func'
config.app.child.MODE = 'prod'
config.app.child.cli_reader = 'CliReaderAsClass'
```

### Ещё один способ назначения

При таком способе назначения, если читатель является функцией, которая не принимает ни одного именованного аргумента, то нужно задать первым позиционным аргументом `#!python self`, иначе поднимется исключение.

```py title="settings.py"
from typing import Any
from arfi_settings import ArFiReader, ArFiSettings, SettingsConfigDict, ArFiHandler


def parse_args(self) -> dict[str, Any]:
    # Read command line params ...
    return {"cli_reader": "cli_reader_as_parse_args"}


def custom_cli_reader(self) -> dict[str, Any]:
    # Read command line params ...
    return {"cli_reader": "cli_reader_as_custom_cli_reader"}


class CliReaderAsClass:
    def __call__(self) -> dict[str, Any]:
        # Read command line params ...
        return {"cli_reader": "CliReaderAsClass"}


class AaaReader(ArFiReader):
    default_cli_reader = parse_args


class BbbReader(ArFiReader):
    default_cli_reader = custom_cli_reader


class CccReader(ArFiReader):
    default_cli_reader = CliReaderAsClass()


class DddReader(ArFiReader):
    pass


DddReader.setup_cli_reader(parse_args)


class AaaHandler(ArFiHandler):
    reader_class = AaaReader


class BbbHandler(ArFiHandler):
    reader_class = BbbReader


class CccHandler(ArFiHandler):
    reader_class = CccReader


class DddHandler(ArFiHandler):
    reader_class = DddReader


class Aaa(ArFiSettings):
    cli_reader: str
    handler_class = AaaHandler
    model_config = SettingsConfigDict(cli=True)


class Bbb(ArFiSettings):
    cli_reader: str
    handler_class = BbbHandler
    model_config = SettingsConfigDict(cli=True)


class Ccc(ArFiSettings):
    cli_reader: str
    handler_class = CccHandler
    model_config = SettingsConfigDict(cli=True)


class Ddd(ArFiSettings):
    cli_reader: str
    handler_class = DddHandler
    model_config = SettingsConfigDict(cli=True)


class AppConfig(ArFiSettings):
    AAA: Aaa
    BBB: Bbb
    CCC: Ccc
    DDD: Ddd


config = AppConfig()
print(f"{config.AAA.cli_reader = }")
#> config.AAA.cli_reader = 'cli_reader_as_parse_args'
print(f"{config.BBB.cli_reader = }")
#> config.BBB.cli_reader = 'cli_reader_as_custom_cli_reader'
print(f"{config.CCC.cli_reader = }")
#> config.CCC.cli_reader = 'CliReaderAsClass'
print(f"{config.DDD.cli_reader = }")
#> config.DDD.cli_reader = 'cli_reader_as_parse_args'
```

Запускаем в терминале:

```bash
$ python settings.py
config.AAA.cli_reader = 'cli_reader_as_parse_args'
config.BBB.cli_reader = 'cli_reader_as_custom_cli_reader'
config.CCC.cli_reader = 'CliReaderAsClass'
```
