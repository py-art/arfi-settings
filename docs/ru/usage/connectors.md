# Коннекторы

## Описание

Так как практически любому приложению требуется где-то хранить или откуда-то читать данные, помимо файлового хранилища, то было принято решение добавить по умолчанию наиболее распространённые коннекторы.

Под коннектором подразумевается набор стандартных параметров, необходимых для установления соединения с конкретным сервисом или базой данных.

Так как все коннекторы наследуются от класса `arfi_settings.ArFiSettings`, то они обладают всеми преимуществами данной библиотеки, такими как:

- быстрая смена режима подключения с помощью параметра [MODE](config.md#mode)
- возможность объединения различных коннекторов по дискриминатору, и мгновенная смена коннектора при изменении дискриминатора в конфигурации
- чтение настроек из различных источников
- автоматическая валидация значений, заданных в конфигурации
- а так же дополнительными преимуществами, реализованными конкретно в данных коннекторах

Коннекторы, которые реализованы, отмечены галочкой, остальные в ближайших планах для реализации:

- [x] [SQLite](#sqlite)
- [x] [MySQL](#mysql)
- [x] [PostgreSQL](#postgresql)
- [ ] ClickHouse
- [ ] MongoDB
- [ ] Redis
- [ ] RabbitMQ
- [ ] Kafka


## SQLite

Сам коннектор реализован классом `arfi_settings.connectors.SQLite`.

Упрощённо и схематично его можно представить в следующем виде:

```py
from typing import Literal
from pydantic import BaseModel


class SQLite(BaseModel):
    MODE: str | None = None
    DIALECT: Literal["sqlite"] = "sqlite"
    DRIVER: Literal["", "pysqlite", "aiosqlite"] = ""
    DATABASE: str = ":memory:"
    DATABASE_URL: str = ""
```

Поле `DATABASE_URL` имеет приоритет. То есть если передан параметр `DATABASE_URL` в конфигурации, то остальные параметры заполняются исходя из значений, переданных в этом параметре. Но если параметр `DATABASE_URL` не передан в конфигурации, то `DATABASE_URL` будет строиться исходя из остальных переданных параметров.

Имена переменных окружения должны начинаться с префикса `sqlite_` или `SQLITE_`. Например `SQLITE_DATABASE_URL`.


## MySQL

Сам коннектор реализован классом `arfi_settings.connectors.MySQL`.

Упрощённо и схематично его можно представить в следующем виде:

```py
from typing import Literal
from pydantic import BaseModel


ALLOWED_MYSQL_DRIVERS = Literal[
    "",
    "mysqlconnector",
    "aiomysql",
    "asyncmy",
    "mysqldb",
    "pymysql",
    "cymysql",
    "pyodbc",
]


class MySQL(BaseModel):
    MODE: str | None = None
    DIALECT: Literal["mysql"] = "mysql"
    DRIVER: ALLOWED_MYSQL_DRIVERS = ""
    HOST: str
    PORT: int = 3306
    USER: str
    PASSWORD: str
    DATABASE: str = ""
    DATABASE_URL: str = ""
```

Поле `DATABASE_URL` имеет приоритет. То есть если передан параметр `DATABASE_URL` в конфигурации, то остальные параметры заполняются исходя из значений, переданных в этом параметре. Но если параметр `DATABASE_URL` не передан в конфигурации, то `DATABASE_URL` будет строиться исходя из остальных переданных параметров.

Имена переменных окружения должны начинаться с префикса `mysql_` или  `MQSQL_`. Например `MQSQL_DATABASE_URL`.


## PostgreSQL

Сам коннектор реализован классом `arfi_settings.connectors.PostgreSQL`.

Упрощённо и схематично его можно представить в следующем виде:

```py
from typing import Literal
from pydantic import BaseModel


ALLOWED_POSTGRES_DRIVERS = Literal[
    "",
    "asyncpg",
    "pg8000",
    "psycopg",
    "psycopg2",
    "psycopg2cffi",
    "py-postgresql",
    "pygresql",
]


class PostgreSQL(BaseModel):
    MODE: str | None = None
    DIALECT: Literal["postgresql"] = "postgresql"
    DRIVER: ALLOWED_POSTGRES_DRIVERS = ""
    HOST: str
    PORT: int = 5432
    USER: str
    PASSWORD: str
    DATABASE: str = ""
    DATABASE_URL: str = ""
```

Поле `DATABASE_URL` имеет приоритет. То есть если передан параметр `DATABASE_URL` в конфигурации, то остальные параметры заполняются исходя из значений, переданных в этом параметре. Но если параметр `DATABASE_URL` не передан в конфигурации, то `DATABASE_URL` будет строиться исходя из остальных переданных параметров.

Имена переменных окружения должны начинаться с префикса `postgres_` или `POSTRES_`. Например `POSTRES_DATABASE_URL`.


## Пример настройки подключения к БД

### Стандартное подключение

Ниже приведён пример одного из вариантов развёртывания приложения в проде с использование секретной директории.

Создаём необходимые файлы:

- На сервере в секретной директории укажем режим работы приложения

```txt title="/var/run/secrets/MODE"
production
```

- На сервере в секретной директории укажем хост, пользователя и пароль

```toml title="/var/run/secrets/config/db/postgres/production.toml"
host = "production.site.com"
user = "secret_usrname"
password = "SUPER_SECRET_PASSWORD"
```

- Указываем секретную директорию глобально для всего проекта, которую мы предварительно создали на сервере

```toml title="pyproject.toml"
[tool.arfi_settings]
secrets_dir = "/var/run/secrets/config"
```

- В домашней директории проекта укажем настройки подключения, которые будем использовать в режиме разработки

```toml title="config/config.toml"
[db]
host = "127.0.0.1"
user = "root"
password = "password"
database = "my_database"
```

- В домашней директории создаем файл с настройками подключения к тестовой базе данных, развёрнутой на удалённом сервере, в которой хранятся данные, наиболее приближенные к продуктовой БД

```toml title="config/db/postgres/dev.toml"
host = "test.develop.net"
user = "test"
password = "test"
```
Подключаться к тестовой базе данных при разработке будем путём задания значения переменной окружения `DB__MODE` в файле `.env`:

```txt title=".env"
DB__MODE=dev
```

- Задаём необходимые параметры в классе настроек для чтения конфигурации:

  * В `ordered_settings` задаём наивысший приоритет настройкам, прочитанным из секретной директории. В данном случае это нужно для указания `MODE`, чтоб на сервере приоритетные настройки читались из файлов `production.toml`
  * В параметре `conf_dir` задаем пути к директориям с конфигурационными файлами, при этом секретную директорию указываем как наиболее приоритетную.
  * Задаём разделитель для имён переменных окружения, чтоб при разработке мы могли задать режим БД более человеко-читаемым названием переменной `DB__MODE`. Хотя наиболее приоритетным в данном случае будет значение, указанное в переменной окружения `POSTRES_MODE`

```py title="settings.py"
from arfi_settings import ArFiSettings, SettingsConfigDict
from arfi_settings.connectors import PostgreSQL


class AppConfig(ArFiSettings):
    db: PostgreSQL

    model_config = SettingsConfigDict(
        conf_dir=[
            "config",
            "/var/run/secrets/config",
        ],
        secrets_dir="/var/run/secrets",
        env_nested_delimiter="__",
    )
    ordered_settings = [
        "secrets",
        "cli",
        "init_kwargs",
        "env",
        "env_file",
        "conf_file",
    ]


config = AppConfig()
print(config.db.model_dump_json(indent=4))
```

- Результат запуска на локальной машине без указания переменной окружения `DB__MODE`:

```bash
$ python settings.py
{
    "MODE": null,
    "DIALECT": "postgresql",
    "DRIVER": "",
    "DATABASE": "my_database",
    "DATABASE_URL": "postgresql://root:password@127.0.0.1:5432/my_database",
    "HOST": "127.0.0.1",
    "PORT": 5432,
    "USER": "root",
    "PASSWORD": "password"
}
```

- Результат запуска на локальной машине с переменной окружения `DB__MODE=dev`:

```bash
$ python settings.py
{
    "MODE": "dev",
    "DIALECT": "postgresql",
    "DRIVER": "",
    "DATABASE": "my_database",
    "DATABASE_URL": "postgresql://test:test@test.develop.net:5432/my_database",
    "HOST": "test.develop.net",
    "PORT": 5432,
    "USER": "test",
    "PASSWORD": "test"
}
```

- Результат запуска на сервере:

```bash
$ python settings.py
{
    "MODE": "production",
    "DIALECT": "postgresql",
    "DRIVER": "",
    "DATABASE": "my_database",
    "DATABASE_URL": "postgresql://secret_usrname:SUPER_SECRET_PASSWORD@production.site.com:5432/my_database",
    "HOST": "production.site.com",
    "PORT": 5432,
    "USER": "secret_usrname",
    "PASSWORD": "SUPER_SECRET_PASSWORD"
}
```
### Подключение используя дискриминатор

Если в классе настроек задать подключение к БД с помощью дискриминатора, то можно использовать не только все преимущества стандартного подключения, но и с лёгкостью переключаться между разными типами БД.

Ниже приведён упрощённый пример реализации, потому что настройки для каждой конкретной БД можно прописывать не только в общем файле настроек, но и в файлах настроек конкретной бд, например в файлах `config/db/mysql/config.toml` и `config/db/postgres/config.toml`, а так же задавать наиболее приоритетными переменными окружения, такими как `POSTGRES_PASSWORD` и `MYSQL_PASSWORD`.

**Создадим необходимые файлы**:

- общий файл конфигурации

```toml title="config/config.toml"
[db]
host = "127.0.0.1"
user = "root"
password = "password"
database = "my_database"
```

- Файл с переменными окружение. Менять будем только значение переменной `DB__DIALECT`

```txt title=".env"
DB__DIALECT=sqlite
# DB__DIALECT=mysql
# DB__DIALECT=postgresql
```

Диалект так же можно менять и в общем файле конфигурации, но переменные окружения по умолчанию имеют приоритет:

```toml title="config/config.toml"
[db]
dialect = "postgresql"
```

- Файл настроек

```py title="settings.py"
from arfi_settings import ArFiSettings, SettingsConfigDict
from arfi_settings.connectors import MySQL, PostgreSQL, SQLite
from pydantic import Field


class AppConfig(ArFiSettings):
    db: SQLite | MySQL | PostgreSQL = Field(SQLite(), discriminator="DIALECT")

    model_config = SettingsConfigDict(env_nested_delimiter="__")


config = AppConfig()
print(config.db.model_dump_json(indent=4))
```

- Результат запуска с переменной окружения `DB__DIALECT=sqlite` или вообще без указания этой переменной:

```bash
$ python settings.py
{
    "MODE": null,
    "DIALECT": "sqlite",
    "DRIVER": "",
    "DATABASE": "my_database",
    "DATABASE_URL": "sqlite:///my_database"
}
```

- Результат запуска с переменной окружения `DB__DIALECT=mysql` или вообще без указания этой переменной:

```bash
$ python settings.py
{
    "MODE": null,
    "DIALECT": "mysql",
    "DRIVER": "",
    "DATABASE": "my_database",
    "DATABASE_URL": "mysql://root:password@127.0.0.1:3306/my_database",
    "HOST": "127.0.0.1",
    "PORT": 3306,
    "USER": "root",
    "PASSWORD": "password"
}
```

- Результат запуска с переменной окружения `DB__DIALECT=postgresql` или вообще без указания этой переменной:

```bash
$ python settings.py
{
    "MODE": null,
    "DIALECT": "postgresql",
    "DRIVER": "",
    "DATABASE": "my_database",
    "DATABASE_URL": "postgresql://root:password@127.0.0.1:5432/my_database",
    "HOST": "127.0.0.1",
    "PORT": 5432,
    "USER": "root",
    "PASSWORD": "password"
}
```
