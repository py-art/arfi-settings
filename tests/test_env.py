from typing import Literal, Any

import pytest
from pydantic import AliasChoices, Field, BaseModel, AliasPath

from arfi_settings import ArFiSettings, EnvConfigDict


class DataBase(ArFiSettings):
    mode_dir = "db"
    DIALECT: str = Field(..., validation_alias=AliasChoices("dialect", "DIALECT"))
    # DATABASE_URL: str


class SQLite(DataBase):
    mode_dir = "sqlite"
    DIALECT: Literal["sqlite"] = "sqlite"
    DATABASE_URL: str = "sqlite:///:memory:"


class MySQL(DataBase):
    mode_dir = "mysql"
    DIALECT: Literal["mysql"] = "mysql"
    HOST: str = "mysql_default_host"
    PORT: int = 3306
    USER: str = "mysql_default_user"
    PASSWORD: str = "mysql_default_password"
    DATABASE: str = "mysql_default_database"


class Postgres(DataBase):
    mode_dir = "postgres"
    DIALECT: Literal["postgres"] = "postgres"
    HOST: str = "postgres_default_host"
    PORT: int = 5432
    USER: str = "postgres_default_user"
    PASSWORD: str = "postgres_default_password"
    DATABASE: str = "postgres_default_database"


# @pytest.mark.current
@pytest.mark.env
def test_simple_env_data(monkeypatch, cwd_to_tmp, path_base_dir):
    monkeypatch.setenv("PATH_FILE", "test.txt")

    class AppConfig(ArFiSettings):
        path_file: str = "default_path_file"

    config = AppConfig()
    assert config.path_file == "test.txt"


# @pytest.mark.current
@pytest.mark.env
def test_discriminator_default_env(cwd_to_tmp, path_base_dir):
    class AppConfig(ArFiSettings):
        db: SQLite | MySQL | Postgres = Field(SQLite(), discriminator="DIALECT")
        ordered_settings = ["env"]

    config = AppConfig()
    assert config.db.DIALECT == "sqlite"
    assert config.db.DATABASE_URL == "sqlite:///:memory:"


# @pytest.mark.current
@pytest.mark.env
def test_discriminator_as_json_env(monkeypatch, cwd_to_tmp, path_base_dir):
    monkeypatch.setenv("db", '{"DIALECT":"sqlite"}')

    class AppConfig(ArFiSettings):
        db: SQLite | MySQL | Postgres = Field(discriminator="DIALECT")
        ordered_settings = ["env"]

    config = AppConfig()
    assert config.db.DIALECT == "sqlite"
    assert config.db.DATABASE_URL == "sqlite:///:memory:"


# @pytest.mark.current
@pytest.mark.env
def test_pydantic_single_field_env(monkeypatch, cwd_to_tmp, path_base_dir):
    class AppSettings(BaseModel):
        name: str = "default_name"
        Value: str = "default_value"

    class AppConfig(ArFiSettings):
        app: AppSettings

    monkeypatch.setenv("APP", '{"NAME": "json_NAME", "VALUE": "json_VALUE"}')
    config = AppConfig()
    assert config.app.name == "json_NAME"
    assert config.app.Value == "json_VALUE"

    monkeypatch.setenv("app", '{"name": "json_name", "Value": "json_Value"}')
    config = AppConfig()
    assert config.app.name == "json_name"
    assert config.app.Value == "json_Value"

    class AppConfig(ArFiSettings):
        app: AppSettings
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("APP__NAME", "APP__NAME")
    monkeypatch.setenv("APP__VALUE", "APP__VALUE")
    config = AppConfig()
    assert config.app.name == "APP__NAME"
    assert config.app.Value == "APP__VALUE"

    monkeypatch.setenv("APP__name", "APP__name")
    monkeypatch.setenv("APP__Value", "APP__Value")
    config = AppConfig()
    assert config.app.name == "APP__name"
    assert config.app.Value == "APP__Value"

    monkeypatch.setenv("app__NAME", "app__NAME")
    monkeypatch.setenv("app__VALUE", "app__VALUE")
    config = AppConfig()
    assert config.app.name == "app__NAME"
    assert config.app.Value == "app__VALUE"

    monkeypatch.setenv("app__name", "app__name")
    monkeypatch.setenv("app__Value", "app__Value")
    config = AppConfig()
    assert config.app.name == "app__name"
    assert config.app.Value == "app__Value"


# @pytest.mark.current
@pytest.mark.env
def test_pydantic_single_field_nested_env(
    monkeypatch,
    cwd_to_tmp,
    path_base_dir,
    platform_system,
):
    class Proxy(BaseModel):
        host: str = "default_host"
        port: str = "default_port"

    class AppSettings(BaseModel):
        Name: str = "default_name"
        proxy: Proxy

    class AppConfig(ArFiSettings):
        app: AppSettings
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv(
        "APP",
        '{"NAME": "APP_json_NAME", "PROXY": {"HOST": "APP_json_HOST", "PORT": "APP_json_PORT"}}',
    )
    config = AppConfig()
    assert config.app.Name == "APP_json_NAME"
    assert config.app.proxy.host == "APP_json_HOST"
    assert config.app.proxy.port == "APP_json_PORT"

    monkeypatch.setenv(
        "APP",
        '{"Name": "APP_json_Name", "ProXY": {"HosT": "APP_json_HosT", "PorT": "APP_json_PorT"}}',
    )
    config = AppConfig()
    assert config.app.Name == "APP_json_Name"
    assert config.app.proxy.host == "APP_json_HosT"
    assert config.app.proxy.port == "APP_json_PorT"

    monkeypatch.setenv(
        "app",
        '{"Name": "app_json_Name", "ProXY": {"HosT": "app_json_HosT", "PorT": "app_json_PorT"}}',
    )
    config = AppConfig()
    assert config.app.Name == "app_json_Name"
    assert config.app.proxy.host == "app_json_HosT"
    assert config.app.proxy.port == "app_json_PorT"

    monkeypatch.setenv(
        "app",
        '{"Name": "app_json_Name", "proxy": {"host": "app_json_host", "PORT": "app_json_PORT"}}',
    )
    config = AppConfig()
    assert config.app.Name == "app_json_Name"
    assert config.app.proxy.host == "app_json_host"
    assert config.app.proxy.port == "app_json_PORT"

    monkeypatch.setenv("APP__NAME", "APP__NAME")
    monkeypatch.setenv("APP__PROXY", '{"HOST": "APP__HOST", "PORT": "APP__PORT"}')
    config = AppConfig()
    assert config.app.Name == "APP__NAME"
    assert config.app.proxy.host == "APP__HOST"
    assert config.app.proxy.port == "APP__PORT"

    monkeypatch.setenv("app__PROXY", '{"HosT": "app__HosT", "PORT": "app__PorT"}')
    config = AppConfig()
    assert config.app.proxy.host == "app__HosT"
    assert config.app.proxy.port == "app__PorT"

    monkeypatch.setenv("app__proxy", '{"Host": "app__Host", "Port": "app__Port"}')
    config = AppConfig()
    assert config.app.proxy.host == "app__Host"
    assert config.app.proxy.port == "app__Port"

    monkeypatch.setenv("APP__PROXY__HOST", "APP__PROXY__HOST")
    monkeypatch.setenv("APP__PROXY__PORT", "APP__PROXY__PORT")
    config = AppConfig()
    assert config.app.proxy.host == "APP__PROXY__HOST"
    assert config.app.proxy.port == "APP__PROXY__PORT"

    monkeypatch.setenv("APP__proxy__HOST", "APP__proxy__HOST")
    monkeypatch.setenv("APP__proxy__PORT", "APP__proxy__PORT")
    config = AppConfig()
    assert config.app.proxy.host == "APP__proxy__HOST"
    assert config.app.proxy.port == "APP__proxy__PORT"

    monkeypatch.setenv("APP__proxy__host", "APP__proxy__host")
    monkeypatch.setenv("APP__proxy__port", "APP__proxy__port")
    config = AppConfig()
    assert config.app.proxy.host == "APP__proxy__host"
    assert config.app.proxy.port == "APP__proxy__port"

    monkeypatch.setenv("app__PROXY__HOST", "app__PROXY__HOST")
    monkeypatch.setenv("app__PROXY__PORT", "app__PROXY__PORT")
    config = AppConfig()
    assert config.app.proxy.host == "app__PROXY__HOST"
    assert config.app.proxy.port == "app__PROXY__PORT"

    monkeypatch.setenv("app__proxy__HOST", "app__proxy__HOST")
    monkeypatch.setenv("app__proxy__PORT", "app__proxy__PORT")
    config = AppConfig()
    assert config.app.proxy.host == "app__proxy__HOST"
    assert config.app.proxy.port == "app__proxy__PORT"

    monkeypatch.setenv("app__proxy__host", "app__proxy__host")
    monkeypatch.setenv("app__proxy__port", "app__proxy__port")
    config = AppConfig()
    assert config.app.proxy.host == "app__proxy__host"
    assert config.app.proxy.port == "app__proxy__port"

    class AppConfig(ArFiSettings):
        app: AppSettings
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
            env_case_sensitive=True,
        )

    monkeypatch.setenv("app__Name", "app__Name")
    if platform_system.lower() != "windows":
        config = AppConfig()
        # TODO: investigate windows
        assert config.app.Name == "app__Name"
        assert config.app.proxy.host == "app__proxy__host"
        assert config.app.proxy.port == "app__proxy__port"


# @pytest.mark.current
@pytest.mark.env
def test_pydantic_single_field_nested_with_alias_choises_json_env(monkeypatch, cwd_to_tmp, path_base_dir):
    class Proxy(BaseModel):
        host: str = Field(validation_alias=AliasChoices("my_host", "hOsT"))
        port: str = Field(validation_alias=AliasChoices("PORT", "my_port"))

    class AppSettings(BaseModel):
        proxy: Proxy = Field(validation_alias=AliasChoices("MY_PROXY", "proxy"))

    class AppConfig(ArFiSettings):
        app: AppSettings = Field(validation_alias=AliasChoices("my_app", "APP"))
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv(
        "app",
        '{"PROXY": {"HOST": "app_PROXY_json_HOST", "MY_PORT": "app_PROXY_json_MY_PORT"}}',
    )
    config = AppConfig()
    assert config.app.proxy.host == "app_PROXY_json_HOST"
    assert config.app.proxy.port == "app_PROXY_json_MY_PORT"

    monkeypatch.setenv(
        "app",
        '{"Proxy": {"MY_HOST": "app_Proxy_json_MY_HOST", "PORT": "app_Proxy_json_PORT"}}',
    )
    config = AppConfig()
    assert config.app.proxy.host == "app_Proxy_json_MY_HOST"
    assert config.app.proxy.port == "app_Proxy_json_PORT"

    monkeypatch.setenv(
        "APP",
        '{"MY_PROXY": {"MY_HOST": "APP_MY_PROXY_json_MY_HOST", "PORT": "APP_MY_PROXY_json_MY_PORT"}}',
    )
    config = AppConfig()
    assert config.app.proxy.host == "APP_MY_PROXY_json_MY_HOST"
    assert config.app.proxy.port == "APP_MY_PROXY_json_MY_PORT"

    monkeypatch.setenv(
        "MY_APP",
        '{"Proxy": {"hOst": "MY_APP_Proxy_json_hOst", "MY_port": "MY_APP_Proxy_json_MY_port"}}',
    )
    config = AppConfig()
    assert config.app.proxy.host == "MY_APP_Proxy_json_hOst"
    assert config.app.proxy.port == "MY_APP_Proxy_json_MY_port"

    monkeypatch.setenv(
        "MY_APP",
        '{"my_proxy": {"MY_HOST": "MY_APP_my_proxy_json_MY_HOST", "my_PORT": "MY_APP_my_proxy_json_my_PORT"}}',
    )
    config = AppConfig()
    assert config.app.proxy.host == "MY_APP_my_proxy_json_MY_HOST"
    assert config.app.proxy.port == "MY_APP_my_proxy_json_my_PORT"

    monkeypatch.setenv(
        "my_app",
        '{"MY_PROXY": {"my_host": "my_app_MY_PROXY_json_my_host", "PORT": "my_app_MY_PROXY_json_PORT"}}',
    )
    config = AppConfig()
    assert config.app.proxy.host == "my_app_MY_PROXY_json_my_host"
    assert config.app.proxy.port == "my_app_MY_PROXY_json_PORT"


# @pytest.mark.current
@pytest.mark.env
def test_pydantic_single_field_nested_with_alias_choises_env(
    monkeypatch,
    cwd_to_tmp,
    path_base_dir,
    platform_system,
):
    class Proxy(BaseModel):
        host: str = Field(validation_alias=AliasChoices("my_host", "hOsT"))
        port: str = Field(validation_alias=AliasChoices("PORT", "my_port"))

    class AppSettings(BaseModel):
        proxy: Proxy = Field(validation_alias=AliasChoices("MY_PROXY", "proxy"))

    class AppConfig(ArFiSettings):
        app: AppSettings = Field(validation_alias=AliasChoices("my_app", "APP"))
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("app__PROXY__HOST", "app__PROXY__HOST")
    monkeypatch.setenv("app__PROXY__MY_PORT", "app__PROXY__MY_PORT")
    config = AppConfig()
    assert config.app.proxy.host == "app__PROXY__HOST"
    assert config.app.proxy.port == "app__PROXY__MY_PORT"

    monkeypatch.setenv("app__proxy__HOST", "app__proxy__HOST")
    monkeypatch.setenv("app__proxy__my_port", "app__proxy__my_port")
    config = AppConfig()
    assert config.app.proxy.host == "app__proxy__HOST"
    assert config.app.proxy.port == "app__proxy__my_port"

    monkeypatch.setenv("app__proxy__host", "app__proxy__host")
    monkeypatch.setenv("app__PROXY__PORT", "app__PROXY__PORT")
    config = AppConfig()
    assert config.app.proxy.host == "app__proxy__host"
    assert config.app.proxy.port == "app__PROXY__PORT"

    monkeypatch.setenv("app__PROXY__hOst", "app__PROXY__hOst")
    monkeypatch.setenv("app__proxy__port", "app__proxy__port")
    config = AppConfig()
    assert config.app.proxy.host == "app__PROXY__hOst"
    assert config.app.proxy.port == "app__proxy__port"

    monkeypatch.setenv("app__proxy__hOst", "app__proxy__hOst")
    monkeypatch.setenv("app__proxy__PORT", "app__proxy__PORT")
    config = AppConfig()
    assert config.app.proxy.host == "app__proxy__hOst"
    assert config.app.proxy.port == "app__proxy__PORT"

    monkeypatch.setenv("APP__MY_PROXY__MY_HOST", "APP__MY_PROXY__MY_HOST")
    monkeypatch.setenv("APP__MY_PROXY__MY_PORT", "APP__MY_PROXY__MY_PORT")
    config = AppConfig()
    assert config.app.proxy.host == "APP__MY_PROXY__MY_HOST"
    assert config.app.proxy.port == "APP__MY_PROXY__MY_PORT"

    monkeypatch.setenv("MY_APP__Proxy__hOst", "MY_APP__Proxy__hOst")
    monkeypatch.setenv("MY_APP__Proxy__MY_port", "MY_APP__Proxy__MY_port")
    config = AppConfig()
    assert config.app.proxy.host == "MY_APP__Proxy__hOst"
    assert config.app.proxy.port == "MY_APP__Proxy__MY_port"

    monkeypatch.setenv("MY_APP__my_proxy__MY_HOST", "MY_APP__my_proxy__MY_HOST")
    monkeypatch.setenv("MY_APP__my_proxy__my_PORT", "MY_APP__my_proxy__my_PORT")
    config = AppConfig()
    assert config.app.proxy.host == "MY_APP__my_proxy__MY_HOST"
    assert config.app.proxy.port == "MY_APP__my_proxy__my_PORT"

    monkeypatch.setenv("my_app__MY_PROXY__my_host", "my_app__MY_PROXY__my_host")
    monkeypatch.setenv("my_app__MY_PROXY__PORT", "my_app__MY_PROXY__PORT")
    config = AppConfig()
    assert config.app.proxy.host == "my_app__MY_PROXY__my_host"
    assert config.app.proxy.port == "my_app__MY_PROXY__PORT"

    class AppConfig(ArFiSettings):
        app: AppSettings = Field(validation_alias=AliasChoices("my_app", "APP"))
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
            env_case_sensitive=True,
        )

    if platform_system.lower() != "windows":
        # TODO: investigate windows
        config = AppConfig()
        assert config.app.proxy.host == "my_app__MY_PROXY__my_host"
        assert config.app.proxy.port == "my_app__MY_PROXY__PORT"


# @pytest.mark.current
@pytest.mark.env
def test_pydantic_single_field_nested_with_alias_choises_alias_path_env(monkeypatch, cwd_to_tmp, path_base_dir):
    class Proxy(BaseModel):
        host: str = Field(
            validation_alias=AliasChoices(
                "my_host",
                AliasPath("PROXY_PATH", 0),
            ),
        )
        port: str = Field(
            validation_alias=AliasChoices(
                AliasPath("PROXY_PATH", 1),
                "my_port",
            ),
        )

    class AppSettings(BaseModel):
        proxy: Proxy = Field(
            validation_alias=AliasChoices(
                "my_proxy",
                AliasPath("alias_path", 0),
            ),
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv(
        "app",
        '{"alias_path": [{"my_host": "app__alias_path__json_my_host", "my_port": "app__alias_path__json_my_port"}]}',
    )
    config = AppConfig()
    assert config.app.proxy.host == "app__alias_path__json_my_host"
    assert config.app.proxy.port == "app__alias_path__json_my_port"

    monkeypatch.setenv(
        "app__alias_path",
        '[{"my_host": "app__alias_path__my_host", "my_port": "app__alias_path__my_port"}]',
    )
    config = AppConfig()
    assert config.app.proxy.host == "app__alias_path__my_host"
    assert config.app.proxy.port == "app__alias_path__my_port"

    monkeypatch.setenv(
        "app__my_proxy",
        '{"PROXY_PATH": ["app__my_proxy__PROXY_PATH_json_host", "app__my_proxy__PROXY_PATH_json_port"]}',
    )
    config = AppConfig()
    assert config.app.proxy.host == "app__my_proxy__PROXY_PATH_json_host"
    assert config.app.proxy.port == "app__my_proxy__PROXY_PATH_json_port"

    monkeypatch.setenv("app__my_proxy__my_host", "app__my_proxy__my_host")
    monkeypatch.setenv("app__my_proxy__my_port", "app__my_proxy__my_port")
    config = AppConfig()
    assert config.app.proxy.host == "app__my_proxy__my_host"
    assert config.app.proxy.port == "app__my_proxy__my_port"

    monkeypatch.setenv(
        "app__my_proxy__PROXY_PATH", '["app__my_proxy__PROXY_PATH_0_host", "app__my_proxy__PROXY_PATH_1_port"]'
    )
    config = AppConfig()
    assert config.app.proxy.host == "app__my_proxy__my_host"
    assert config.app.proxy.port == "app__my_proxy__PROXY_PATH_1_port"


# @pytest.mark.current
@pytest.mark.env
def test_arfi_settings_single_field_env(monkeypatch, cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        name: str = "default_name"
        Value: str = "default_value"

    class AppConfig(ArFiSettings):
        app: AppSettings
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("APP", '{"NAME": "json_NAME", "VALUE": "json_VALUE"}')
    config = AppConfig()
    assert config.app.name == "json_NAME"
    assert config.app.Value == "json_VALUE"

    monkeypatch.setenv("app", '{"name": "json_name", "Value": "json_Value"}')
    config = AppConfig()
    assert config.app.name == "json_name"
    assert config.app.Value == "json_Value"

    monkeypatch.setenv("APP__NAME", "APP__NAME")
    monkeypatch.setenv("APP__VALUE", "APP__VALUE")
    config = AppConfig()
    assert config.app.name == "APP__NAME"
    assert config.app.Value == "APP__VALUE"

    monkeypatch.setenv("app__NAME", "app__NAME")
    monkeypatch.setenv("app__VALUE", "app__VALUE")
    config = AppConfig()
    assert config.app.name == "app__NAME"
    assert config.app.Value == "app__VALUE"

    monkeypatch.setenv("app__name", "app__name")
    monkeypatch.setenv("app__Value", "app__Value")
    config = AppConfig()
    assert config.app.name == "app__name"
    assert config.app.Value == "app__Value"

    monkeypatch.setenv("NAME", "simple_NAME")
    monkeypatch.setenv("VALUE", "simple_VALUE")

    class AppSettings(ArFiSettings):
        name: str = "default_name"
        Value: str = "default_value"

        env_config_inherit_parent = False

    class AppConfig(ArFiSettings):
        app: AppSettings
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    config = AppConfig()
    assert config.app.name == "simple_NAME"
    assert config.app.Value == "simple_VALUE"

    monkeypatch.setenv("name", "simple_name")
    monkeypatch.setenv("Value", "simple_Value")
    config = AppConfig()
    assert config.app.name == "simple_name"
    assert config.app.Value == "simple_Value"


# @pytest.mark.current
@pytest.mark.env
def test_arfi_settings_single_field_with_alias_env(monkeypatch, cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        name: str = Field("default_name", validation_alias=AliasChoices("MY_NAME", "name"))
        Value: str = Field("default_value", validation_alias=AliasChoices("Value", "MY_VALUE"))

    class AppConfig(ArFiSettings):
        app: AppSettings = Field(
            ...,
            validation_alias=AliasChoices(
                "my_app",
                "APP",
            ),
        )
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("app", '{"NAME": "app_json_NAME", "VALUE": "app_json_VALUE"}')
    config = AppConfig()
    assert config.app.name == "app_json_NAME"
    assert config.app.Value == "app_json_VALUE"

    monkeypatch.setenv("app", '{"MY_NAME": "app_json_MY_NAME", "MY_VALUE": "app_json_MY_VALUE"}')
    config = AppConfig()
    assert config.app.name == "app_json_MY_NAME"
    assert config.app.Value == "app_json_MY_VALUE"

    monkeypatch.setenv("APP", '{"NAME": "APP_json_NAME", "VALUE": "APP_json_VALUE"}')
    config = AppConfig()
    assert config.app.name == "APP_json_NAME"
    assert config.app.Value == "APP_json_VALUE"

    monkeypatch.setenv("MY_APP", '{"NAME": "MY_APP_json_NAME", "VALUE": "MY_APP_json_VALUE"}')
    config = AppConfig()
    assert config.app.name == "MY_APP_json_NAME"
    assert config.app.Value == "MY_APP_json_VALUE"

    monkeypatch.setenv("MY_APP", '{"name": "MY_APP_json_name", "MY_VALUE": "MY_APP_json_MY_VALUE"}')
    config = AppConfig()
    assert config.app.name == "MY_APP_json_name"
    assert config.app.Value == "MY_APP_json_MY_VALUE"

    monkeypatch.setenv("my_app", '{"NAME": "my_app_json_NAME", "VALUE": "my_app_json_VALUE"}')
    config = AppConfig()
    assert config.app.name == "my_app_json_NAME"
    assert config.app.Value == "my_app_json_VALUE"

    monkeypatch.setenv("app__NAME", "app__NAME")
    monkeypatch.setenv("app__my_value", "app__my_value")
    config = AppConfig()
    assert config.app.name == "app__NAME"
    assert config.app.Value == "app__my_value"

    monkeypatch.setenv("app__name", "app__name")
    monkeypatch.setenv("app__VALUE", "app__VALUE")
    config = AppConfig()
    assert config.app.name == "app__name"
    assert config.app.Value == "app__VALUE"

    monkeypatch.setenv("APP__name", "APP__name")
    monkeypatch.setenv("app__Value", "app__Value")
    config = AppConfig()
    assert config.app.name == "APP__name"
    assert config.app.Value == "app__Value"

    monkeypatch.setenv("my_app__name", "my_app__name")
    monkeypatch.setenv("my_app__MY_VALUE", "my_app__MY_VALUE")
    config = AppConfig()
    assert config.app.name == "my_app__name"
    assert config.app.Value == "my_app__MY_VALUE"

    monkeypatch.setenv("my_app__MY_NAME", "my_app__MY_NAME")
    monkeypatch.setenv("my_app__Value", "my_app__Value")
    config = AppConfig()
    assert config.app.name == "my_app__MY_NAME"
    assert config.app.Value == "my_app__Value"


# @pytest.mark.current
@pytest.mark.env
def test_discriminator_without_delimiter_env(monkeypatch, cwd_to_tmp, path_base_dir):
    try:
        monkeypatch.delenv("USER")
    except KeyError:
        pass

    class AppConfig(ArFiSettings):
        db: SQLite | MySQL | Postgres = Field(Postgres(), discriminator="DIALECT")

    config = AppConfig()
    assert config.db.DIALECT == "postgres"
    assert config.db.HOST == "postgres_default_host"
    assert config.db.PORT == 5432
    assert config.db.USER == "postgres_default_user"
    assert config.db.PASSWORD == "postgres_default_password"
    assert config.db.DATABASE == "postgres_default_database"

    monkeypatch.setenv("db", '{"DIALECT":"sqlite"}')

    class AppConfig(ArFiSettings):
        db: SQLite | MySQL | Postgres = Field(discriminator="DIALECT")

    config = AppConfig()
    assert config.db.DIALECT == "sqlite"
    assert config.db.DATABASE_URL == "sqlite:///:memory:"

    monkeypatch.setenv("DB_DIALECT", "mysql")
    config = AppConfig()
    assert config.db.DIALECT == "mysql"
    assert config.db.HOST == "mysql_default_host"
    assert config.db.PORT == 3306
    assert config.db.USER == "mysql_default_user"
    assert config.db.PASSWORD == "mysql_default_password"
    assert config.db.DATABASE == "mysql_default_database"

    monkeypatch.setenv("db_DIALECT", "postgres")
    monkeypatch.setenv("host", "postgres_host")
    monkeypatch.setenv("port", "5432")
    monkeypatch.setenv("user", "postgres_user")
    monkeypatch.setenv("password", "postgres_password")
    monkeypatch.setenv("database", "postgres_database")

    config = AppConfig()
    assert config.db.DIALECT == "postgres"
    assert config.db.HOST == "postgres_host"
    assert config.db.PORT == 5432
    assert config.db.USER == "postgres_user"
    assert config.db.PASSWORD == "postgres_password"
    assert config.db.DATABASE == "postgres_database"

    monkeypatch.setenv("HOST", "postgres_HOST")
    monkeypatch.setenv("PORT", "5432")
    monkeypatch.setenv("USER", "postgres_USER")
    monkeypatch.setenv("PASSWORD", "postgres_PASSWORD")
    monkeypatch.setenv("DATABASE", "postgres_DATABASE")
    config = AppConfig()
    assert config.db.DIALECT == "postgres"
    assert config.db.HOST == "postgres_HOST"
    assert config.db.PORT == 5432
    assert config.db.USER == "postgres_USER"
    assert config.db.PASSWORD == "postgres_PASSWORD"
    assert config.db.DATABASE == "postgres_DATABASE"


# @pytest.mark.current
@pytest.mark.env
def test_discriminator_with_nested_delimiter_env(monkeypatch, cwd_to_tmp, path_base_dir):
    try:
        monkeypatch.delenv("USER")
    except KeyError:
        pass
    monkeypatch.setenv("db", '{"DIALECT":"sqlite"}')
    monkeypatch.setenv("DB_DIALECT", "postgres")
    monkeypatch.setenv("DB__DIALECT", "mysql")

    class AppConfig(ArFiSettings):
        db: SQLite | MySQL | Postgres = Field(SQLite(), discriminator="DIALECT")
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("DB__HOST", "mysql_host_upper")
    monkeypatch.setenv("DB__PORT", "1111")
    monkeypatch.setenv("DB__USER", "mysql_user_upper")
    monkeypatch.setenv("DB__PASSWORD", "mysql_password_upper")
    monkeypatch.setenv("DB__DATABASE", "mysql_database_upper")
    config = AppConfig()
    assert config.db.DIALECT == "mysql"
    assert config.db.HOST == "mysql_host_upper"
    assert config.db.PORT == 1111
    assert config.db.USER == "mysql_user_upper"
    assert config.db.PASSWORD == "mysql_password_upper"
    assert config.db.DATABASE == "mysql_database_upper"

    monkeypatch.setenv("db__host", "mysql_host_lower")
    monkeypatch.setenv("db__port", "2222")
    monkeypatch.setenv("db__user", "mysql_user_lower")
    monkeypatch.setenv("db__password", "mysql_password_lower")
    monkeypatch.setenv("db__database", "mysql_database_lower")
    config = AppConfig()
    assert config.db.DIALECT == "mysql"
    assert config.db.HOST == "mysql_host_lower"
    assert config.db.PORT == 2222
    assert config.db.USER == "mysql_user_lower"
    assert config.db.PASSWORD == "mysql_password_lower"
    assert config.db.DATABASE == "mysql_database_lower"

    monkeypatch.setenv("db__HOST", "mysql_host")
    monkeypatch.setenv("db__PORT", "3306")
    monkeypatch.setenv("db__USER", "mysql_user")
    monkeypatch.setenv("db__PASSWORD", "mysql_password")
    monkeypatch.setenv("db__DATABASE", "mysql_database")
    config = AppConfig()
    assert config.db.DIALECT == "mysql"
    assert config.db.HOST == "mysql_host"
    assert config.db.PORT == 3306
    assert config.db.USER == "mysql_user"
    assert config.db.PASSWORD == "mysql_password"
    assert config.db.DATABASE == "mysql_database"


# @pytest.mark.current
@pytest.mark.env
def test_prefix_as_mode_dir_env(monkeypatch, cwd_to_tmp, path_base_dir):
    class Postgres(ArFiSettings):
        mode_dir = "postgres"
        HOST: str = "postgres_default_host"

    class AppConfig(ArFiSettings):
        db: Postgres

    config = AppConfig()
    assert config.db.HOST == "postgres_default_host"

    monkeypatch.setenv("host", "postgres_host")
    config = AppConfig()
    assert config.db.HOST == "postgres_host"

    class AppConfig(ArFiSettings):
        db: Postgres
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    config = AppConfig()
    assert config.db.HOST == "postgres_default_host"

    class Postgres(ArFiSettings):
        HOST: str = "postgres_default_host"

        mode_dir = "postgres"
        env_config_inherit_parent = False
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    class AppConfig(ArFiSettings):
        db: Postgres

    config = AppConfig()
    assert config.db.HOST == "postgres_default_host"

    monkeypatch.setenv("db__host", "db__host")

    class AppConfig(ArFiSettings):
        db: Postgres

        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    config = AppConfig()
    assert config.db.HOST == "db__host"

    monkeypatch.setenv("db__HOST", "db__HOST")
    config = AppConfig()
    assert config.db.HOST == "db__HOST"

    monkeypatch.setenv("postgres_host", "postgres_host")
    config = AppConfig()
    assert config.db.HOST == "postgres_host"

    monkeypatch.setenv("postgres_HOST", "postgres_HOST")
    config = AppConfig()
    assert config.db.HOST == "postgres_HOST"


# @pytest.mark.current
@pytest.mark.env
def test_prefix_as_mode_dir_with_discriminator_env(monkeypatch, cwd_to_tmp, path_base_dir):
    class AppConfig(ArFiSettings):
        db: SQLite | MySQL | Postgres = Field(SQLite(), discriminator="DIALECT")
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
            env_prefix_as_source_mode_dir=True,
        )

    config = AppConfig()
    assert config.db.DIALECT == "sqlite"

    monkeypatch.setenv("db", '{"DIALECT":"postgres"}')
    config = AppConfig()
    assert config.db.mode_dir == "db/postgres"
    assert config.db.DIALECT == "postgres"
    assert config.db.HOST == "postgres_default_host"
    assert config.db.PORT == 5432
    assert config.db.USER == "postgres_default_user"
    assert config.db.PASSWORD == "postgres_default_password"
    assert config.db.DATABASE == "postgres_default_database"

    monkeypatch.setenv("DB_DIALECT", "mysql")

    config = AppConfig()
    assert config.db.mode_dir == "db/mysql"
    assert config.db.DIALECT == "mysql"
    assert config.db.HOST == "mysql_default_host"
    assert config.db.PORT == 3306
    assert config.db.USER == "mysql_default_user"
    assert config.db.PASSWORD == "mysql_default_password"
    assert config.db.DATABASE == "mysql_default_database"

    class PostgresMODIFYED(Postgres):
        mode_dir = None
        env_config_inherit_parent = False
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    class AppConfig(ArFiSettings):
        db: SQLite | MySQL | PostgresMODIFYED = Field(SQLite(), discriminator="DIALECT")
        env_config = EnvConfigDict(
            env_prefix_as_source_mode_dir=True,
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("DB__DIALECT", "postgres")
    monkeypatch.setenv("DB__HOST", "db_host")
    monkeypatch.setenv("DB__PORT", "6666")
    monkeypatch.setenv("DB__USER", "db_user")
    monkeypatch.setenv("DB__PASSWORD", "db_password")
    monkeypatch.setenv("DB__DATABASE", "db_database")

    config = AppConfig()
    assert config.db.mode_dir == "db/postgres"
    assert config.db.DIALECT == "postgres"
    assert config.db.HOST == "db_host"
    assert config.db.PORT == 6666
    assert config.db.USER == "db_user"
    assert config.db.PASSWORD == "db_password"
    assert config.db.DATABASE == "db_database"

    monkeypatch.setenv("DB_POSTGRES_HOST", "DB_POSTGRES_HOST")
    monkeypatch.setenv("DB_POSTGRES_PORT", "4444")
    monkeypatch.setenv("DB_POSTGRES_USER", "DB_POSTGRES_USER")
    monkeypatch.setenv("DB_POSTGRES_PASSWORD", "DB_POSTGRES_PASSWORD")
    monkeypatch.setenv("DB_POSTGRES_DATABASE", "DB_POSTGRES_DATABASE")
    config = AppConfig()
    assert config.db.mode_dir == "db/postgres"
    assert config.db.HOST == "DB_POSTGRES_HOST"
    assert config.db.PORT == 4444
    assert config.db.USER == "DB_POSTGRES_USER"
    assert config.db.PASSWORD == "DB_POSTGRES_PASSWORD"
    assert config.db.DATABASE == "DB_POSTGRES_DATABASE"

    class SubModel(ArFiSettings):
        val: int = 0

        mode_dir = "test_sub_model"
        env_config_inherit_parent = False
        env_config = EnvConfigDict(
            env_prefix_as_source_mode_dir=True,
        )

    class AppSettings(ArFiSettings):
        name: str
        sub_model: SubModel

    class Proxy(ArFiSettings):
        host: str

    class AppConfig(ArFiSettings):
        db: SQLite | MySQL | PostgresMODIFYED = Field(SQLite(), discriminator="DIALECT")
        APP: AppSettings
        proxy: Proxy
        env_config = EnvConfigDict(
            env_nested_delimiter="__",
        )

    monkeypatch.setenv("app__name", "my_app")
    monkeypatch.setenv("TEST_SUB_MODEL_VAL", "9117")
    monkeypatch.setenv("proxy__host", "proxy__host")
    monkeypatch.setenv("db_postgres_HOST", "db_postgres_HOST")
    monkeypatch.setenv("db_postgres_PORT", "5555")
    monkeypatch.setenv("db_postgres_USER", "db_postgres_USER")
    monkeypatch.setenv("db_postgres_PASSWORD", "db_postgres_PASSWORD")
    monkeypatch.setenv("db_postgres_DATABASE", "db_postgres_DATABASE")
    config = AppConfig()
    assert config.APP.name == "my_app"
    assert config.APP.sub_model.val == 9117
    assert config.proxy.host == "proxy__host"
    assert config.db.mode_dir == "db/postgres"
    assert config.db.HOST == "db_postgres_HOST"
    assert config.db.PORT == 5555
    assert config.db.USER == "db_postgres_USER"
    assert config.db.PASSWORD == "db_postgres_PASSWORD"
    assert config.db.DATABASE == "db_postgres_DATABASE"

    class PostgresMODIFYED_2222(Postgres):
        mode_dir = "postgres"
        mode_dir_inherit_nested = False
        env_config_inherit_parent = False
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    class AppConfig(ArFiSettings):
        db: SQLite | MySQL | PostgresMODIFYED_2222 = Field(SQLite(), discriminator="DIALECT")
        env_config = EnvConfigDict(env_nested_delimiter="__")

    monkeypatch.setenv("POSTGRES_HOST", "postgres_host")
    monkeypatch.setenv("POSTGRES_PORT", "8888")
    monkeypatch.setenv("POSTGRES_USER", "postgres_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres_password")
    monkeypatch.setenv("POSTGRES_DATABASE", "postgres_database")
    config = AppConfig()
    assert config.db.mode_dir == "postgres"
    assert config.db.HOST == "postgres_host"
    assert config.db.PORT == 8888
    assert config.db.USER == "postgres_user"
    assert config.db.PASSWORD == "postgres_password"
    assert config.db.DATABASE == "postgres_database"


# @pytest.mark.current
@pytest.mark.env
def test_multi_env_prefix_as_mode_dir(monkeypatch, cwd_to_tmp, path_base_dir):
    class Nested(ArFiSettings):
        mode_dir = "nested"

    class Child(Nested):
        mode_dir = "child"
        name: str = "default_name_child"

        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_prefix_as_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        child: Child
        name: str = "default_name_app"

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings
        name: str = "default_name_config"

    monkeypatch.setenv("NAME", "NAME")
    monkeypatch.setenv("DEV_APP_NESTED_CHILD_NAME", "DEV_APP_NESTED_CHILD_NAME")
    config = AppConfig()
    assert config.name == "NAME"
    assert config.app.name == "NAME"
    assert config.app.child.name == "DEV_APP_NESTED_CHILD_NAME"

    class Child(Nested):
        mode_dir = "child"
        name: str = "default_name_child"

        env_config = EnvConfigDict(
            env_prefix_as_nested_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_prefix_as_nested_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        child: Child
        name: str = "default_name_app"
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings
        name: str = "default_name_config"

    monkeypatch.setenv("NESTED_CHILD_NAME", "NESTED_CHILD_NAME")
    config = AppConfig()
    assert config.name == "NAME"
    assert config.app.name == "NAME"
    assert config.app.child.name == "NESTED_CHILD_NAME"

    class AppSettings(ArFiSettings):
        child: Child
        name: str = "default_name_app"
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_exclude_inherit_parent",
                "env_prefix_as_mode_dir",
                "env_prefix_as_nested_mode_dir",
                "env_prefix_as_source_mode_dir",
            ],
        )

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings
        name: str = "default_name_config"

    monkeypatch.setenv("NESTED_CHILD_NAME", "NESTED_CHILD_NAME")
    monkeypatch.setenv("DEV_APP_NAME", "DEV_APP_NAME")
    config = AppConfig()
    assert config.name == "NAME"
    assert config.app.name == "DEV_APP_NAME"
    assert config.app.child.name == "NESTED_CHILD_NAME"

    class Child(Nested):
        mode_dir = "child"
        name: str = "default_name_child"

        env_config = EnvConfigDict(
            env_prefix_as_source_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_prefix_as_source_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        child: Child
        name: str = "default_name_app"
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_exclude_inherit_parent",
                "env_prefix_as_mode_dir",
                "env_prefix_as_nested_mode_dir",
                "env_prefix_as_source_mode_dir",
            ],
        )

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings
        name: str = "default_name_config"

    monkeypatch.setenv("CHILD_NAME", "CHILD_NAME")
    config = AppConfig()
    assert config.name == "NAME"
    assert config.app.name == "DEV_APP_NAME"
    assert config.app.child.name == "CHILD_NAME"

    class Child(Nested):
        mode_dir = "child"
        name: str = "default_name_child"

        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_exclude_inherit_parent",
                "env_prefix_as_mode_dir",
                "env_prefix_as_nested_mode_dir",
                "env_prefix_as_source_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        child: Child
        name: str = "default_name_app"
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_prefix_as_mode_dir",
                "env_prefix_as_source_mode_dir",
            ],
        )

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings
        name: str = "default_name_config"
        env_config = EnvConfigDict(
            env_prefix_as_source_mode_dir=True,
        )

    monkeypatch.setenv("DEV_NAME", "DEV_NAME")
    config = AppConfig()
    assert config.name == "DEV_NAME"
    assert config.app.name == "DEV_APP_NAME"
    assert config.app.child.name == "DEV_APP_NESTED_CHILD_NAME"

    class Child(Nested):
        mode_dir = "child"
        name: str = "default_name_child"

    class AppSettings(ArFiSettings):
        child: Child
        name: str = "default_name_app"

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings
        name: str = "default_name_config"
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    config = AppConfig()
    assert config.name == "DEV_NAME"
    assert config.app.name == "DEV_APP_NAME"
    assert config.app.child.name == "DEV_APP_NESTED_CHILD_NAME"

    monkeypatch.setenv("dev_name", "dev_name")
    monkeypatch.setenv("dev_app_name", "dev_app_name")
    monkeypatch.setenv("dev_app_nested_child_name", "dev_app_nested_child_name")
    config = AppConfig()
    assert config.name == "dev_name"
    assert config.app.name == "dev_app_name"
    assert config.app.child.name == "dev_app_nested_child_name"

    class Child(Nested):
        mode_dir = "child"
        mode_dir_inherit_nested = False
        name: str = "default_name_child"

    class AppSettings(ArFiSettings):
        child: Child
        name: str = "default_name_app"

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings
        name: str = "default_name_config"
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    monkeypatch.setenv("dev_app_child_name", "dev_app_child_name")
    config = AppConfig()
    assert config.name == "dev_name"
    assert config.app.name == "dev_app_name"
    assert config.app.child.name == "dev_app_child_name"


# @pytest.mark.current
@pytest.mark.env
def test_non_pydantic_field(monkeypatch, cwd_to_tmp, path_base_dir):
    class AppConfig(ArFiSettings):
        thing: Any = "default_thing"

    monkeypatch.setenv("thing", '{"key": "value"}')
    config = AppConfig()
    assert isinstance(config.thing, dict)
    assert config.thing == {"key": "value"}

    monkeypatch.setenv("thing", '{"key": "value",}')
    config = AppConfig()
    assert isinstance(config.thing, str)
    assert config.thing == '{"key": "value",}'

    class AppConfig(ArFiSettings):
        name: str = "default_name"

    monkeypatch.setenv("name", "name")
    config = AppConfig()
    assert config.name == "name"

    class AppConfig(ArFiSettings):
        gender: Literal["female", "male"] = "male"

    monkeypatch.setenv("gender", "female")
    config = AppConfig()
    assert config.gender == "female"

    class AppConfig(ArFiSettings):
        fruits: list[str] = ["apple", "banana"]

    monkeypatch.setenv("fruits", '["mango", "orange"]')
    config = AppConfig()
    assert config.fruits == ["mango", "orange"]

    class AppConfig(ArFiSettings):
        pets: tuple[str, ...] = ("cat", "dog")

    monkeypatch.setenv("pets", '["hamster", "rabbit"]')
    config = AppConfig()
    assert config.pets == ("hamster", "rabbit")

    class AppConfig(ArFiSettings):
        pets: str | tuple[str, ...] = ("cat", "dog")

    monkeypatch.setenv("pets", '("hamster", "rabbit")')
    config = AppConfig()
    assert config.pets == '("hamster", "rabbit")'

    class AppConfig(ArFiSettings):
        animals: set[str]

    monkeypatch.setenv("animals", '["panda", "elephant"]')
    config = AppConfig()
    assert config.animals == {"panda", "elephant"}

    class AppConfig(ArFiSettings):
        animals: str | set[str] | None = None

    monkeypatch.setenv("animals", '{"panda", "elephant"}')
    config = AppConfig()
    assert config.animals == '{"panda", "elephant"}'

    class AppConfig(ArFiSettings):
        animals: set[str] | Any = None

    monkeypatch.setenv("animals", '{"panda", "elephant"}')
    config = AppConfig()
    assert config.animals == '{"panda", "elephant"}'

    class AppConfig(ArFiSettings):
        numbers: dict[str, int]

    monkeypatch.setenv("numbers", '{"one": 1, "two": 2}')
    config = AppConfig()
    assert config.numbers == {"one": 1, "two": 2}

    class AppConfig(ArFiSettings):
        numbers: dict[str, int] | Any

    monkeypatch.setenv("numbers", '[{"one": 1, "two": 2}]')
    config = AppConfig()
    assert isinstance(config.numbers, list)
    assert config.numbers == [
        {"one": 1, "two": 2},
    ]
    monkeypatch.setenv("numbers", '[{"one": 1, "two": 2},]')
    config = AppConfig()
    assert isinstance(config.numbers, str)
    assert config.numbers == '[{"one": 1, "two": 2},]'

    class AppConfig(ArFiSettings):
        numbers: dict[str, int] | None

    monkeypatch.setenv("numbers", "null")
    config = AppConfig()
    assert config.numbers is None
