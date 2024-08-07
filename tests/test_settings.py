from pathlib import Path

import pytest

import arfi_settings
from arfi_settings import ArFiSettings
from arfi_settings.init_config import InitSettings


# @pytest.mark.current
@pytest.mark.settings
def test_base_dir(cwd_to_tmp, monkeypatch, platform_system):
    class PatchedInitSettings(InitSettings):
        @staticmethod
        def _search_called_file():
            return cwd_to_tmp.as_posix(), 0

    monkeypatch.setattr(arfi_settings.init_config, "InitSettings", PatchedInitSettings)
    init_settings = PatchedInitSettings()
    monkeypatch.setattr(arfi_settings.init_config, "init_settings", init_settings)
    monkeypatch.setattr(arfi_settings.main, "init_settings", init_settings)

    class AppConfig(ArFiSettings):
        pass

    config = AppConfig()
    assert config.BASE_DIR == cwd_to_tmp.parent

    monkeypatch.setattr(arfi_settings.init_config, "InitSettings", PatchedInitSettings)
    init_settings = PatchedInitSettings()
    monkeypatch.setattr(arfi_settings.init_config, "init_settings", init_settings)
    monkeypatch.setattr(arfi_settings.main, "init_settings", init_settings)

    class AppConfig(ArFiSettings):
        BASE_DIR = "settings/"

    config = AppConfig()
    assert config.BASE_DIR == cwd_to_tmp / "settings"

    monkeypatch.setattr(arfi_settings.init_config, "InitSettings", PatchedInitSettings)
    init_settings = PatchedInitSettings()
    monkeypatch.setattr(arfi_settings.init_config, "init_settings", init_settings)
    monkeypatch.setattr(arfi_settings.main, "init_settings", init_settings)

    class AppConfig(ArFiSettings):
        BASE_DIR = "/settings"

    config = AppConfig()
    base_dir = Path("/settings")
    assert config.BASE_DIR == base_dir.expanduser().resolve()

    monkeypatch.setattr(arfi_settings.init_config, "InitSettings", PatchedInitSettings)
    init_settings = PatchedInitSettings()
    monkeypatch.setattr(arfi_settings.init_config, "init_settings", init_settings)
    monkeypatch.setattr(arfi_settings.main, "init_settings", init_settings)
    monkeypatch.setenv("HOME", "/")

    class AppConfig(ArFiSettings):
        BASE_DIR = "~/settings"

    config = AppConfig()
    base_dir = Path("~/settings")
    assert config.BASE_DIR == base_dir.expanduser().resolve()
