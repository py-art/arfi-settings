from typing import Any, ClassVar, Literal

from pydantic import (
    MySQLDsn,
    PostgresDsn,
    UrlConstraints,
    model_validator,
)
from pydantic_core import MultiHostUrl, Url
from typing_extensions import Annotated, Self

from arfi_settings import ArFiSettings, SettingsConfigDict

__all__ = [
    "BaseDatabase",
    "AdvancedDatabase",
    "PostgreSQL",
    "MySQL",
    "SQLite",
    "SqLiteDsn",
]

SqLiteDsn = Annotated[
    Url,
    UrlConstraints(
        allowed_schemes=[
            "sqlite",
            "sqlite+pysqlite",
            "sqlite+aiosqlite",
        ],
        default_path="/:memory:",
    ),
]

ALLOWED_SQLITE_DRIVERS = Literal[
    "",
    "pysqlite",
    "aiosqlite",
]

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


class BaseDatabase(ArFiSettings):
    """Base class for simple database."""

    mode_dir = "db"
    env_config_inherit_parent = False
    Dsn: ClassVar[Url | MultiHostUrl] = None
    DIALECT: str
    DRIVER: str = ""
    DATABASE: str = ""
    DATABASE_URL: str = ""

    model_config = SettingsConfigDict(
        env_prefix_as_source_mode_dir=True,
        validate_default=False,
        validate_return=True,
        validate_assignment=True,
    )

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.Dsn is None:
            if cls.__name__ != "AdvancedDatabase":
                raise TypeError(f"{cls.__name__}: missing the `Dsn` class variable.")

    @property
    def scheme(self) -> str:
        if self.DRIVER:
            return f"{self.DIALECT}+{self.DRIVER}"
        return self.DIALECT

    @property
    def database_uri(self) -> str:
        """Computed database uri."""
        raise NotImplementedError(f"{self.__class__.__name__}: does not implement the `database_uri` property.")

    @model_validator(mode="before")
    @classmethod
    def check_database_url_before(cls, data: Any) -> Any:
        """Check database url."""
        raise NotImplementedError(f"{cls.__name__}: does not implement the `check_database_url_before` method.")

    @model_validator(mode="after")
    def create_database_url_after(self) -> Self:
        """Create database url."""
        raise NotImplementedError(
            f"{self.__class__.__name__}: does not implement the `create_database_url_after` method."
        )


class AdvancedDatabase(BaseDatabase):
    """Base class for advanced database."""

    mode_dir = None
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str

    @property
    def database_uri(self) -> str:
        uri = MultiHostUrl.build(
            scheme=self.scheme,
            username=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=self.PORT,
            path=self.DATABASE,
        )
        return str(uri)

    @model_validator(mode="before")
    @classmethod
    def check_database_url_before(cls, data: Any) -> Self:
        if isinstance(data, dict):
            if database_url := data.get("DATABASE_URL"):
                if isinstance(database_url, str):
                    database_url = cls.Dsn(database_url)
                data["DATABASE_URL"] = database_url
                if issubclass(type(database_url), (Url, MultiHostUrl)):
                    if "+" in database_url.scheme:
                        data["DRIVER"] = database_url.scheme.split("+")[1]
                    if issubclass(type(database_url), MultiHostUrl):
                        host_data = database_url.hosts()[0]
                        data["HOST"] = host_data["host"]
                        data["PORT"] = host_data["port"]
                        data["USER"] = host_data["username"]
                        data["PASSWORD"] = host_data["password"]
                    else:
                        data["HOST"] = database_url.host
                        data["PORT"] = database_url.port
                        data["USER"] = database_url.username
                        data["PASSWORD"] = database_url.password
                    if database_url.path:
                        data["DATABASE"] = database_url.path[1:]
        return data

    @model_validator(mode="after")
    def create_database_url_after(self) -> Self:
        if not self.DATABASE_URL:
            self.DATABASE_URL = self.Dsn(self.database_uri)
        if not self.DATABASE:
            raise ValueError(f"{self.__class__.__name__}: missing the `DATABASE`.")
        return self


class SQLite(BaseDatabase):
    """SQLite database."""

    mode_dir = "sqlite"
    Dsn: ClassVar[type[Url]] = SqLiteDsn
    DIALECT: Literal["sqlite"] = "sqlite"
    DRIVER: ALLOWED_SQLITE_DRIVERS = ""
    DATABASE: str = ":memory:"
    DATABASE_URL: SqLiteDsn = ""

    @property
    def database_uri(self) -> str:
        return f"{self.scheme}:///{self.DATABASE}"

    @model_validator(mode="before")
    @classmethod
    def check_database_url_before(cls, data: Any) -> Self:
        if isinstance(data, dict):
            if database_url := data.get("DATABASE_URL"):
                if isinstance(database_url, str):
                    error_message = f"{cls.__name__}.DATABASE_URL={database_url} incorrect url."
                    if "://" not in database_url:
                        raise ValueError(error_message)
                    database_url = cls.Dsn(database_url)
                    if database_url.host:
                        raise ValueError(error_message)
                data["DATABASE_URL"] = database_url
                if issubclass(type(database_url), Url):
                    if "+" in database_url.scheme:
                        data["DRIVER"] = database_url.scheme.split("+")[1]
                    if database_url.path:
                        database = database_url.path[1:]
                        if not database:
                            database = ":memory:"
                        data["DATABASE"] = database
        return data

    @model_validator(mode="after")
    def create_database_url_after(self) -> Self:
        if not self.DATABASE_URL:
            self.DATABASE_URL = self.Dsn(self.database_uri)
        if not self.DATABASE_URL.path or not self.DATABASE_URL.path[1:]:
            self.DATABASE_URL.path = "/:memory:"
        return self


class MySQL(AdvancedDatabase):
    """MySQL database."""

    mode_dir = "mysql"
    Dsn: ClassVar[MySQLDsn] = MySQLDsn
    DIALECT: Literal["mysql"] = "mysql"
    DRIVER: ALLOWED_MYSQL_DRIVERS = ""
    PORT: int = 3306
    DATABASE_URL: MySQLDsn = ""


class PostgreSQL(AdvancedDatabase):
    """PostgreSQL database."""

    mode_dir = "postgres"
    Dsn: ClassVar[PostgresDsn] = PostgresDsn
    DIALECT: Literal["postgresql"] = "postgresql"
    DRIVER: ALLOWED_POSTGRES_DRIVERS = ""
    PORT: int = 5432
    DATABASE_URL: PostgresDsn = ""
