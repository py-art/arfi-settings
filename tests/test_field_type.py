import pytest

from arfi_settings import ArFiSettings, ArFiSettingsError


@pytest.mark.field_type
def test_legal_field_type(cwd_to_tmp, path_base_dir):
    class CustomSettings(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings = AppSettings()

    config = AppConfig()
    assert config

    class AppConfig(ArFiSettings):
        app: CustomSettings | AppSettings = AppSettings()

    config = AppConfig()
    assert config

    class AppConfig(ArFiSettings):
        app: list[AppSettings | CustomSettings] = [
            AppSettings(),
            CustomSettings(),
        ]

    config = AppConfig()
    assert config


@pytest.mark.field_type
def test_illegal_field_type(cwd_to_tmp, path_base_dir):
    class AppSettings(ArFiSettings):
        pass

    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig(ArFiSettings):
            app: ArFiSettings = AppSettings()

        _ = AppConfig()
    assert "cannot contain ArFiSettings type" in str(excinfo)

    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig(ArFiSettings):
            app: ArFiSettings | None = AppSettings()

        _ = AppConfig()
    assert "cannot contain ArFiSettings type" in str(excinfo)

    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig(ArFiSettings):
            app: list[ArFiSettings] = [
                AppSettings(),
            ]

        _ = AppConfig()
    assert "cannot contain ArFiSettings type" in str(excinfo)

    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig(ArFiSettings):
            app: dict[str, ArFiSettings] = dict(asd=AppSettings())

        _ = AppConfig()
    assert "cannot contain ArFiSettings type" in str(excinfo)

    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig(ArFiSettings):
            app: AppSettings | tuple[dict[str, ArFiSettings], str] | str = AppSettings()

        _ = AppConfig()
    assert "cannot contain ArFiSettings type" in str(excinfo)
