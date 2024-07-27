from pathlib import PosixPath

import pydantic
import pytest
from pydantic import AliasChoices, AliasPath, Field

from arfi_settings import (
    ArFiSettings,
    ArFiSettingsError,
    SettingsConfigDict,
)


# @pytest.mark.current
@pytest.mark.secret
def test_non_existing_secrets_dir(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="non_existing_secret_dir",
        )

    config = AppConfig()
    assert config.settings_config.secrets_dir == PosixPath("non_existing_secret_dir")

    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig(ArFiSettings):
            ordered_settings = [
                "secrets",
            ]
            model_config = SettingsConfigDict(
                secrets_dir="non_existing_secrets_dir",
                ignore_missing=False,
            )

        _ = AppConfig()
    assert "Missing secrets directory" in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.secret
def test_empty_secrets_dir(secrets_dir):
    class AppConfig(ArFiSettings):
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="secrets",
            ignore_missing=False,
        )

    config = AppConfig()
    assert config.settings_config.secrets_dir == PosixPath("secrets")


# @pytest.mark.current
@pytest.mark.secret
def test_empty_data_secrets_dir(empty_secret_path_config_file):
    class AppConfig(ArFiSettings):
        path_config_file: str
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="secrets",
            ignore_missing=False,
        )

    config = AppConfig()
    assert config.settings_config.secrets_dir == PosixPath("secrets")
    assert config.path_config_file == ""


# @pytest.mark.current
@pytest.mark.secret
def test_simple_data_secrets_dir(simple_data_secret_path_config_file):
    class AppConfig(ArFiSettings):
        path_config_file: str
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="secrets",
            ignore_missing=False,
        )

    config = AppConfig()
    assert config.settings_config.secrets_dir == PosixPath("secrets")
    assert config.path_config_file == "secrets/path_config_file"


# @pytest.mark.current
@pytest.mark.case_sensitive
@pytest.mark.secret
def test_case_sensitive_secrets_dir(secrets_dir, platform_system):
    PATH_CONFIG_FILE = secrets_dir / "PATH_CONFIG_FILE"
    PATH_CONFIG_FILE.touch(exist_ok=True)
    PATH_CONFIG_FILE.write_text("secrets/PATH_CONFIG_FILE")

    Path_Config_File = secrets_dir / "Path_Config_File"
    Path_Config_File.touch(exist_ok=True)
    Path_Config_File.write_text("secrets/Path_Config_File")

    path_config_file = secrets_dir / "path_config_file"
    path_config_file.touch(exist_ok=True)
    path_config_file.write_text("secrets/path_config_file")

    class AppConfig(ArFiSettings):
        path_config_file: str
        PATH_CONFIG_FILE: str
        Path_Config_File: str
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="secrets",
            ignore_missing=False,
        )

    config = AppConfig()
    assert config.path_config_file == "secrets/path_config_file"
    if platform_system.lower() == "linux":
        assert config.PATH_CONFIG_FILE == "secrets/PATH_CONFIG_FILE"
    else:
        assert config.PATH_CONFIG_FILE == "secrets/Path_Config_File"
    assert config.Path_Config_File == "secrets/Path_Config_File"

    class AppConfig(ArFiSettings):
        path_config_FILE: str
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="secrets",
            ignore_missing=False,
        )

    config = AppConfig()
    assert config.path_config_FILE == "secrets/path_config_file"

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class AppConfig(ArFiSettings):
            path_config_FILE: str
            ordered_settings = [
                "secrets",
            ]
            model_config = SettingsConfigDict(
                secrets_dir="secrets",
                ignore_missing=False,
                case_sensitive=True,
            )

        _ = AppConfig()

    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "missing",
            "loc": ("path_config_FILE",),
            "msg": "Field required",
            "input": {},
        },
    ]


# @pytest.mark.current
@pytest.mark.alias
@pytest.mark.secret
def test_alias_choices_secrets_dir(secrets_dir):
    PATH_CONFIG_FILE = secrets_dir / "PATH_CONFIG_FILE"
    PATH_CONFIG_FILE.touch(exist_ok=True)
    PATH_CONFIG_FILE.write_text("secrets/PATH_CONFIG_FILE")

    Path_Config_File = secrets_dir / "Path_Config_File"
    Path_Config_File.touch(exist_ok=True)
    Path_Config_File.write_text("secrets/Path_Config_File")

    path_config_file = secrets_dir / "path_config_file"
    path_config_file.touch(exist_ok=True)
    path_config_file.write_text("secrets/path_config_file")

    class AppConfig(ArFiSettings):
        path: str = Field(alias="path_config_file")
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="secrets",
            ignore_missing=False,
        )

    config = AppConfig()
    assert config.path == "secrets/path_config_file"

    class AppConfig(ArFiSettings):
        path: str = Field(
            validation_alias=AliasChoices("path_CONFIG_file", "path_config_FILE"),
        )
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="secrets",
            ignore_missing=False,
        )

    config = AppConfig()
    assert config.path == "secrets/path_config_file"

    class AppConfig(ArFiSettings):
        path: str = Field(
            validation_alias=AliasChoices("Path_Config_File", "path_config_file"),
        )
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="secrets",
            ignore_missing=False,
        )

    config = AppConfig()
    assert config.path == "secrets/Path_Config_File"


# @pytest.mark.current
@pytest.mark.alias
@pytest.mark.secret
def test_alias_path_secrets_dir(secrets_dir):
    path_for_alias = secrets_dir / "path_for_alias"
    path_for_alias.touch(exist_ok=True)
    path_for_alias.write_text(
        '["secrets/path_for_alias_0","secrets/path_for_alias_1"]',
    )

    class AppConfig(ArFiSettings):
        path: str = Field(
            validation_alias=AliasPath("path_for_alias", 1),
        )
        ordered_settings = [
            "secrets",
        ]
        model_config = SettingsConfigDict(
            secrets_dir="secrets",
            ignore_missing=False,
        )

    config = AppConfig()
    assert config.path == "secrets/path_for_alias_1"
