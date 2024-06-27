from typing import Literal

import pytest
from pydantic import AliasChoices, AliasPath, Field

from arfi_settings import ArFiSettings, EnvConfigDict, FileConfigDict, SettingsConfigDict


# @pytest.mark.current
@pytest.mark.case_sensitive
def test_case_sensitive(alias_data_config_config_toml, path_base_dir):
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig()
    assert config.settings_config.case_sensitive is False
    assert config.settings_config.conf_case_sensitive is False
    assert config.settings_config.env_case_sensitive is False

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(case_sensitive=True)

    config = AppConfig()
    assert config.settings_config.case_sensitive is True
    assert config.settings_config.conf_case_sensitive is True
    assert config.settings_config.env_case_sensitive is True

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            case_sensitive=True,
            conf_case_sensitive=False,
            env_case_sensitive=False,
        )

    config = AppConfig()
    assert config.settings_config.case_sensitive is True
    assert config.settings_config.conf_case_sensitive is False
    assert config.settings_config.env_case_sensitive is False

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(conf_case_sensitive=False)
        env_config = EnvConfigDict(env_case_sensitive=False)
        model_config = SettingsConfigDict(
            case_sensitive=True,
            conf_case_sensitive=True,
            env_case_sensitive=True,
        )

    config = AppConfig()
    assert config.settings_config.case_sensitive is True
    assert config.settings_config.conf_case_sensitive is False
    assert config.settings_config.env_case_sensitive is False

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            validation_alias=AliasChoices(
                AliasPath("ALIAS_PATH", 0),
                AliasPath("OTHER_ALIAS_PATH", 1),
            ),
        )
        asd: str = Field(validation_alias=AliasChoices("ASD_TEST", "CONFIG_DATA"))

    config = AppConfig()
    assert config.alias_config_data == "alias_path_1"
    assert config.asd == "asd_test"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            validation_alias=AliasChoices(
                AliasPath("ALIAS_PATH", 0),
                AliasPath("OTHER_ALIAS_PATH", 1),
            ),
        )
        asd: str = Field(validation_alias=AliasChoices("ASD_TEST", "CONFIG_DATA"))
        model_config = SettingsConfigDict(case_sensitive=True)

    config = AppConfig()
    assert config.alias_config_data == "other_alias_path_2"
    assert config.asd == "CONFIG_DATA"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            validation_alias=AliasChoices(
                AliasPath("other_complex_alias_path", "ALIAS_PATH", 1),
            ),
        )

    config = AppConfig()
    assert config.alias_config_data == "OTHER_ALIAS_PATH_2"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            validation_alias=AliasChoices(
                AliasPath("other_complex_alias_path", "alias_path", 1),
            ),
        )

    config = AppConfig()
    assert config.alias_config_data == "other_alias_path_2"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            validation_alias=AliasChoices(
                AliasPath("other_complex_alias_path", "Alias_Path", 1),
            ),
        )

    config = AppConfig()
    assert config.alias_config_data == "other_alias_path_2"


# @pytest.mark.current
@pytest.mark.case_sensitive
def test_double_field_case_sensitive(cwd_to_tmp, path_base_dir):
    class AppConfig(ArFiSettings):
        mode: str = "test_mode"

    config = AppConfig()
    assert config.MODE is None
    assert config.mode == "test_mode"

    data = {"mode": "lower_mode"}
    config = AppConfig(**data)
    assert config.MODE == "lower_mode"
    assert config.mode == "lower_mode"

    data = {"MODE": "UPPER_MODE"}
    config = AppConfig(**data)
    assert config.MODE == "UPPER_MODE"
    assert config.mode == "test_mode"

    data = {"MODE": "UPPER_MODE", "mode": "lower_mode"}
    config = AppConfig(**data)
    assert config.MODE == "UPPER_MODE"
    assert config.mode == "lower_mode"


# @pytest.mark.current
@pytest.mark.case_sensitive
def test_double_field_case_sensitive_discriminator(cwd_to_tmp, path_base_dir):
    class MySQL(ArFiSettings):
        DB_TYPE: Literal["mysql"] = "mysql"
        db_type: str = "mysql_default"
        Db_Type: str = "Db_Type_mysql"

    class Postgres(ArFiSettings):
        DB_TYPE: Literal["postgres"] = "postgres"
        db_type: str = "postgres_default"
        Db_Type: str = "Db_Type_postgres"

    class AppConfig(ArFiSettings):
        db: Postgres | MySQL = Field(MySQL(), discriminator="DB_TYPE")

    data = {"db": {"db_type": "postgres"}}
    config = AppConfig(**data)
    assert config.db.DB_TYPE == "postgres"
    assert config.db.db_type == "postgres"
    assert config.db.Db_Type == "Db_Type_postgres"

    data = {"db": {"Db_Type": "postgres"}}
    config = AppConfig(**data)
    assert config.db.DB_TYPE == "postgres"
    assert config.db.db_type == "postgres_default"
    assert config.db.Db_Type == "postgres"

    data = {"db": {"DB_TYPE": "postgres"}}
    config = AppConfig(**data)
    assert config.db.DB_TYPE == "postgres"
    assert config.db.db_type == "postgres_default"
    assert config.db.Db_Type == "Db_Type_postgres"

    data = {"db": {"DB_TYPE": "postgres", "db_type": "INIT_DTATA"}}
    config = AppConfig(**data)
    assert config.db.DB_TYPE == "postgres"
    assert config.db.db_type == "INIT_DTATA"
    assert config.db.Db_Type == "Db_Type_postgres"

    class AppConfig(ArFiSettings):
        db: Postgres | MySQL = Field(MySQL(), discriminator="DB_TYPE")

        model_config = SettingsConfigDict(case_sensitive=True)

    data = {"db": {"db_type": "postgres"}}
    config = AppConfig(**data)
    assert config.db.DB_TYPE == "mysql"
    assert config.db.db_type == "postgres"
    assert config.db.Db_Type == "Db_Type_mysql"
