import pytest

from arfi_settings import ArFiSettings
from pathlib import PosixPath


# @pytest.mark.current
@pytest.mark.field_default_params
def test_read_config_default_params(simple_data_config_config_toml, path_base_dir):
    """Test default params _read_config and _read_config_force."""

    class AppConfig(ArFiSettings):
        path_config_file: str = "default"

    config = AppConfig()
    assert config.path_config_file == "config/config.toml"
    config = AppConfig(_read_config=False)
    assert config.path_config_file == "default"
    config = AppConfig(_read_config=False, _read_config_force=True)
    assert config.path_config_file == "config/config.toml"

    class AppConfig(ArFiSettings):
        read_config = False
        path_config_file: str = "default"

    config = AppConfig()
    assert config.path_config_file == "default"
    config = AppConfig(_read_config=True)
    assert config.path_config_file == "config/config.toml"

    class AppConfig(ArFiSettings):
        read_config = False
        read_config_force = False
        path_config_file: str = "default"

    config = AppConfig()
    assert config.path_config_file == "default"
    config = AppConfig(_read_config=True)
    assert config.path_config_file == "default"
    config = AppConfig(_read_config_force=True)
    assert config.path_config_file == "config/config.toml"

    class AppConfig(ArFiSettings):
        read_config = True
        read_config_force = False
        path_config_file: str = "default"

    config = AppConfig()
    assert config.path_config_file == "default"
    config = AppConfig(_read_config_force=True)
    assert config.path_config_file == "config/config.toml"

    class AppConfig(ArFiSettings):
        read_config = False
        read_config_force = True
        path_config_file: str = "default"

    config = AppConfig()
    assert config.path_config_file == "config/config.toml"
    config = AppConfig(_read_config_force=False)
    assert config.path_config_file == "default"


# @pytest.mark.current
@pytest.mark.field_default_params
@pytest.mark.mode_dir
def test_mode_dir_default_params(cwd_to_tmp):
    """Test default params _mode_dir."""
    # from pathlib import Path
    #
    # print()
    # print(Path().cwd())

    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings()
        read_config_force = False

    config = AppConfig()
    assert config.mode_dir == PosixPath(".")
    assert config.app.mode_dir == "app"

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config.mode_dir == PosixPath(".")
    assert config.app.mode_dir == "app"

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings(_mode_dir="test_mode_dir")

    config = AppConfig()
    assert config.mode_dir == PosixPath(".")
    assert config.app.mode_dir == "test_mode_dir"


#
