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


# @pytest.mark.settings
# def test_simple_config_file_by_default(simple_data_config_config_toml):
#     class AppConfig(ArFiSettings):
#         path_config_file: str
#
#     config = AppConfig()
#     assert config.MODE is None
#     assert config.path_config_file == "config/config.toml"
#
#
# # @pytest.mark.skip
# @pytest.mark.settings
# class TestMainConfig:
#     # @pytest.mark.current
#     def test_read_config_default_detection(self):
#         class AppConfig(ArFiSettings):
#             pass
#
#         assert AppConfig.read_config is False
#         config = AppConfig()
#         assert config.read_config is True
#
#     # @pytest.mark.current
#     def test_read_config_handler_setup(self):
#         class ProdAppSettings(ArFiSettings):
#             pass
#
#         class AppSettings(ArFiSettings):
#             asd: str = "test"
#             pass
#
#         class AppConfig(ArFiSettings):
#             app: AppSettings
#             # app: AppSettings = {}
#             # app: AppSettings = AppSettings()
#
#         assert AppSettings.read_config is False
#         assert ProdAppSettings.read_config is False
#         assert AppConfig.read_config is False
#
#         data = {
#             "app": {
#                 "asd": "asd",
#                 # "_read_config": True,
#             }
#         }
#         config = AppConfig(**data)
#         assert config.read_config is True
#         assert config.app.read_config is True
#
#         print("=" * 100)
#
#         class AppConfig(ArFiSettings):
#             app: AppSettings | ProdAppSettings = AppSettings()
#
#         config = AppConfig()
#         assert config.app.read_config is True
#
#         print("=" * 100)
#
#         class AppConfig(ArFiSettings):
#             app: AppSettings | None = AppSettings()
#
#         config = AppConfig()
#         assert config.app.read_config is False
#
#         print("=" * 100)
#
#         class AppConfig(ArFiSettings):
#             # app: ArFiSettings = None
#             app: AppSettings = None
#
#         config = AppConfig()
#         assert config.app.read_config is True
#
#
# # @pytest.mark.settings
# # class TestAliasesSettings:
# #     """Test aliases in settings."""
# #
# #     # @pytest.mark.current
# #     def test_without_alias(self, empty_config_config_toml):
# #         conf_file = empty_config_config_toml
# #         conf_file.write_text(
# #             """
# #             path_config_file = 'config/config.toml'
# #             [app]
# #             path_config_file = 'config/config.toml'
# #             """
# #         )
# #
# #         class AppSettings(ArFiSettings):
# #             path_config_file: str = "tests/"
# #
# #         class AppConfig(ArFiSettings):
# #             path_config_file: str
# #             app: AppSettings
# #
# #         config = AppConfig()
# #         assert config.MODE is None
# #         assert config.path_config_file == "config/config.toml"
# #         assert config.app.path_config_file == "config/config.toml"
# #
# #     # @pytest.mark.current
# #     def test_simple_alias(self, empty_config_config_toml):
# #         conf_file = empty_config_config_toml
# #         conf_file.write_text(
# #             """
# #             app_config_file = 'config/config.toml'
# #             [app]
# #             app_settings_file = 'config/config.toml'
# #             """
# #         )
# #
# #         class AppSettings(ArFiSettings):
# #             path_config_file: str = Field(alias="app_settings_file")
# #
# #         class AppConfig(ArFiSettings):
# #             path_config_file: str = Field(alias="app_config_file")
# #             app: AppSettings
# #
# #         config = AppConfig()
# #         assert config.MODE is None
# #         assert config.path_config_file == "config/config.toml"
# #         assert config.app.path_config_file == "config/config.toml"
# #
# #     # # @pytest.mark.current
# #     # def test_alias_case_sensitive_by_default(self, empty_config_config_toml):
# #     #     conf_file = empty_config_config_toml
# #     #     conf_file.write_text(
# #     #         """
# #     #         APP_CONFIG_FILE = 'config/config.toml'
# #     #         [app]
# #     #         APP_SETTINGS_FILE = 'config/config.toml'
# #     #         """
# #     #     )
# #     #
# #     #     class AppSettings(ArFiSettings):
# #     #         path_config_file: str = Field(alias="app_settings_file")
# #     #
# #     #     class AppConfig(ArFiSettings):
# #     #         path_config_file: str = Field(alias="app_config_file")
# #     #         app: AppSettings
# #     #
# #     #     config = AppConfig()
# #     #     assert config.MODE is None
# #     #     assert config.path_config_file == "config/config.toml"
# #     #     assert config.app.path_config_file == "config/config.toml"
#
#
# # @pytest.mark.current
# # @pytest.mark.settings
# # def test_explicit_config_file_by_default(simple_data_config_config_toml):
# #     from typing import Optional, Literal
# #     from pydantic import BaseModel
# #
# #     class ProdAppSettings(ArFiSettings):
# #         path_config_file: str = "prod/"
# #
# #     class AppSettings(ArFiSettings):
# #         path_config_file: str = "tests/"
# #
# #     class Simple(BaseModel):
# #         path_config_file: str = "base/"
# #
# #     class AppConfig(ArFiSettings):
# #         path_config_file: str
# #         # app: AppSettings
# #         app: AppSettings | ProdAppSettings
# #         # app: dict | AppSettings
# #         # app: AppSettings | dict
# #         # app: AppSettings | str | None
# #         # app: Optional[AppSettings]
# #         # app: Optional[AppSettings] | str | dict
# #         # app: AppSettings = AppSettings()
# #         # app: AppSettings = None
# #         # app: AppSettings | str | None | list | dict | Simple | ProdAppSettings = None
# #         # app: AppSettings | list[AppSettings] | str | None
# #         # app: list[AppSettings] | AppSettings | str | None
# #         # app: list[AppSettings] | AppSettings | str | None | Simple
# #
# #         # app: Literal["ArFiSettings", "ProdAppSettings", ArFiSettings()] | str
# #
# #     data = {
# #         "app": {"path_config_file": "config/config.toml"},
# #     }
# #     # data = {"app": AppSettings}
# #     config = AppConfig(**data)
# #     assert config.MODE is None
# #     assert config.path_config_file == "config/config.toml"
# #     assert config.app.path_config_file == "config/config.toml"
#
#
# # @pytest.mark.current
# # @pytest.mark.settings
# # def test_explicit_config_file_by_default2(tests_dir):
# #     print()
# #     import os
# #
# #     print(os.getcwd())
# #
# #     class Proxy(ArFiSettings):
# #         path_config_file: str
# #
# #     class AppSettings(ArFiSettings):
# #         path_config_file: str
# #         proxy: Proxy
# #
# #     class AppConfig(ArFiSettings):
# #         path_config_file: str
# #         app: AppSettings
# #
# #     config = AppConfig()
# #     assert config.MODE is None
# #     assert config.path_config_file == "config/config.toml"
# #     print()
# #     print(config.model_dump_json(indent=4))
#
#
# # # @pytest.mark.current
# # @pytest.mark.settings
# # def test_explicit_config_file_by_default_init(tests_dir):
# #     print()
# #     import os
# #
# #     print(os.getcwd())
# #
# #     class Proxy(ArFiSettings):
# #         path_config_file: str
# #
# #     class AppSettings(ArFiSettings):
# #         path_config_file: str
# #         proxy: Proxy
# #
# #     class AppConfig(ArFiSettings):
# #         path_config_file: str
# #         app: AppSettings = AppSettings()
# #
# #     config = AppConfig()
# #     assert config.MODE is None
# #     assert config.path_config_file == "config/config.toml"
