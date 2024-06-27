import pytest
from pydantic import Field, AliasChoices, AliasPath, ValidationError

from arfi_settings import ArFiSettings, SettingsConfigDict


# @pytest.mark.current
@pytest.mark.alias
@pytest.mark.parametrize(
    "data",
    [
        {"app": {"mode": "asd"}},
        {"app": {"MODE": "asd"}},
    ],
)
def test_mode_alias(data):
    class AppSettings(ArFiSettings):
        pass

    class AppConfig(ArFiSettings):
        app: AppSettings

    config = AppConfig(**data)
    assert config.MODE is None
    assert config.app.MODE == "asd"


# @pytest.mark.current
@pytest.mark.alias
def test_without_aliase(alias_data_config_config_toml, path_base_dir):
    class AppConfig(ArFiSettings):
        read_config_force = False
        alias_config_data: str = "default"

    config = AppConfig()
    assert config.alias_config_data == "default"

    class AppConfig(ArFiSettings):
        alias_config_data: str = "default"

    config = AppConfig()
    assert config.alias_config_data == "alias_config_data"


# @pytest.mark.current
@pytest.mark.alias
def test_strict_aliase(alias_data_config_config_toml, path_base_dir):
    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            "default",
            alias="ALIAS_CONFIG_DATA",
        )

    config = AppConfig()
    assert config.alias_config_data == "ALIAS_CONFIG_DATA"


# @pytest.mark.current
@pytest.mark.alias
def test_validation_aliase(alias_data_config_config_toml, path_base_dir):
    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            "default",
            alias="ALIAS_CONFIG_DATA",
            validation_alias="AliasConfigData",
        )

    config = AppConfig()
    assert config.alias_config_data == "AliasConfigData"


@pytest.mark.alias
def test_validation_aliase_aliaschoices(alias_data_config_config_toml, path_base_dir):
    class AppConfig(ArFiSettings):
        # read_config_force = False
        alias_config_data: str = Field(
            "default",
            alias="Alias_Config_Data",
            validation_alias=AliasChoices("configData", "AliasConfigData"),
        )

    config = AppConfig()
    assert config.alias_config_data == "configData"


@pytest.mark.alias
def test_validation_aliase_multi_aliaspath(alias_data_config_config_toml, path_base_dir):
    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            "default",
            validation_alias=AliasPath("complex_alias_path", "alias_path", 0),
        )

    config = AppConfig()
    assert config.alias_config_data == "alias_path_1"


@pytest.mark.alias
def test_validation_aliase_aliaspath(alias_data_config_config_toml, path_base_dir):
    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            "default",
            alias="Alias_Config_Data",
            validation_alias=AliasPath("alias_path", 0),
        )

    config = AppConfig()
    assert config
    assert config.alias_config_data == "alias_path_1"


# @pytest.mark.current
@pytest.mark.alias
def test_validation_aliase_with_extra(alias_data_config_config_toml, path_base_dir):
    data = {"alias_path": ["alias_path_1", "alias_path_2"], "asd": "alias_path_2"}

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(validation_alias=AliasPath("alias_path", 0))
        asd: str = Field(validation_alias=AliasChoices("asd", AliasPath("alias_path", 1)))

    config = AppConfig(**data)
    assert config
    assert config.alias_config_data == "alias_path_1"
    assert config.asd == "alias_path_2"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(validation_alias=AliasPath("alias_path", 0))
        asd: str = Field(validation_alias=AliasChoices(AliasPath("alias_path", 1), "asd"))

    config = AppConfig(**data)
    assert config
    assert config.alias_config_data == "alias_path_1"
    assert config.asd == "alias_path_2"

    class AppConfig(ArFiSettings):
        read_config_force = False
        alias_config_data: str = Field(validation_alias=AliasPath("alias_path", 0))
        asd: str = Field(validation_alias=AliasChoices("asd", AliasPath("alias_path", 1)))

    config = AppConfig(**data)
    assert config
    assert config.alias_config_data == "alias_path_1"
    assert config.asd == "alias_path_2"

    with pytest.raises(ValidationError) as excinfo:

        class AppConfig(ArFiSettings):
            read_config_force = False
            alias_config_data: str = Field(validation_alias=AliasPath("alias_path", 0))
            asd: str = Field(validation_alias=AliasChoices(AliasPath("alias_path", 1), "asd"))

        _ = AppConfig(**data)
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "extra_forbidden",
            "loc": ("asd",),
            "msg": "Extra inputs are not permitted",
            "input": "alias_path_2",
        },
    ]

    class AppConfig(ArFiSettings):
        read_config_force = False
        alias_config_data: str = Field(validation_alias=AliasPath("alias_path", 0))
        asd: str = Field(validation_alias=AliasChoices(AliasPath("alias_path", 1), "asd"))

        model_config = SettingsConfigDict(
            extra="ignore",
        )

    config = AppConfig(**data)
    assert config
    assert config.alias_config_data == "alias_path_1"
    assert config.asd == "alias_path_2"


# @pytest.mark.current
@pytest.mark.alias
@pytest.mark.parametrize(
    "validation_alias_config, validation_alias_asd, data, res_alias_config_data, res_asd",
    [
        (
            AliasPath("alias_path", 0),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {},
            "alias_path_1",
            "alias_path_2",
        ),
        (
            AliasPath("alias_path"),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {},
            ["alias_path_1", "alias_path_2"],
            "alias_path_2",
        ),
        (
            AliasPath("complex_alias_path", "alias_path"),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {},
            ["alias_path_1", "alias_path_2"],
            "alias_path_2",
        ),
        (
            AliasPath("alias_path", 0),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {"alias_path": ["alias_path_1", "alias_path_2"]},
            "alias_path_1",
            "alias_path_2",
        ),
        (
            AliasPath("alias_path", 0),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {"alias_path": ["alias_path_1"], "asd": "alias_path_8"},
            "alias_path_1",
            "alias_path_8",
        ),
        (
            AliasPath("alias_path", 0),
            AliasChoices(AliasPath("alias_path", 1), "asd"),
            {"alias_path": ["alias_path_1"], "asd": "alias_path_8"},
            "alias_path_1",
            "alias_path_8",
        ),
        (
            AliasPath("alias_path", 0),
            AliasChoices(AliasPath("alias_path", 1), "asd"),
            {"alias_path": ["alias_path_1"]},
            "alias_path_1",
            "alias_path_2",
        ),
        (
            AliasPath("alias_path", 0),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {"alias_path": ["alias_path_1", "alias_path_2"], "asd": "alias_path_8"},
            "alias_path_1",
            "alias_path_8",
        ),
        (
            AliasPath("alias_path", 0),
            AliasChoices(AliasPath("alias_path", 1), "asd"),
            {"alias_path": ["alias_path_1", "alias_path_2"], "asd": "alias_path_8"},
            "alias_path_1",
            "alias_path_2",
        ),
        (
            AliasChoices("alias_config_data", "Alias_Config_Data"),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {},
            "alias_config_data",
            "alias_path_2",
        ),
        (
            AliasChoices("alias_config_data", "Alias_Config_Data"),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {"alias_config_data": "Alias_Config_Data"},
            "Alias_Config_Data",
            "alias_path_2",
        ),
        (
            AliasChoices("Alias_Config_Data", "alias_config_data"),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {"alias_config_data": "Alias_Config_Data"},
            "Alias_Config_Data",
            "alias_path_2",
        ),
        (
            AliasChoices("alias_config_data", "Alias_Config_Data"),
            AliasChoices("asd", AliasPath("alias_path", 1)),
            {"Alias_Config_Data": "Alias_Config_Data"},
            "Alias_Config_Data",
            "alias_path_2",
        ),
    ],
)
def test_validation_aliase_aliaschoices_aliaspath(
    alias_data_config_config_toml,
    validation_alias_config,
    validation_alias_asd,
    data,
    res_alias_config_data,
    res_asd,
    path_base_dir,
):
    class AppConfig(ArFiSettings):
        alias_config_data: str | list | dict = Field(validation_alias=validation_alias_config)
        asd: str = Field(validation_alias=validation_alias_asd)

    config = AppConfig(**data)
    assert config.alias_config_data == res_alias_config_data
    assert config.asd == res_asd


# @pytest.mark.current
@pytest.mark.alias
def test_validation_aliase_aliaschoices_aliaspath_on_default_valut(
    alias_data_config_config_toml,
    path_base_dir,
):
    class AppSettings(ArFiSettings):
        alias_config_data: str = Field(validation_alias=AliasPath("alias_path", 0))
        asd: str = Field(validation_alias=AliasChoices("asd", AliasPath("alias_path", 1)))

    class AppConfig(ArFiSettings):
        app: AppSettings

    app = AppSettings()
    config = AppConfig(app=app)
    assert config.app.alias_config_data == "alias_path_1"
    assert config.app.asd == "alias_path_2"

    config = AppConfig(app=AppSettings())
    assert config.app.alias_config_data == "alias_path_1"
    assert config.app.asd == "alias_path_2"

    config = AppConfig(app=AppSettings(alias_path=["alias_path_1"]))
    assert config.app.alias_config_data == "alias_path_1"
    assert config.app.asd == "alias_path_2"

    config = AppConfig(app=AppSettings(alias_path=["alias_path_1"], asd="alias_path_8"))
    assert config.app.alias_config_data == "alias_path_1"
    assert config.app.asd == "alias_path_8"

    config = AppConfig(app=AppSettings(alias_path=["alias_path_1", "alias_path_2"], asd="alias_path_8"))
    assert config.app.alias_config_data == "alias_path_1"
    assert config.app.asd == "alias_path_8"

    config = AppConfig(app=AppSettings(alias_config_data="alias_path_1", asd="alias_path_8"))
    assert config.app.alias_config_data == "alias_path_1"
    assert config.app.asd == "alias_path_8"

    with pytest.raises(ValidationError) as excinfo:

        class AppSettings(ArFiSettings):
            read_config_force = False
            alias_config_data: str = Field("default1", validation_alias=AliasPath("alias_path", 0))
            asd: str = Field("default2", validation_alias=AliasChoices("asd", AliasPath("alias_path", 1)))

        _ = AppConfig(app=AppSettings(alias_config_data="alias_path_1", asd="alias_path_8"))
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "extra_forbidden",
            "loc": ("alias_config_data",),
            "msg": "Extra inputs are not permitted",
            "input": "alias_path_1",
        },
    ]

    class AppSettings(ArFiSettings):
        read_config_force = False
        alias_config_data: str = Field("default1", validation_alias=AliasPath("alias_path", 0))
        asd: str = Field("default2", validation_alias=AliasChoices("asd", AliasPath("alias_path", 1)))
        model_config = SettingsConfigDict(extra="ignore")

    config = AppConfig(app=AppSettings(alias_config_data="alias_path_1", asd="alias_path_8"))
    assert config.app.alias_config_data == "default1"
    assert config.app.asd == "alias_path_8"

    config = AppConfig(app=AppSettings(alias_path=["alias_path_9"], asd="alias_path_8"))
    assert config.app.alias_config_data == "alias_path_9"
    assert config.app.asd == "alias_path_8"

    config = AppConfig(
        app=AppSettings(
            alias_config_data="alias_path_1",
            alias_path=["alias_path_9"],
            asd="alias_path_8",
        )
    )
    assert config.app.alias_config_data == "alias_path_9"
    assert config.app.asd == "alias_path_8"

    app = AppSettings(alias_path=["alias_path_1"], asd="alias_path_8")
    config = AppConfig(app=app)
    assert config.app.alias_config_data == "alias_path_1"
    assert config.app.asd == "alias_path_8"

    test_app = AppSettings(alias_path=["alias_path_1"], asd="alias_path_8")

    class AppConfig(ArFiSettings):
        app: AppSettings = test_app

    config = AppConfig()
    assert config.app.alias_config_data == "alias_path_1"
    assert config.app.asd == "alias_path_8"

    config = AppConfig(app=AppSettings(alias_path=["alias_path_1"], asd="ALIAS_PATH_5"))
    assert config.app.alias_config_data == "alias_path_1"
    assert config.app.asd == "ALIAS_PATH_5"


# @pytest.mark.current
@pytest.mark.alias
def test_alias_generator(alias_data_config_config_toml, path_base_dir):
    def to_camel(string: str):
        return "".join(x.capitalize() for x in string.split("_"))

    class AppConfig(ArFiSettings):
        alias_config_data: str
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "AliasConfigData"

    config = AppConfig(alias_config_data="alias_config_data")
    assert config.alias_config_data == "AliasConfigData"

    config = AppConfig(AliasConfigData="alias_config_data")
    assert config.alias_config_data == "alias_config_data"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            validation_alias=AliasChoices(
                "Alias_Config_Data",
                "alias_config_data",
            ),
        )
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "Alias_Config_Data"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            alias="Alias_Config_Data",
            validation_alias=AliasChoices(
                "CONFIG_DATA",
            ),
        )
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "CONFIG_DATA"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            alias_priority=1,
            alias="Alias_Config_Data",
            validation_alias=AliasChoices(
                "configData",
            ),
        )
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "AliasConfigData"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            alias_priority=2,
            alias="Alias_Config_Data",
            validation_alias=AliasChoices(
                "configData",
            ),
        )
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "configData"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            alias_priority=30,
            alias="Alias_Config_Data",
            validation_alias=AliasChoices(
                "configData",
            ),
        )
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "configData"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            alias_priority=1,
            alias="configData",
        )
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "AliasConfigData"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            alias_priority=2,
            alias="configData",
        )
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "configData"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(
            alias_priority=30,
            alias="configData",
        )
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "configData"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(alias_priority=0)
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "AliasConfigData"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(alias_priority=1)
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "AliasConfigData"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(alias_priority=2)
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "AliasConfigData"

    class AppConfig(ArFiSettings):
        alias_config_data: str = Field(alias_priority=30)
        model_config = SettingsConfigDict(alias_generator=to_camel)

    config = AppConfig()
    assert config.alias_config_data == "AliasConfigData"
