import argparse
import sys
from pathlib import Path
from typing import Literal

import pytest

import arfi_settings
from arfi_settings import ArFiReader, ArFiSettings, EnvConfigDict, SettingsConfigDict
from arfi_settings.init_config import InitSettings


try:
    import yaml
except ImportError:
    yaml = None


# @pytest.mark.current
@pytest.mark.pyproject
def test_init_settings_with_pyproject_toml(
    empty_pyproject_toml_file,
    cwd_to_tmp,
    monkeypatch,
):
    settings_file = cwd_to_tmp / "settings.py"
    settings_file.touch(exist_ok=True)

    class PatchedInitSettings(InitSettings):
        @staticmethod
        def _search_called_file():
            return settings_file.as_posix(), 0

    monkeypatch.setattr(arfi_settings.init_config, "InitSettings", PatchedInitSettings)
    init_settings = PatchedInitSettings()
    monkeypatch.setattr(arfi_settings.init_config, "init_settings", init_settings)
    monkeypatch.setattr(arfi_settings.main, "init_settings", init_settings)
    empty_pyproject_toml_file.write_text(
        """
        [tool.arfi_settings]
        env_file=''
        env_config_inherit_parent=false
        """
    )

    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings
        env_config_inherit_parent = True

    assert init_settings.pyproject_toml_path is None
    assert init_settings.main_config_file is None
    assert init_settings.init_params.env_file == ".env"
    assert init_settings.init_params.env_config_inherit_parent is True

    _ = AppConfig()

    assert init_settings.pyproject_toml_path == empty_pyproject_toml_file
    assert init_settings.main_config_file == settings_file
    assert init_settings.init_params.env_file == ""
    assert init_settings.init_params.env_config_inherit_parent is False


# @pytest.mark.current
@pytest.mark.skipif(yaml is None, reason="PyYaml not installed")
@pytest.mark.pyproject
def test_pyproject_toml_class_vars(
    cwd_to_tmp,
    monkeypatch,
):
    root_init_file = cwd_to_tmp / "__init__.py"
    root_init_file.touch(exist_ok=True)
    settings_dir = cwd_to_tmp / "settings"
    settings_dir.mkdir(exist_ok=True)
    settings_init_file = settings_dir / "__init__.py"
    settings_init_file.touch(exist_ok=True)
    settings_file = settings_dir / "settings.py"
    settings_file.touch(exist_ok=True)
    config_dir = cwd_to_tmp / "config"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.yml"
    config_file.touch(exist_ok=True)
    app_config_dir = config_dir / "app"
    app_config_dir.mkdir(exist_ok=True)
    app_config_file = app_config_dir / "config.yml"
    app_config_file.touch(exist_ok=True)
    app_config_file.write_text(
        """
        mode: 'prod'
        path_config_file: 'config/app/config.yml'
        """
    )
    app_mode_prod_config_file = app_config_dir / "prod.json"
    app_mode_prod_config_file.touch(exist_ok=True)
    app_mode_prod_config_file.write_text(
        """
        {
            "path_config_file": "config/app/prod.json",
            "database_dialect": "postgresql"
        }
        """
    )
    app_mode_dev_config_file = app_config_dir / "dev.json"
    app_mode_dev_config_file.touch(exist_ok=True)
    app_mode_dev_config_file.write_text(
        """
        {
            "path_config_file": "config/app/dev.json",
            "database_dialect": "mysql"
        }
        """
    )
    app_mode_test_config_file = app_config_dir / "test.yml"
    app_mode_test_config_file.touch(exist_ok=True)
    app_mode_test_config_file.write_text(
        """
        database_dialect: "sqlite"
        """
    )

    class PatchedInitSettings(InitSettings):
        @staticmethod
        def _search_called_file():
            return settings_file.as_posix(), 0

    monkeypatch.setattr(arfi_settings.init_config, "InitSettings", PatchedInitSettings)
    init_settings = PatchedInitSettings()
    monkeypatch.setattr(arfi_settings.init_config, "init_settings", init_settings)
    monkeypatch.setattr(arfi_settings.main, "init_settings", init_settings)
    monkeypatch.setattr(arfi_settings.readers.ArFiReader, "default_cli_reader", None)

    pyproject_toml_file = cwd_to_tmp / "pyproject.toml"
    pyproject_toml_file.touch(exist_ok=True)
    pyproject_toml_file.write_text(
        """
        [tool.arfi_settings]
        env_file=''
        env_config_inherit_parent=false
        env_file_encoding="cp1251"
        ignore_missing=true
        conf_ignore_missing=false
        conf_exclude_inherit_parent=[
            "conf_ignore_missing",
            "conf_ext"
        ]
        secrets_dir="secrets/"
        """
    )
    secrets_dir = cwd_to_tmp / "secrets"
    secrets_dir.mkdir(exist_ok=True)

    class AppSettings(ArFiSettings):
        path_config_file: str
        database_dialect: Literal["sqlite", "postgresql", "mysql"] = "mysql"
        model_config = SettingsConfigDict(
            env_file_encoding="utf-8",
            conf_ext=["yml", "json"],
            env_file=".env.prod",
            cli=True,
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        env_config_inherit_parent = True
        env_config = EnvConfigDict(
            env_case_sensitive=True,
        )
        model_config = SettingsConfigDict(
            ignore_missing=False,
            conf_ignore_missing=True,
        )

    assert init_settings.pyproject_toml_path is None
    assert init_settings.main_config_file is None
    assert init_settings.init_params.env_file == ".env"
    assert init_settings.init_params.env_config_inherit_parent is True

    config = AppConfig()

    assert init_settings.pyproject_toml_path == pyproject_toml_file
    assert init_settings.main_config_file == settings_file
    assert init_settings.init_params.env_file == ""
    assert init_settings.init_params.env_config_inherit_parent is False

    assert config.pyproject_toml_path == pyproject_toml_file
    assert config.app.pyproject_toml_path == pyproject_toml_file
    assert config.env_config_inherit_parent is True
    assert config.app.env_config_inherit_parent is False
    assert config.settings_config.env_file == ""
    assert config.app.settings_config.env_file == ".env.prod"
    assert config.settings_config.env_file_encoding == "cp1251"
    assert config.app.settings_config.env_file_encoding == "utf-8"

    assert config.settings_config.conf_ignore_missing is True
    assert config.settings_config.env_ignore_missing is False
    assert config.app.settings_config.conf_ignore_missing is False
    assert config.app.settings_config.env_ignore_missing is True

    assert config.settings_config.conf_ext == ["toml", "yaml", "yml", "json"]
    assert config.app.settings_config.conf_ext == ["yml", "json"]

    assert config.app.path_config_file == "config/app/prod.json"
    assert config.app.database_dialect == "postgresql"

    secrets_file = secrets_dir / "path_config_FILE"
    secrets_file.touch(exist_ok=True)
    secrets_file.write_text("secrets/path_config_file")

    config = AppConfig()
    assert config.settings_config.secrets_dir == Path("secrets")
    assert config.settings_config.secrets_dir.resolve() == secrets_dir
    assert config.app.path_config_file == "secrets/path_config_file"

    env_file = cwd_to_tmp / ".env.prod"
    env_file.touch(exist_ok=True)
    env_file.write_text("PATH_CONFIG_FILE=ENV_FILE_PATH_CONFIG_FILE")
    config = AppConfig()
    assert config.app.path_config_file == "ENV_FILE_PATH_CONFIG_FILE"

    monkeypatch.setenv("PATH_CONFIG_FILE", "env_path_config_file")
    config = AppConfig()
    assert config.app.path_config_file == "env_path_config_file"

    def parse_args():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument(
            "--debug",
            type=bool,
            const=True,
            nargs="?",
            help="Debug application",
        )
        parser.add_argument(
            "--mode",
            type=str,
            help="Application mode",
        )
        cli_options = parser.parse_args()
        data = dict(cli_options._get_kwargs())
        if not cli_options.mode:
            data.pop("mode")
        if cli_options.debug and not cli_options.mode:
            data["MODE"] = "dev"
        return data

    ArFiReader.setup_cli_reader(parse_args)
    monkeypatch.setattr(sys, "argv", [sys.argv[0]])
    config = AppConfig()
    assert config.MODE is None
    assert config.app.MODE == "prod"
    assert config.app.path_config_file == "env_path_config_file"
    assert config.app.database_dialect == "postgresql"

    monkeypatch.setattr(sys, "argv", [sys.argv[0], "--debug"])
    config = AppConfig()
    assert config.MODE is None
    assert config.app.MODE == "dev"
    assert config.app.path_config_file == "env_path_config_file"
    assert config.app.database_dialect == "mysql"

    monkeypatch.setattr(sys, "argv", [sys.argv[0], "--debug", "--mode", "test"])
    config = AppConfig()
    assert config.MODE is None
    assert config.app.MODE == "test"
    assert config.app.path_config_file == "env_path_config_file"
    assert config.app.database_dialect == "sqlite"
