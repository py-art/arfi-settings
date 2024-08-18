import pytest

from arfi_settings import ArFiSettings


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_1(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings
        ordered_settings = ["init_kwargs"]

    config = AppConfig()
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings_inherit_parent is True


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_2(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings()
        ordered_settings = ["init_kwargs"]

    config = AppConfig()
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings_inherit_parent is True


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_3(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings(_ordered_settings=["cli"])
        ordered_settings = ["init_kwargs"]

    config = AppConfig()
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings_inherit_parent is True


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_4(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings(
            _ordered_settings=["cli"],
            _ordered_settings_inherit_parent=False,
        )
        ordered_settings = ["init_kwargs"]

    config = AppConfig()
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == ["cli"]
    assert config.app.ordered_settings_inherit_parent is False


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_5(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings(
            _ordered_settings_inherit_parent=False,
        )
        ordered_settings = ["init_kwargs"]

    config = AppConfig()
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == [
        "cli",
        "init_kwargs",
        "env",
        "env_file",
        "secrets",
        "conf_file",
    ]
    assert config.app.ordered_settings_inherit_parent is False


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_6(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings
        ordered_settings = ["init_kwargs"]

    config = AppConfig(
        app=AppSettings(
            _ordered_settings=["cli"],
        )
    )
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings_inherit_parent is True


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_7(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings
        ordered_settings = ["init_kwargs"]

    config = AppConfig(
        app=AppSettings(
            _ordered_settings_inherit_parent=False,
            _ordered_settings=["cli"],
        )
    )
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == ["cli"]
    assert config.app.ordered_settings_inherit_parent is False


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_8(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings()
        ordered_settings = ["init_kwargs"]

    config = AppConfig(
        app=AppSettings(
            _ordered_settings=["cli"],
        )
    )
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings_inherit_parent is True


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_9(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings()
        ordered_settings = ["init_kwargs"]

    config = AppConfig(
        app=AppSettings(
            _ordered_settings_inherit_parent=False,
            _ordered_settings=["cli"],
        )
    )
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == ["cli"]
    assert config.app.ordered_settings_inherit_parent is False


# @pytest.mark.current
@pytest.mark.settings
def test_ordered_settings_10(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings(
            _ordered_settings_inherit_parent=True,
        )
        ordered_settings = ["init_kwargs"]

    config = AppConfig(
        app=AppSettings(
            _ordered_settings_inherit_parent=False,
            _ordered_settings=["cli"],
        )
    )
    assert config.ordered_settings == ["init_kwargs"]
    assert config.app.ordered_settings == ["cli"]
    assert config.app.ordered_settings_inherit_parent is False
