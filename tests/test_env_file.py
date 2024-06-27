import pytest

from arfi_settings import ArFiSettings, EnvConfigDict


# @pytest.mark.current
@pytest.mark.env_file
def test_simple_env_file_data(
    simple_data_env_file,
    path_base_dir,
):
    class AppConfig(ArFiSettings):
        path_config_file: str = "default_path_config_file"

    config = AppConfig()
    assert config.path_config_file == ".env"


# @pytest.mark.current
@pytest.mark.env_file
def test_ordered_env_file_data(
    simple_data_env_file,
    simple_data_prod_env_file,
    path_base_dir,
):
    class AppConfig(ArFiSettings):
        path_config_file: str = "default_path_config_file"
        env_config = EnvConfigDict(
            env_file=[
                "prod.env",
                ".env",
            ],
        )

    config = AppConfig()
    assert config.path_config_file == ".env"

    class AppConfig(ArFiSettings):
        path_config_file: str = "default_path_config_file"
        env_config = EnvConfigDict(
            env_file=[
                ".env",
                "prod.env",
            ],
        )

    config = AppConfig()
    assert config.path_config_file == "prod.env"
