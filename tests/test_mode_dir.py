from pathlib import Path

import pytest

from arfi_settings import ArFiSettings
from arfi_settings.types import DEFAULT_PATH_SENTINEL


# @pytest.mark.current
@pytest.mark.mode_dir
def test_nested_mode_dir(cwd_to_tmp):
    class Database(ArFiSettings):
        mode_dir = "db"

    class Postgres(Database):
        mode_dir = "postgres"

    class AppConfig(ArFiSettings):
        # read_config = True
        db: Postgres = Postgres()

    config = AppConfig()
    assert config.db.mode_dir == "db/postgres"


# @pytest.mark.current
@pytest.mark.mode_dir
def test_mode_dir_inherit_nested(cwd_to_tmp):
    class Database(ArFiSettings):
        mode_dir = "db"

    class Postgres(Database):
        mode_dir = "postgres"
        mode_dir_inherit_nested = False

    class AppConfig(ArFiSettings):
        read_config = True
        db: Postgres = Postgres()

    config = AppConfig()
    assert config.db.mode_dir == "postgres"


# @pytest.mark.current
@pytest.mark.mode_dir
def test_mode_dir_inherit_nested_false(cwd_to_tmp):
    class Database(ArFiSettings):
        mode_dir = "db"

    class Postgres(Database):
        mode_dir_inherit_nested = False

    class AppConfig(ArFiSettings):
        read_config = True
        db: Database = Postgres()

    config = AppConfig()
    assert config.db.mode_dir == "db"


# @pytest.mark.current
@pytest.mark.mode_dir
def test_mode_dir_by_attr(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = True
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.app.mode_dir == "app"
    assert config.app.proxy.mode_dir == "proxy"
    assert config.app.proxy.mode_dir_path == Path("app/proxy")
    app_settings = AppSettings()
    assert app_settings.mode_dir == DEFAULT_PATH_SENTINEL


# @pytest.mark.current
@pytest.mark.mode_dir
def test_mode_dir_by_attr_inherit_parent_false(cwd_to_tmp):
    class Proxy(ArFiSettings):
        mode_dir_inherit_parent = False

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = True
        mode_dir = "dev"
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.app.mode_dir == "app"
    assert config.app.proxy.mode_dir == "proxy"
    assert config.app.mode_dir_path == Path("dev/app")
    assert config.app.proxy.mode_dir_path == Path("proxy")
    app_settings = AppSettings()
    assert app_settings.mode_dir == DEFAULT_PATH_SENTINEL


# @pytest.mark.current
@pytest.mark.mode_dir
def test_init_mode_dir(cwd_to_tmp):
    class Database(ArFiSettings):
        mode_dir = "db"

    class Postgres(Database):
        mode_dir = "postgres"

    class AppConfig(ArFiSettings):
        read_config = True
        db: Postgres
        pg: Postgres = Postgres(_mode_dir="pg")
        prod_postgres: Postgres = Postgres(_mode_dir="prod_postgres")
        test_db: Postgres = Postgres()
        mdb: Postgres = Postgres(_mode_dir="mdb", _mode_dir_inherit_nested=False)

    config = AppConfig()
    assert config.db.mode_dir == "db/postgres"
    assert config.pg.mode_dir == "db/pg"
    assert config.prod_postgres.mode_dir == "db/prod_postgres"
    assert config.test_db.mode_dir == "db/postgres"
    assert config.mdb.mode_dir == "mdb"

    pg_conf = Postgres(_mode_dir="pg", MODE="pg")
    assert pg_conf.read_config
    assert pg_conf.MODE == "pg"
    assert pg_conf.mode_dir == "db/pg"


# @pytest.mark.current
@pytest.mark.mode_dir
def test_nested_with_init_mode_dir(cwd_to_tmp):
    class Database(ArFiSettings):
        mode_dir = "db"

    class Postgres(Database):
        mode_dir = "postgres"

    class AppConfig(ArFiSettings):
        read_config = True
        db: Postgres = Postgres()

    config = AppConfig()
    assert config.db.mode_dir == "db/postgres"

    class QuerySettings(ArFiSettings):
        db: Postgres = Postgres(_mode_dir="query")

    q = QuerySettings()
    assert q.db.mode_dir == "db/query"


# @pytest.mark.current
@pytest.mark.mode_dir
def test_parent_mode_dir(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        proxy: Proxy

    class AppConfig(ArFiSettings):
        # read_config = True
        app: AppSettings

    config = AppConfig()
    assert config.app.mode_dir == "app"
    assert config.app.proxy.parent_mode_dir == "app"
    assert config.app.proxy.mode_dir_path == Path("app/proxy")

    # print()
    # print("=*" * 50)
    # print(config.model_dump_json(indent=4))
    # print(f"{config.app.conf_path = }")
    # print(f"{config.app.proxy.conf_path = }")


# @pytest.mark.current
@pytest.mark.mode_dir
def test_mode_dir_inherit_parent(cwd_to_tmp):
    class Proxy(ArFiSettings):
        mode_dir_inherit_parent = False

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = True
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.app.mode_dir == "app"
    assert config.app.proxy.parent_mode_dir == "app"
    assert config.app.proxy.mode_dir_path == Path("proxy")


# @pytest.mark.current
@pytest.mark.mode_dir
def test_empty_mode_dir(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        mode_dir = ""
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = True
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.app.proxy.parent_mode_dir == DEFAULT_PATH_SENTINEL
    assert config.app.proxy.mode_dir_path == Path("proxy")


# @pytest.mark.current
@pytest.mark.mode_dir
def test_none_mode_dir(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        mode_dir = None
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = True
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.app.proxy.parent_mode_dir == DEFAULT_PATH_SENTINEL
    assert config.app.proxy.mode_dir_path == Path("proxy")


@pytest.mark.mode_dir
def test_empty_mode_dir_with_parent_mode_dir(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        mode_dir = ""
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = True
        mode_dir = "dev"
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.app.parent_mode_dir == "dev"
    assert config.app.mode_dir_path == Path("dev")
    assert config.app.proxy.parent_mode_dir == "dev"
    assert config.app.proxy.mode_dir_path == Path("dev/proxy")


# @pytest.mark.current
@pytest.mark.mode_dir
def test_none_mode_dir_with_parent_mode_dir(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        mode_dir = None
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = True
        mode_dir = "dev"
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.app.parent_mode_dir == "dev"
    assert config.app.mode_dir_path == Path("dev")
    assert config.app.proxy.parent_mode_dir == "dev"
    assert config.app.proxy.mode_dir_path == Path("dev/proxy")


# @pytest.mark.current
@pytest.mark.mode_dir
def test_read_config(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = True
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.read_config


@pytest.mark.mode_dir
@pytest.mark.xfail
@pytest.mark.parametrize("value", [None, 0, 1, "", "some_string", "False"])
def test_read_config_not_bool(cwd_to_tmp, value):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = value
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.read_config


# @pytest.mark.current
@pytest.mark.mode_dir
@pytest.mark.parametrize(
    "values, app_mode, proxy_mode",
    [
        (
            {"app": {"MODE": "my_app_mode", "proxy": {"MODE": "my_proxy_mode"}}},
            "my_app_mode",
            "my_proxy_mode",
        ),
        (
            {"app": {"proxy": {}}},
            None,
            None,
        ),
    ],
)
def test_mode(cwd_to_tmp, values, app_mode, proxy_mode, path_base_dir):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        read_config = True
        app: AppSettings = AppSettings()

    config = AppConfig(**values)
    assert config.MODE is None
    assert config.app.MODE == app_mode
    assert config.app.proxy.MODE == proxy_mode
    assert config.app.mode_dir == "app"
    assert config.app.proxy.mode_dir == "proxy"
