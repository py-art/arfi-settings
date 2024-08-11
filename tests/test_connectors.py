import pydantic
import pytest
from pydantic_core import MultiHostUrl, Url

from arfi_settings import ArFiSettings, SettingsConfigDict
from arfi_settings.connectors import BaseDatabase, MySQL, PostgreSQL, SQLite


# @pytest.mark.current
@pytest.mark.connectors
def test_new_connector():
    with pytest.raises(TypeError) as excinfo:

        class NewConnector(BaseDatabase):
            pass

    assert "missing the `Dsn` class variable." in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.connectors
def test_sqlite_defaul_param(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        db: SQLite = SQLite()

    config = AppConfig()
    assert config.db.DIALECT == "sqlite"
    assert config.db.DRIVER == ""
    assert config.db.DATABASE == ":memory:"
    assert str(config.db.DATABASE_URL) == "sqlite:///:memory:"
    assert config.db.database_uri == "sqlite:///:memory:"
    assert config.db.model_dump() == {
        "MODE": None,
        "DIALECT": "sqlite",
        "DRIVER": "",
        "DATABASE": ":memory:",
        "DATABASE_URL": Url("sqlite:///:memory:"),
    }

    data = {"db": {"database_url": Url("sqlite://")}}
    config = AppConfig(**data)
    assert config.db.DATABASE == ":memory:"


# @pytest.mark.current
@pytest.mark.connectors
def test_sqlite_dialect(monkeypatch, cwd_to_tmp, path_base_dir):
    class AppConfig(ArFiSettings):
        db: SQLite
        model_config = SettingsConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("DB__DIALECT", "sqlite")
    config = AppConfig()
    assert config.db.DIALECT == "sqlite"

    with pytest.raises(pydantic.ValidationError) as excinfo:
        monkeypatch.setenv("DB__DIALECT", "mysql")
        AppConfig()

    assert excinfo.value.errors(include_url=False) == [
        {
            "ctx": {
                "expected": "'sqlite'",
            },
            "input": "mysql",
            "loc": (
                "db",
                "DIALECT",
            ),
            "msg": "Input should be 'sqlite'",
            "type": "literal_error",
        },
    ]


# @pytest.mark.current
@pytest.mark.connectors
def test_sqlite_driver(monkeypatch, cwd_to_tmp, path_base_dir):
    class AppConfig(ArFiSettings):
        db: SQLite
        model_config = SettingsConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("DB__DRIVER", "aiosqlite")
    config = AppConfig()
    assert config.db.DRIVER == "aiosqlite"
    assert config.db.database_uri == "sqlite+aiosqlite:///:memory:"

    with pytest.raises(pydantic.ValidationError) as excinfo:
        monkeypatch.setenv("DB__DRIVER", "not_valid_driver")
        AppConfig()

    assert excinfo.value.errors(include_url=False) == [
        {
            "ctx": {
                "expected": "'', 'pysqlite' or 'aiosqlite'",
            },
            "input": "not_valid_driver",
            "loc": (
                "db",
                "DRIVER",
            ),
            "msg": "Input should be '', 'pysqlite' or 'aiosqlite'",
            "type": "literal_error",
        },
    ]


# @pytest.mark.current
@pytest.mark.connectors
def test_sqlite_database(monkeypatch, cwd_to_tmp, path_base_dir):
    class AppConfig(ArFiSettings):
        db: SQLite
        model_config = SettingsConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("DB__DATABASE", "test.sqlite3")
    config = AppConfig()
    assert config.db.DATABASE == "test.sqlite3"
    assert config.db.database_uri == "sqlite:///test.sqlite3"

    config_dir = cwd_to_tmp / "config"
    config_dir.mkdir(exist_ok=True)
    conf_file = config_dir / "config.toml"
    conf_file.touch(exist_ok=True)
    conf_file.write_text(
        """
        [db]
        database = ["db", "db.sqlite"]
        """
    )
    monkeypatch.delenv("DB__DATABASE", raising=False)

    with pytest.raises(pydantic.ValidationError) as excinfo:
        AppConfig()

    assert excinfo.value.errors(include_url=False) == [
        {
            "input": [
                "db",
                "db.sqlite",
            ],
            "loc": (
                "db",
                "DATABASE",
            ),
            "msg": "Input should be a valid string",
            "type": "string_type",
        },
    ]


# @pytest.mark.current
@pytest.mark.connectors
def test_sqlite_database_url(monkeypatch, cwd_to_tmp, path_base_dir):
    monkeypatch.setenv("DB__DATABASE", "default_database")

    class AppConfig(ArFiSettings):
        db: SQLite
        model_config = SettingsConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("DB__DATABASE_URL", "sqlite://")
    config = AppConfig()
    assert str(config.db.DATABASE_URL) == "sqlite:///:memory:"
    assert config.db.database_uri == "sqlite:///:memory:"
    assert config.db.DATABASE == ":memory:"

    monkeypatch.setenv("DB__DATABASE_URL", "sqlite+pysqlite://")
    config = AppConfig()
    assert str(config.db.DATABASE_URL) == "sqlite+pysqlite:///:memory:"
    assert config.db.database_uri == "sqlite+pysqlite:///:memory:"
    assert config.db.DATABASE == ":memory:"
    assert config.db.DRIVER == "pysqlite"

    monkeypatch.setenv("DB__DATABASE_URL", "sqlite:///:memory:")
    config = AppConfig()
    assert str(config.db.DATABASE_URL) == "sqlite:///:memory:"
    assert config.db.database_uri == "sqlite:///:memory:"
    assert config.db.DATABASE == ":memory:"

    monkeypatch.setenv("DB__DATABASE_URL", "sqlite:///test.sqlite3")
    config = AppConfig()
    assert str(config.db.DATABASE_URL) == "sqlite:///test.sqlite3"
    assert config.db.database_uri == "sqlite:///test.sqlite3"
    assert config.db.DATABASE == "test.sqlite3"

    monkeypatch.setenv("DB__DATABASE_URL", "sqlite_db")
    with pytest.raises(pydantic.ValidationError) as excinfo:
        config = AppConfig()

    assert "incorrect url" in str(excinfo.value)

    monkeypatch.setenv("DB__DATABASE_URL", "sqlite://host/test.sqlite3")
    with pytest.raises(pydantic.ValidationError) as excinfo:
        config = AppConfig()

    assert "incorrect url" in str(excinfo.value)

    monkeypatch.delenv("DB__DATABASE_URL", raising=False)
    monkeypatch.delenv("DB__DATABASE", raising=False)

    with pytest.raises(pydantic.ValidationError) as excinfo:
        data = {"db": ["db", "db.sqlite"]}
        AppConfig(**data)

    assert excinfo.value.errors(include_url=False) == [
        {
            "ctx": {
                "class_name": "SQLite",
            },
            "input": ["db", "db.sqlite"],
            "loc": ("db",),
            "msg": "Input should be a valid dictionary or instance of SQLite",
            "type": "model_type",
        },
    ]

    data = {"db": {"database_url": Url("sqlite:///")}}
    config = AppConfig(**data)
    assert config.db.DATABASE == ":memory:"
    assert config.db.database_uri == "sqlite:///:memory:"

    with pytest.raises(pydantic.ValidationError) as excinfo:
        data = {"db": {"database_url": 123}}
        AppConfig(**data)

    assert excinfo.value.errors(include_url=False) == [
        {
            "input": 123,
            "loc": (
                "db",
                "DATABASE_URL",
            ),
            "msg": "URL input should be a string or URL",
            "type": "url_type",
        },
    ]


# @pytest.mark.current
@pytest.mark.connectors
def test_postgres_defaul_param(cwd_to_tmp, path_base_dir):
    config_dir = cwd_to_tmp / "config"
    config_dir.mkdir()
    conf_file = config_dir / "config.toml"
    conf_file.write_text(
        """
        [DB]
        HOST = "127.0.0.1"
        USER = "root"
        PASSWORD = "password"
        DATABASE = "database"
        """
    )

    class DatabaseConfig(ArFiSettings):
        db: PostgreSQL

    config = DatabaseConfig()
    assert config.db.DIALECT == "postgresql"
    assert config.db.DRIVER == ""
    assert config.db.HOST == "127.0.0.1"
    assert config.db.PORT == 5432
    assert config.db.USER == "root"
    assert config.db.PASSWORD == "password"
    assert config.db.DATABASE == "database"
    assert str(config.db.DATABASE_URL) == "postgresql://root:password@127.0.0.1:5432/database"
    assert config.db.database_uri == "postgresql://root:password@127.0.0.1:5432/database"


# @pytest.mark.current
@pytest.mark.connectors
def test_postgres_database_url(cwd_to_tmp, path_base_dir):
    class DatabaseConfig(ArFiSettings):
        db: PostgreSQL

    data = {"db": {"database_url": "postgresql://user:password@localhost:6432/test"}}
    config = DatabaseConfig(**data)
    assert config.db.DIALECT == "postgresql"
    assert config.db.DRIVER == ""
    assert config.db.HOST == "localhost"
    assert config.db.PORT == 6432
    assert config.db.USER == "user"
    assert config.db.PASSWORD == "password"
    assert config.db.DATABASE == "test"
    assert str(config.db.DATABASE_URL) == "postgresql://user:password@localhost:6432/test"
    assert config.db.database_uri == "postgresql://user:password@localhost:6432/test"

    data = {"db": {"database_url": Url("postgresql://user:password@localhost:6432/test")}}
    config = DatabaseConfig(**data)
    assert config.db.DATABASE == "test"

    with pytest.raises(pydantic.ValidationError) as excinfo:
        DatabaseConfig(db={"database_url": 123})

    assert excinfo.value.errors(include_url=False) == [
        {
            "input": 123,
            "loc": (
                "db",
                "DATABASE_URL",
            ),
            "msg": "URL input should be a string or URL",
            "type": "url_type",
        },
        {
            "input": {
                "DATABASE_URL": 123,
            },
            "loc": (
                "db",
                "HOST",
            ),
            "msg": "Field required",
            "type": "missing",
        },
        {
            "input": {
                "DATABASE_URL": 123,
            },
            "loc": (
                "db",
                "USER",
            ),
            "msg": "Field required",
            "type": "missing",
        },
        {
            "input": {
                "DATABASE_URL": 123,
            },
            "loc": (
                "db",
                "PASSWORD",
            ),
            "msg": "Field required",
            "type": "missing",
        },
    ]

    with pytest.raises(pydantic.ValidationError) as excinfo:
        DatabaseConfig(db={"database_url": "postgresql://user:password@localhost:6432"})

    assert "missing the `DATABASE`" in str(excinfo.value)

    # data = {"db": {"database_url": ["db", "postgresql://user:password@localhost:6432/test"]}}
    data = {"db": ["db", "postgresql://user:password@localhost:6432/test"]}
    with pytest.raises(pydantic.ValidationError) as excinfo:
        DatabaseConfig(**data)

    assert excinfo.value.errors(include_url=False) == [
        {
            "ctx": {
                "class_name": "PostgreSQL",
            },
            "input": [
                "db",
                "postgresql://user:password@localhost:6432/test",
            ],
            "loc": ("db",),
            "msg": "Input should be a valid dictionary or instance of PostgreSQL",
            "type": "model_type",
        },
    ]


# @pytest.mark.current
@pytest.mark.connectors
def test_postgres_driver(cwd_to_tmp, path_base_dir):
    class DatabaseConfig(ArFiSettings):
        db: PostgreSQL

    data = {"db": {"database_url": "postgresql+asyncpg://user:password@localhost:5432/test"}}
    config = DatabaseConfig(**data)
    assert config.db.DRIVER == "asyncpg"

    with pytest.raises(pydantic.ValidationError) as excinfo:
        DatabaseConfig(db={"database_url": "postgresql+driver://user:password@localhost:5432/test"})

    assert excinfo.value.errors(include_url=False) == [
        {
            "ctx": {
                "expected": "'', 'asyncpg', 'pg8000', 'psycopg', 'psycopg2', 'psycopg2cffi', "
                "'py-postgresql' or 'pygresql'",
            },
            "input": "driver",
            "loc": (
                "db",
                "DRIVER",
            ),
            "msg": "Input should be '', 'asyncpg', 'pg8000', 'psycopg', 'psycopg2', "
            "'psycopg2cffi', 'py-postgresql' or 'pygresql'",
            "type": "literal_error",
        },
        {
            "ctx": {
                "expected_schemes": "'postgres', 'postgresql', 'postgresql+asyncpg', "
                "'postgresql+pg8000', 'postgresql+psycopg', 'postgresql+psycopg2', "
                "'postgresql+psycopg2cffi', 'postgresql+py-postgresql' or "
                "'postgresql+pygresql'",
            },
            "input": MultiHostUrl("postgresql+driver://user:password@localhost:5432/test"),
            "loc": (
                "db",
                "DATABASE_URL",
            ),
            "msg": "URL scheme should be 'postgres', 'postgresql', 'postgresql+asyncpg', "
            "'postgresql+pg8000', 'postgresql+psycopg', 'postgresql+psycopg2', "
            "'postgresql+psycopg2cffi', 'postgresql+py-postgresql' or "
            "'postgresql+pygresql'",
            "type": "url_scheme",
        },
    ]


# @pytest.mark.current
@pytest.mark.connectors
def test_postgres_schema(cwd_to_tmp, path_base_dir):
    class DatabaseConfig(ArFiSettings):
        db: PostgreSQL

    with pytest.raises(pydantic.ValidationError) as excinfo:
        DatabaseConfig(db={"database_url": "postgres+asyncpg://user:password@localhost:6432/test"})

    assert excinfo.value.errors(include_url=False) == [
        {
            "ctx": {
                "expected_schemes": "'postgres', 'postgresql', 'postgresql+asyncpg', "
                "'postgresql+pg8000', 'postgresql+psycopg', 'postgresql+psycopg2', "
                "'postgresql+psycopg2cffi', 'postgresql+py-postgresql' or "
                "'postgresql+pygresql'",
            },
            "input": MultiHostUrl("postgres+asyncpg://user:password@localhost:6432/test"),
            "loc": (
                "db",
                "DATABASE_URL",
            ),
            "msg": "URL scheme should be 'postgres', 'postgresql', 'postgresql+asyncpg', "
            "'postgresql+pg8000', 'postgresql+psycopg', 'postgresql+psycopg2', "
            "'postgresql+psycopg2cffi', 'postgresql+py-postgresql' or "
            "'postgresql+pygresql'",
            "type": "url_scheme",
        },
    ]


# @pytest.mark.current
@pytest.mark.connectors
def test_mysql_defaul_param(cwd_to_tmp, path_base_dir):
    config_dir = cwd_to_tmp / "config"
    config_dir.mkdir()
    conf_file = config_dir / "config.toml"
    conf_file.write_text(
        """
        [DB]
        HOST = "127.0.0.1"
        USER = "root"
        PASSWORD = "password"
        DATABASE = "database"
        """
    )

    class DatabaseConfig(ArFiSettings):
        db: MySQL

    config = DatabaseConfig()
    assert config.db.DIALECT == "mysql"
    assert config.db.DRIVER == ""
    assert config.db.HOST == "127.0.0.1"
    assert config.db.PORT == 3306
    assert config.db.USER == "root"
    assert config.db.PASSWORD == "password"
    assert config.db.DATABASE == "database"
    assert str(config.db.DATABASE_URL) == "mysql://root:password@127.0.0.1:3306/database"
    assert config.db.database_uri == "mysql://root:password@127.0.0.1:3306/database"


# @pytest.mark.current
@pytest.mark.connectors
def test_mysql_database_url(cwd_to_tmp, path_base_dir):
    class DatabaseConfig(ArFiSettings):
        db: MySQL

    data = {"db": {"database_url": "mysql://user:password@localhost:1234/test"}}
    config = DatabaseConfig(**data)
    assert config.db.DIALECT == "mysql"
    assert config.db.DRIVER == ""
    assert config.db.HOST == "localhost"
    assert config.db.PORT == 1234
    assert config.db.USER == "user"
    assert config.db.PASSWORD == "password"
    assert config.db.DATABASE == "test"
    assert str(config.db.DATABASE_URL) == "mysql://user:password@localhost:1234/test"
    assert config.db.database_uri == "mysql://user:password@localhost:1234/test"


# @pytest.mark.current
@pytest.mark.connectors
def test_mysql_driver(cwd_to_tmp, path_base_dir):
    class DatabaseConfig(ArFiSettings):
        db: MySQL

    data = {"db": {"database_url": "mysql+asyncmy://user:password@localhost:3306/test"}}
    config = DatabaseConfig(**data)
    assert config.db.DRIVER == "asyncmy"

    with pytest.raises(pydantic.ValidationError) as excinfo:
        DatabaseConfig(db={"database_url": "mysql+driver://user:password@localhost:3306/test"})

    assert excinfo.value.errors(include_url=False) == [
        {
            "ctx": {
                "expected": "'', 'mysqlconnector', 'aiomysql', 'asyncmy', 'mysqldb', "
                "'pymysql', 'cymysql' or 'pyodbc'",
            },
            "input": "driver",
            "loc": (
                "db",
                "DRIVER",
            ),
            "msg": "Input should be '', 'mysqlconnector', 'aiomysql', 'asyncmy', "
            "'mysqldb', 'pymysql', 'cymysql' or 'pyodbc'",
            "type": "literal_error",
        },
        {
            "ctx": {
                "expected_schemes": "'mysql', 'mysql+mysqlconnector', 'mysql+aiomysql', "
                "'mysql+asyncmy', 'mysql+mysqldb', 'mysql+pymysql', "
                "'mysql+cymysql' or 'mysql+pyodbc'",
            },
            "input": Url("mysql+driver://user:password@localhost:3306/test"),
            "loc": (
                "db",
                "DATABASE_URL",
            ),
            "msg": "URL scheme should be 'mysql', 'mysql+mysqlconnector', "
            "'mysql+aiomysql', 'mysql+asyncmy', 'mysql+mysqldb', 'mysql+pymysql', "
            "'mysql+cymysql' or 'mysql+pyodbc'",
            "type": "url_scheme",
        },
    ]


#
