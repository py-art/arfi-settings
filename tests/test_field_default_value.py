from typing import Literal

import pytest
from pydantic import AliasChoices, BaseModel, Field

from arfi_settings import ArFiSettings


# @pytest.mark.current
@pytest.mark.field_default_value
def test_default_value(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.MODE is None
    assert config.app.MODE is None

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings(mode="prod")

    config = AppConfig()
    assert config.MODE is None
    assert config.app.MODE == "prod"

    class AppSettings(ArFiSettings):
        MODE: str | None = Field("prod", validation_alias=AliasChoices("mode", "MODE"))

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.MODE is None
    assert config.app.MODE == "prod"

    app = AppSettings(mode="dev")
    config = AppConfig(app=app)
    assert config.app.MODE == "dev"

    config = AppConfig(app=AppSettings(mode="test"))
    assert config.app.MODE == "test"

    class PydanticConfig(BaseModel):
        app: AppSettings = AppSettings(mode="pydantic")

    config = PydanticConfig()
    assert config.app.MODE == "pydantic"


# @pytest.mark.current
@pytest.mark.field_default_value
def test_default_value_with_discriminator(cwd_to_tmp, path_base_dir):
    class SQLite(BaseModel):
        db_type: Literal["sqlite"] = "sqlite"

    class Postgre(ArFiSettings):
        db_type: Literal["postgre"] = "postgre"

    class MySQL(ArFiSettings):
        db_type: Literal["mysql"] = "mysql"

    class AppConfig(ArFiSettings):
        db: SQLite | Postgre = Field(  # SQLite is not settings field type
            default=Postgre(mode="prod"),
            discriminator="db_type",
        )

    config = AppConfig()
    assert config.db.MODE == "prod"
    assert config.db.db_type == "postgre"

    data = {"db": {"mode": "asd", "db_type": "postgre"}}
    config = AppConfig(**data)
    assert config.db.MODE == "asd"
    assert config.db.db_type == "postgre"

    data = {"db": {"db_type": "sqlite"}}
    config = AppConfig(**data)
    assert config.db.db_type == "sqlite"

    # the default values are not readable
    data = {"db": {"db_type": "postgre"}}
    config = AppConfig(**data)
    assert config.db.MODE is None  # because db: SQLite is not settings field type
    assert config.db.db_type == "postgre"

    class AppConfig(ArFiSettings):
        db: MySQL | Postgre = Field(  # all types are settings field types
            default=Postgre(mode="prod"),
            discriminator="db_type",
        )

    # the default values are read
    data = {"db": {"db_type": "postgre"}}
    config = AppConfig(**data)
    assert config.db.MODE == "prod"  # because db: MySQL is settings field type
    assert config.db.db_type == "postgre"
