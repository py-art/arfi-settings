import os
import platform

import pytest

import arfi_settings
from arfi_settings.init_config import InitSettings


def pytest_configure(config):
    config.addinivalue_line("markers", "todo: need implementation")
    config.addinivalue_line("markers", "current: for debug current tests")
    config.addinivalue_line("markers", "mode_dir")
    config.addinivalue_line("markers", "descriptors")
    config.addinivalue_line("markers", "schemes")
    config.addinivalue_line("markers", "file_config")
    config.addinivalue_line("markers", "env_config")
    config.addinivalue_line("markers", "readers")
    config.addinivalue_line("markers", "handlers")
    config.addinivalue_line("markers", "settings")
    config.addinivalue_line("markers", "field_type")
    config.addinivalue_line("markers", "field_default_value")
    config.addinivalue_line("markers", "field_default_params")
    config.addinivalue_line("markers", "alias")
    config.addinivalue_line("markers", "utils")
    config.addinivalue_line("markers", "case_sensitive")
    config.addinivalue_line("markers", "env_file")
    config.addinivalue_line("markers", "env")
    config.addinivalue_line("markers", "cli")
    config.addinivalue_line("markers", "secret")
    config.addinivalue_line("markers", "pyproject")
    config.addinivalue_line("markers", "connectors")


@pytest.fixture(scope="session")
def platform_system():
    yield platform.system()


@pytest.fixture
def cwd_to_tmp(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)

    yield tmp_path

    os.chdir(cwd)


@pytest.fixture
def path_base_dir(tmp_path, monkeypatch):
    call_file = tmp_path / "__init__.py"
    call_file.touch(exist_ok=True)

    class PatchedInitSettings(InitSettings):
        @staticmethod
        def _search_called_file():
            return call_file.as_posix(), 0

    monkeypatch.setattr(arfi_settings.init_config, "InitSettings", PatchedInitSettings)
    init_settings = PatchedInitSettings()
    monkeypatch.setattr(arfi_settings.init_config, "init_settings", init_settings)
    monkeypatch.setattr(arfi_settings.main, "init_settings", init_settings)
    yield


@pytest.fixture
def tests_dir():
    cwd = os.getcwd()
    os.chdir("./tests")

    yield tests_dir

    os.chdir(cwd)


@pytest.fixture
def config_dir(cwd_to_tmp):
    config_dir = cwd_to_tmp / "config"
    config_dir.mkdir(exist_ok=True)
    yield config_dir


@pytest.fixture
def secrets_dir(cwd_to_tmp):
    secrets_dir = cwd_to_tmp / "secrets"
    secrets_dir.mkdir(exist_ok=True)
    yield secrets_dir


@pytest.fixture
def cwd_to_tmp_src_project_settings(tmp_path):
    cwd = os.getcwd()
    nested_cwd = tmp_path / "src" / "project" / "settings"
    nested_cwd.mkdir(parents=True, exist_ok=True)
    os.chdir(nested_cwd)

    yield nested_cwd

    os.chdir(cwd)


@pytest.fixture
def cwd_multi_nested(tmp_path):
    cwd = os.getcwd()
    multi_nested_cwd = tmp_path / "src" / "project" / "settings" / "multi" / "nested" / "directory"
    multi_nested_cwd.mkdir(parents=True, exist_ok=True)
    os.chdir(multi_nested_cwd)

    yield multi_nested_cwd

    os.chdir(cwd)


@pytest.fixture
def empty_pyproject_toml_file(cwd_to_tmp):
    pyproject_toml_file = cwd_to_tmp / "pyproject.toml"
    pyproject_toml_file.touch(exist_ok=True)
    yield pyproject_toml_file


@pytest.fixture
def empty_env_file(cwd_to_tmp):
    conf_file = cwd_to_tmp / ".env"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_env_file(empty_env_file):
    env_file = empty_env_file
    env_file.write_text(
        """
        PATH_CONFIG_FILE = '.env'
        """
    )
    yield env_file


@pytest.fixture
def empty_prod_env_file(cwd_to_tmp):
    conf_file = cwd_to_tmp / "prod.env"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_prod_env_file(empty_prod_env_file):
    env_file = empty_prod_env_file
    env_file.write_text(
        """
        PATH_CONFIG_FILE = 'prod.env'
        """
    )
    yield env_file


@pytest.fixture
def empty_config_without_extension(cwd_to_tmp):
    conf_file = cwd_to_tmp / "config"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_config_without_extension(empty_config_without_extension):
    conf_file = empty_config_without_extension
    conf_file.write_text(
        """
        path_config_file = 'config'
        """
    )
    yield conf_file


@pytest.fixture
def empty_config_toml(cwd_to_tmp):
    conf_file = cwd_to_tmp / "config.toml"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_config_toml(empty_config_toml):
    conf_file = empty_config_toml
    conf_file.write_text(
        """
        path_config_file = 'config.toml'
        """
    )
    yield conf_file


@pytest.fixture
def empty_config_yaml(cwd_to_tmp):
    conf_file = cwd_to_tmp / "config.yaml"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def empty_config_yml(cwd_to_tmp):
    conf_file = cwd_to_tmp / "config.yml"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def empty_config_json(cwd_to_tmp):
    conf_file = cwd_to_tmp / "config.json"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def empty_config_cnf(cwd_to_tmp):
    conf_file = cwd_to_tmp / "config.cnf"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_config_cnf(empty_config_cnf):
    conf_file = empty_config_cnf
    conf_file.write_text(
        """
        path_config_file = 'config.cnf'
        """
    )
    yield conf_file


@pytest.fixture
def empty_config_config_toml(config_dir):
    conf_file = config_dir / "config.toml"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_config_config_toml(empty_config_config_toml):
    conf_file = empty_config_config_toml
    conf_file.write_text(
        """
        path_config_file = 'config/config.toml'
        """
    )
    yield conf_file


@pytest.fixture
def empty_config_config_yaml(config_dir):
    conf_file = config_dir / "config.yaml"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_config_config_yaml(empty_config_config_yaml):
    conf_file = empty_config_config_yaml
    conf_file.write_text(
        """
        path_config_file: 'config/config.yaml'
        """
    )
    yield conf_file


@pytest.fixture
def empty_config_config_yml(config_dir):
    conf_file = config_dir / "config.yml"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_config_config_yml(empty_config_config_yml):
    conf_file = empty_config_config_yml
    conf_file.write_text(
        """
        path_config_file: 'config/config.yml'
        """
    )
    yield conf_file


@pytest.fixture
def empty_config_config_json(config_dir):
    conf_file = config_dir / "config.json"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_config_config_json(empty_config_config_json):
    conf_file = empty_config_config_json
    conf_file.write_text(
        """
        {
            "path_config_file": "config/config.json"
        }
        """
    )
    yield conf_file


@pytest.fixture
def empty_secret_path_config_file(secrets_dir):
    conf_file = secrets_dir / "path_config_file"
    conf_file.touch(exist_ok=True)
    yield conf_file


@pytest.fixture
def simple_data_secret_path_config_file(empty_secret_path_config_file):
    conf_file = empty_secret_path_config_file
    conf_file.write_text(
        """
        secrets/path_config_file
        """
    )
    yield conf_file


@pytest.fixture
def alias_data_config_config_toml(empty_config_config_toml):
    conf_file = empty_config_config_toml
    conf_file.write_text(
        """
        alias_config_data = 'alias_config_data'
        ALIAS_CONFIG_DATA = 'ALIAS_CONFIG_DATA'
        AliasConfigData = "AliasConfigData"
        Alias_Config_Data = "Alias_Config_Data"
        config_data = "config_data"
        CONFIG_DATA = "CONFIG_DATA"
        ConfigData = "ConfigData"
        configData = "configData"

        mode = "mode"
        MODE = "MODE"
        Mode = "Mode"

        alias_path = ["alias_path_1","alias_path_2"]
        OTHER_ALIAS_PATH = ["other_alias_path_1","other_alias_path_2"]
        complex_alias_path = {alias_path = ["alias_path_1","alias_path_2"]}
        OTHER_COMPLEX_ALIAS_PATH = {Alias_Path=["other_alias_path_1","other_alias_path_2"],ALIAS_PATH=['OTHER_ALIAS_PATH_1','OTHER_ALIAS_PATH_2']}

        asd_test = 'asd_test'
        """
    )
    yield conf_file


@pytest.fixture
def mode_prod_data_config_config_toml(empty_config_config_toml):
    conf_file = empty_config_config_toml
    conf_file.write_text(
        """
        mode = "prod"
        """
    )
    yield conf_file


@pytest.fixture
def databese_data_env_file(empty_env_file):
    env_file = empty_env_file
    env_file.write_text(
        """
        db_type = 'mysql'
        DB_TYPE = 'postgres'
        db__db_type = 'mysql'
        DB__DB_TYPE = 'postgres'
        DB__DATABASE = 'DB__DATABASE'
        DB__POSTGRES__DATABASE = 'DB__POSTGRES_DATABASE'
        db__MySQL__databese = 'db__MySQL__databese'
        """
    )
    yield env_file


@pytest.fixture
def env_include_exclude_expected():
    expected = (
        "'env_file', 'env_prefix', 'env_prefix_as_mode_dir', "
        "'env_prefix_as_nested_mode_dir', 'env_prefix_as_source_mode_dir', "
        "'env_file_encoding', 'env_case_sensitive', "
        "'env_nested_delimiter', 'env_ignore_missing', "
        "'env_include_inherit_parent' or 'env_exclude_inherit_parent'"
    )
    return expected


@pytest.fixture
def env_include_exclude_msg():
    msg = (
        "Input should be 'env_file', 'env_prefix', 'env_prefix_as_mode_dir', "
        "'env_prefix_as_nested_mode_dir', 'env_prefix_as_source_mode_dir', "
        "'env_file_encoding', 'env_case_sensitive', 'env_nested_delimiter', "
        "'env_ignore_missing', 'env_include_inherit_parent' or "
        "'env_exclude_inherit_parent'"
    )
    return msg


@pytest.fixture
def conf_include_exclude_expected():
    expected = (
        "'conf_file', 'conf_dir', 'conf_ext', 'conf_file_encoding', "
        "'conf_case_sensitive', 'conf_ignore_missing', "
        "'conf_custom_ext_handler', 'conf_include_inherit_parent' or "
        "'conf_exclude_inherit_parent'"
    )
    return expected


@pytest.fixture
def conf_include_exclude_msg():
    msg = (
        "Input should be 'conf_file', 'conf_dir', 'conf_ext', "
        "'conf_file_encoding', 'conf_case_sensitive', 'conf_ignore_missing', "
        "'conf_custom_ext_handler', 'conf_include_inherit_parent' or "
        "'conf_exclude_inherit_parent'"
    )
    return msg


@pytest.fixture
def include_exclude_expected():
    expected = (
        "'conf_file', 'conf_dir', 'conf_ext', 'conf_file_encoding', "
        "'conf_case_sensitive', 'conf_ignore_missing', "
        "'conf_custom_ext_handler', 'conf_include_inherit_parent', "
        "'conf_exclude_inherit_parent', 'env_file', 'env_prefix', "
        "'env_prefix_as_mode_dir', 'env_prefix_as_nested_mode_dir', "
        "'env_prefix_as_source_mode_dir', 'env_file_encoding', "
        "'env_case_sensitive', 'env_nested_delimiter', "
        "'env_ignore_missing', 'env_include_inherit_parent' or "
        "'env_exclude_inherit_parent'"
    )
    return expected


@pytest.fixture
def include_exclude_msg():
    msg = (
        "Input should be 'conf_file', 'conf_dir', 'conf_ext', "
        "'conf_file_encoding', 'conf_case_sensitive', 'conf_ignore_missing', "
        "'conf_custom_ext_handler', 'conf_include_inherit_parent', "
        "'conf_exclude_inherit_parent', 'env_file', 'env_prefix', "
        "'env_prefix_as_mode_dir', 'env_prefix_as_nested_mode_dir', "
        "'env_prefix_as_source_mode_dir', 'env_file_encoding', "
        "'env_case_sensitive', 'env_nested_delimiter', 'env_ignore_missing', "
        "'env_include_inherit_parent' or 'env_exclude_inherit_parent'"
    )
    return msg
