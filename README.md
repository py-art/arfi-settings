<p align="center">
  <a href="https://py-art.github.io/arfi-settings/en/">
    <img src="https://github.com/py-art/arfi-settings/blob/main/docs/assets/images/github-logo.png?raw=true" alt="ArFiSettings">
  </a>
</p>
<p align="center">
  <i>ArFiSettings - flexible application settings management with Pydantic validation</i>
</p>
<p align="center">
  <a href="https://codecov.io/github/py-art/arfi-settings" >
    <img alt="Codecov" src="https://img.shields.io/codecov/c/github/py-art/arfi-settings?color=008080&logo=codecov&logoColor=008080">
  </a>
  <a href="https://pypi.org/project/arfi-settings" target="_blank">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/v/arfi-settings?label=pipy%20package&color=008080" alt="Package version"/>
  </a>
  <a href="https://pypi.org/project/arfi-settings" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/arfi-settings?color=008080" alt="Supported Python versions"/>
  </a>
</p>
<p align="center">
  <a href="https://py-art.github.io/arfi-settings/en/">Documentation</a>  |  <a href="https://py-art.github.io/arfi-settings/">Документация</a>
</p>

# arfi-settings

<!--toc:start-->
- [Installation](#installation)
- [Advantages](#advantages)
- [Features](#features)
  - [Reverse inheritance](#reverse-inheritance)
  - [model_config, file_config and env_config](#modelconfig-fileconfig-and-envconfig)
  - [Users Readers and Handlers](#users-readers-and-handlers)
  - [CLI](#cli)
  - [MODE](#mode)
  - [Reading order of settings](#reading-order-of-settings)
  - [File `pyproject.toml`](#file-pyprojecttoml)
- [A Simple Example](#a-simple-example)
- [Roadmap](#roadmap)
- [Logo](#logo)
<!--toc:end-->


## Installation

```bash
pip install -U arfi-settings
```

## Advantages

- Contains all the functionality of [pydantic-settings](https://github.com/pydantic/pydantic-settings), but with more accurate name resolving.
- Inheritance is used when reading from any source.
- Specifying configuration sources is individual for each class of settings.
- Possibility to switch all settings by changing just one `MODE` parameter.
- Ability to switch between specific settings using the discriminator.
- Read configuration files with and without any extension.
- Configure reading command line parameters individually for the class and for the entire project.
- Clear configuration file structure out of the box with no need for pre-configuration. Flexible setting of absolutely all parameters.
- Easy creation of your own configuration read sources.
- Availability of connectors to the most common databases
- Specify your own default library settings in the `pyproject.toml` file.
- Debug Mode.
- And many other things ...


## Features

### Reverse inheritance

If a parent class, essentially the main settings class, has fields that inherit from `ArFiSettings`, then it will inherit settings from that parent class.
This behaviour can be switched off.
```py
from arfi_settings import ArFiSettings, SettingsConfigDict

class SubChild(ArFiSettings):
    pass

class Child(ArFiSettings):
    sub_child: SubChild

class Parent(ArFiSettings):
    child: Child

config = Parent()

print(config.conf_path)
#> [PosixPath('config/config')]
print(config.child.sub_child.conf_path)
#> [PosixPath('config/child/sub_child/config')]
print(config.settings_config.env_nested_delimiter)
#> ""
print(config.child.sub_child.settings_config.env_nested_delimiter)
#> ""

# Change settings in parent class
class Parent(ArFiSettings):
    child: Child
    model_config = SettingsConfigDict(
        conf_dir=None,
        conf_file=['appconfig.yaml', '~/.config/allacrity/config.toml'],
        env_nested_delimiter="__",
    )

config = Parent()

print(config.conf_path)
#> [PosixPath('appconfig.yaml'), PosixPath('/home/user/.config/allacrity/config.toml')]
print(config.child.sub_child.conf_path)
#> [PosixPath('child/sub_child/appconfig.yaml'), PosixPath('/home/user/.config/allacrity/config.toml')]
print(config.settings_config.env_nested_delimiter)
#> "__"
print(config.child.sub_child.settings_config.env_nested_delimiter)
#> "__"
```

### model_config, file_config and env_config

Absolutely all settings can be specified via the `model_config` variable.
But the settings for files and environment variables can be set separately in `file_config` and `env_config` respectively.
The settings specified in `file_config` and `env_config` will take precedence and override the settings specified in `model_config`.
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

### Users Readers and Handlers

Adding your own readers and handlers.

```py
from typing import Any

from arfi_settings import (
    ArFiHandler,
    ArFiReader,
    ArFiSettings,
    EnvConfigDict,
    FileConfigDict,
    SettingsConfigDict,
)
from arfi_settings.types import PathType


class AwessomReader(ArFiReader):
    def my_custom_reader(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        return data


class AwessomHandler(ArFiHandler):
    reader_class = AwessomReader

    def nonextension_ext_handler(self, file_path: PathType) -> dict[str, Any]:
        reader = self.reader_class(
            file_path=file_path,
            file_encoding=self.config.conf_file_encoding,
            ignore_missing=self.config.conf_ignore_missing,
        )
        data = reader.my_custom_reader()
        # Do something ...
        data["__case_sensitive"] = self.config.conf_case_sensitive
        return data


# First way: Redefinition handler class inside main config class
class AppConfig(ArFiSettings):
    handler_class = AwessomHandler
    file_config = FileConfigDict(
        conf_ext="json",
    )
    model_config = SettingsConfigDict(
        conf_ext=["", "arfi"],
        conf_custom_ext_handler={"": "nonextension", "arfi": "toml"},
    )


config = AppConfig()
print(config.settings_config.conf_ext)
# > ['json']

# Second way: Redefinition Main handler class for all settings
ArFiSettings.handler_class = AwessomHandler


class AppConfig(ArFiSettings):
    file_config = FileConfigDict(
        conf_ext="json",
    )
    model_config = SettingsConfigDict(
        conf_ext=["", "arfi"],
        conf_custom_ext_handler={"": "nonextension", "arfi": "toml"},
    )


config = AppConfig()
print(config.settings_config.conf_ext)
# > ['json']


# An alternative way: Redefinition Main handler inside class
class AwessomHandler(ArFiHandler):
    def custom_main_handler(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        return data


class AppConfig(ArFiSettings):
    handler_class = AwessomHandler
    handler = "custom_main_handler"
    file_config = FileConfigDict(
        conf_ext="json",
    )
    model_config = SettingsConfigDict(
        conf_ext=["", "arfi"],
    )


config = AppConfig()
print(config.settings_config.conf_ext)
# > ['json']
```

### CLI

The CLI reader can be any callable object that returns `dict[str, Any]`.

```py
import argparse
from typing import Any

from arfi_settings import ArFiSettings, ArFiReader, SettingsConfigDict


def parse_args() -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--mode",
        type=str,
        help="Application mode",
    )

    cli_options = parser.parse_args()
    data = dict(cli_options._get_kwargs())
    return data

# Valid cli reader
ArFiReader.setup_cli_reader(parse_args)
# No Valid cli reader
# ArFiReader.setup_cli_reader(parse_args())

class AppConfig(ArFiSettings):
    model_config = SettingsConfigDict(
        cli=True,
    )

config = AppConfig()
# if run python main.py --mode dev
print(config.model_dump_json())
#> {"MODE": "dev"}


class MyCliReader:
    def __call__(self) -> dict[str, Any]:
      parser = argparse.ArgumentParser(
          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
          argument_default=argparse.SUPPRESS,
      )
      parser.add_argument(
          "--mode",
          type=str,
          help="Application mode",
      )

      cli_options = parser.parse_args()
      data = dict(cli_options._get_kwargs())
      return data

ArFiReader.setup_cli_reader(MyCliReader())

config = AppConfig()

# if run python main.py --mode dev
print(config.model_dump_json())
#> {"MODE": "dev"}
```
### MODE

The main feature of this library is to change the mode of settings (`MODE`) during processing.
For example:
- create a directory with settings in a secret directory on the server.
- to specify all the settings files for a particular mode.
- specify this directory in the class
- specify in environment variables the mode of reading settings `MODE='prod'`.

```bash
sudo mkdir -p /var/run/config
sudo touch /var/run/config/prod.toml
export MODE="prod"
```

```toml
# file /var/run/config/prod.toml
some_var = "test"
```

```py
from arfi_settings import ArFiSettings, SettingsConfigDict

class AppConfig(ArFiSettings):
    some_var: str
    model_config = SettingsConfigDict(
        conf_dir = ["config", "/var/run/config"],
    )

config = AppConfig()
print(config.some_var)
#> test
```

### Reading order of settings

By default:
```py
ORDERED_SETTINGS = [
    "cli",
    "init_kwargs",
    "env",
    "env_file",
    "secrets",
    "conf_file",
]
```
To change:
```py
from arfi_settings import ArFiSettings

class AppConfig(ArFiSettings):
    # change for class
    ordered_settings = ["conf_file", "env", "init_kwargs"]

# change for instance
config = AppConfig(_ordered_settings=["env", "conf_file"])
```
To create custom handler:
```py
from arfi_settings import ArFiSettings, ArFiHandler

class MyHandler(ArFiHandler):
    # method name must ends with `_ordered_settings_handler` and returns `dict[str, Any]`
    def my_custom_ordered_settings_handler(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        # Do something ...
        return data

class AppConfig(ArFiSettings):
    handler_class = MyHandler
    # Here you can specify the short name of the handler method
    ordered_settings = ["my_custom", "init_kwargs"]

```

### File `pyproject.toml`

In this file, set default values for each subclass of `ArFiSettings`.
The values set in the class override the values set in the file `pyproject.toml`.

```toml
[tool.arfi_settings]
env_config_inherit_parent = false
conf_dir = ["config", "/var/run/config"]
env_file_encoding = "cp1251"
arfi_debug = true  # enable debug mode
```

The location of the `pyproject.toml` file is determined automatically. By default, the search is maximally 3 directories up.
If the file is undefined, you can set manually either the maximum search depth by the `pyproject_toml_max_depth` parameter, or the exact depth by the `pyproject_toml_depth` parameter. It is possible to prohibit the search and reading of settings from the `pyproject.toml` file individually for a class or for a class instance by setting the `read_pyproject_toml=False` parameter.

For example. We have a project structure:
```
~/my_project/
├── settings/
│  ├── __init__.py
│  └── settings.py
├── __init__.py
├── main.py
└── pyproject.toml
```

Best way
```py
# file ~/my_project/settings/__init__.py
from arfi_settings import init_settings

init_settings.read_pyproject(read_once=True)

# For automatic search up to a maximum of 5 directories
# init_settings.read_pyproject(
#     read_once=True,
#     pyproject_toml_max_depth=5,
# )

# To specify the exact location of the `pyproject.toml` file
# init_settings.read_pyproject(
#     read_once=True,
#     pyproject_toml_depth=7,
# )
```

Alternative way
```py
# file ~/my_project/settings/settings.py
from arfi_settings import ArFiSettings

class AppConfig(ArFiSettings):
    pass

config = AppConfig(_pyproject_toml_max_depth=5)

# To disable reading settings from the `pyproject.toml` file
# config = AppConfig(_read_pyproject_toml=False)
```

For check path
```py
# file ~/my_project/main.py
from settings.settings import config

print(config.pyproject_toml_path)
#> /home/user/my_project/pyproject.toml
```

## A Simple Example

1. Create `settings.py`
```py
from typing import Literal

from pydantic import Field

from arfi_settings import ArFiSettings, SettingsConfigDict, EnvConfigDict


class Database(ArFiSettings):
    DIALECT: Literal["sqlite", "mysql", "postgres"]
    DATABASE: str

    # Create common nested directory for read settings from config/db for sqlite, mysql, postgres
    mode_dir = "db"
    # Disable inheritance of settings from parent
    env_config_inherit_parent = False
    # Create env prefix as sqlite_, mysql_, postgres_
    env_config = EnvConfigDict(env_prefix_as_source_mode_dir=True)


class SQLite(Database):
    mode_dir = "sqlite"
    DIALECT: Literal["sqlite"] = "sqlite"
    DATABASE: str = "default_database"


class MySQL(Database):
    mode_dir = "mysql"
    DIALECT: Literal["mysql"] = "mysql"
    DATABASE: str


class PostgreSQL(Database):
    mode_dir = "postgres"
    DIALECT: Literal["postgres"] = "postgres"
    DATABASE: str


class AppConfig(ArFiSettings):
    db: SQLite | MySQL | PostgreSQL = Field(SQLite(), discriminator="DIALECT")

    # set env delimiter
    model_config = SettingsConfigDict(env_nested_delimiter="__")


config = AppConfig()
print(config.db.DIALECT)
# > sqlite
print(config.db.DATABASE)
# > default_database
```

2. Create file `config/config.toml`
```toml
[db]
Database = "main_config_database"
```
Result:
```py
config = AppConfig()
print(config.db.DIALECT)
# > sqlite
print(config.db.DATABASE)
# > main_config_database
```

3. Create file `.env`
```env
DB__DATABASE = "env_database"
```
Result:
```py
config = AppConfig()
print(config.db.DIALECT)
# > sqlite
print(config.db.DATABASE)
# > env_database
```

4. Create file `config/db/sqlite/config.toml`
```toml
database = "sqlite_config_database"
```
Result:
```py
config = AppConfig()
print(config.db.DIALECT)
# > sqlite
print(config.db.DATABASE)
# > sqlite_config_database
```
5. Modify file `.env`
```env
DB__DATABASE = "env_database"
SQLITE_DATABASE = "sqlite_env_database"
```
Result:
```py
config = AppConfig()
print(config.db.DIALECT)
# > sqlite
print(config.db.DATABASE)
# > sqlite_env_database
```

6. Create file `config/db/postgres/config.toml`
```toml
database = 'postgres_database_config'
```
Modify file `config/config.toml`
```toml
[db]
Database = "main_config_database"
dialect = "postgres"
```
Result:
```py
config = AppConfig()
print(config.db.DIALECT)
# > postgres
print(config.db.DATABASE)
# > postgres_database_config
```

7. Create file `config/db/postgres/prod.toml`
```toml
database = 'postgres_database_config_prod'
```
Modify file `.env`
```env
DB__DATABASE = "env_database"
SQLITE_DATABASE = "sqlite_env_database"
DB__MODE = "prod"
```
Result:
```py
config = AppConfig()
print(config.db.DIALECT)
# > postgres
print(config.db.DATABASE)
# > postgres_database_config_prod
```

8. Modify file `.env`
```env
DB__DATABASE = "env_database"
SQLITE_DATABASE = "sqlite_env_database"
DB__MODE = "test"
DB__DIALECT = "mysql"
```
Create file `config/db/mysql/test.yaml`
```yaml
database: "mysql_database_config_test"
```

Result:
```py
config = AppConfig()
print(config.db.DIALECT)
# > mysql
print(config.db.DATABASE)
# > mysql_database_config_test
```

9. Modify file `.env`
```env
DB__DATABASE = "env_database"
SQLITE_DATABASE = "sqlite_env_database"
DB__MODE = "test"
DB__DIALECT = "mysql"
MYSQL_DATABASE = "mysql_database_env"
```
Result:
```py
config = AppConfig()
print(config.db.DIALECT)
# > mysql
print(config.db.DATABASE)
# > mysql_database_env
```

10. Set environment variables
```bash
export DB__DIALECT="postgres"
export POSTGRES_DATABASE="postgres_database_from_enviroment"
```
Result:
```py
config = AppConfig()
print(config.db.DIALECT)
# > postgres
print(config.db.DATABASE)
# > postgres_database_from_enviroment
```


## Roadmap

- [x] Create documentation
- [ ] Add missing connectors
- [ ] Read settings from files without creating a model, but with the ability to use `MODE` as for the main settings class
- [ ] Reading settings from `URL`
- [ ] Reading encrypted settings with key specification
- [ ] Expand debugging mode.


## Logo
Logo courtesy of [Alex Zalevski](https://github.com/zalexstudios)
