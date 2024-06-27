import pydantic
import pytest

from arfi_settings import ArFiSettings, EnvConfigDict, SettingsConfigDict


# @pytest.mark.current
@pytest.mark.env_config
def test_class_env_exclude_inherit_parent_valid_input(
    cwd_to_tmp,
    env_include_exclude_expected,
    env_include_exclude_msg,
):
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig()
    assert config.settings_config.env_exclude_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class A(ArFiSettings):
            env_config = EnvConfigDict(
                env_exclude_inherit_parent=True,
            )

        A()
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": (
                "env_config",
                "env_exclude_inherit_parent",
            ),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_exclude_inherit_parent=[],
        )

    config = AppConfig()
    assert config.settings_config.env_exclude_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class B(ArFiSettings):
            env_config = EnvConfigDict(
                env_exclude_inherit_parent=["test"],
            )

        B()

    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "literal_error",
            "loc": (
                "env_exclude_inherit_parent",
                0,
            ),
            "ctx": {
                "expected": env_include_exclude_expected,
            },
            "msg": env_include_exclude_msg,
            "input": "test",
        },
    ]

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class C(ArFiSettings):
            model_config = SettingsConfigDict(
                env_exclude_inherit_parent=True,
            )

        C()
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": ("env_exclude_inherit_parent",),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class D(ArFiSettings):
            model_config = SettingsConfigDict(
                exclude_inherit_parent=True,
            )

        D()
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": ("exclude_inherit_parent",),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]


# @pytest.mark.current
@pytest.mark.env_config
def test_class_env_exclude_inherit_parent(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig()
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_file"],
            exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig()
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_nested_delimiter"],
            exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig()
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]


# @pytest.mark.current
@pytest.mark.env_config
def test_only_init_env_exclude_inherit_parent(
    cwd_to_tmp,
    env_include_exclude_expected,
    env_include_exclude_msg,
):
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig(
        _env_exclude_inherit_parent=[],
    )
    assert config.settings_config.env_exclude_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    config = AppConfig(
        _exclude_inherit_parent=[],
    )
    assert config.settings_config.env_exclude_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:
        AppConfig(
            _env_exclude_inherit_parent=True,
        )
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": ("_env_exclude_inherit_parent",),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    with pytest.raises(pydantic.ValidationError) as excinfo:
        AppConfig(
            _env_exclude_inherit_parent=["test"],
        )
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "literal_error",
            "loc": (
                "_env_exclude_inherit_parent",
                0,
            ),
            "ctx": {
                "expected": env_include_exclude_expected,
            },
            "msg": env_include_exclude_msg,
            "input": "test",
        },
    ]

    config = AppConfig(
        _env_exclude_inherit_parent=["env_file"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _exclude_inherit_parent=["env_file"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _env_exclude_inherit_parent=["env_file"],
        _exclude_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]


# @pytest.mark.current
@pytest.mark.env_config
def test_init_and_class_env_exclude_inherit_parent(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _env_exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
        _exclude_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig(
        _env_exclude_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix"]

    config = AppConfig(
        _exclude_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix_as_source_mode_dir"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_file"],
            exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig(
        _env_exclude_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix"]

    config = AppConfig(
        _exclude_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_nested_delimiter"],
            exclude_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig(
        _env_exclude_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix"]

    config = AppConfig(
        _exclude_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_exclude_inherit_parent == ["env_prefix"]
    assert config.settings_config.exclude_inherit_parent == ["env_prefix"]


# @pytest.mark.current
@pytest.mark.env_config
def test_class_env_include_inherit_parent_valid_input(
    cwd_to_tmp,
    env_include_exclude_expected,
    env_include_exclude_msg,
):
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class A(ArFiSettings):
            env_config = EnvConfigDict(
                env_include_inherit_parent=True,
            )

        A()

    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": (
                "env_config",
                "env_include_inherit_parent",
            ),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=[],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class B(ArFiSettings):
            env_config = EnvConfigDict(
                env_include_inherit_parent=["test"],
            )

        B()
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "literal_error",
            "loc": (
                "env_include_inherit_parent",
                0,
            ),
            "ctx": {
                "expected": env_include_exclude_expected,
            },
            "msg": env_include_exclude_msg,
            "input": "test",
        },
    ]


# @pytest.mark.current
@pytest.mark.env_config
def test_class_env_include_inherit_parent(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file"],
            include_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_nested_delimiter"],
            include_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_file"]


# @pytest.mark.current
@pytest.mark.env_config
def test_only_init_env_include_inherit_parent(
    cwd_to_tmp,
    env_include_exclude_expected,
    env_include_exclude_msg,
):
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig(
        _env_include_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []

    config = AppConfig(
        _include_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:
        AppConfig(
            _env_include_inherit_parent=True,
        )
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": ("_env_include_inherit_parent",),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    with pytest.raises(pydantic.ValidationError) as excinfo:
        AppConfig(
            _env_include_inherit_parent=["test"],
        )
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "literal_error",
            "loc": (
                "_env_include_inherit_parent",
                0,
            ),
            "ctx": {
                "expected": env_include_exclude_expected,
            },
            "msg": env_include_exclude_msg,
            "input": "test",
        },
    ]

    config = AppConfig(
        _env_include_inherit_parent=["env_file"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_file"]

    config = AppConfig(
        _env_include_inherit_parent=["env_file"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_file"]

    config = AppConfig(
        _env_include_inherit_parent=["env_file"],
        _include_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_file"]


# @pytest.mark.current
@pytest.mark.env_config
def test_init_and_class_env_include_inherit_parent(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_include_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.include_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _include_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.include_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _env_include_inherit_parent=["env_prefix_as_source_mode_dir"],
        _include_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.include_inherit_parent == ["env_prefix_as_source_mode_dir"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_include_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.include_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _include_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.include_inherit_parent == ["env_prefix_as_source_mode_dir"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_include_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.include_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _include_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.include_inherit_parent == ["env_prefix_as_source_mode_dir"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig(
        _env_include_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix"]
    assert config.settings_config.include_inherit_parent == ["env_prefix"]

    config = AppConfig(
        _include_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix"]
    assert config.settings_config.include_inherit_parent == ["env_prefix"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            include_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_include_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.include_inherit_parent == ["env_prefix_as_source_mode_dir"]

    config = AppConfig(
        _include_inherit_parent=["env_prefix_as_source_mode_dir"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix_as_source_mode_dir"]
    assert config.settings_config.include_inherit_parent == ["env_prefix_as_source_mode_dir"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file"],
            include_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig(
        _env_include_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix"]
    assert config.settings_config.include_inherit_parent == ["env_prefix"]

    config = AppConfig(
        _include_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix"]
    assert config.settings_config.include_inherit_parent == ["env_prefix"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_nested_delimiter"],
            include_inherit_parent=["env_prefix_as_source_mode_dir"],
        )

    config = AppConfig(
        _env_include_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix"]
    assert config.settings_config.include_inherit_parent == ["env_prefix"]

    config = AppConfig(
        _include_inherit_parent=["env_prefix"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_prefix"]
    assert config.settings_config.include_inherit_parent == ["env_prefix"]


# @pytest.mark.current
@pytest.mark.env_config
def test_combination_class_env_include_exclude_parent(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file"],
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file"],
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            include_inherit_parent=["env_file"],
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_exclude_inherit_parent=[],
        )
        model_config = SettingsConfigDict(
            include_inherit_parent=["env_file"],
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file", "env_ignore_missing"],
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file", "env_ignore_missing"],
        )
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file", "env_ignore_missing"],
        )
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file", "env_ignore_missing"],
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file", "env_ignore_missing"],
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            include_inherit_parent=["env_file", "env_ignore_missing"],
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig()
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]


# @pytest.mark.current
@pytest.mark.env_config
def test_combination_init_and_class_env_include_exclude_parent(cwd_to_tmp):
    # 0
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_include_inherit_parent=["env_file"],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _env_include_inherit_parent=["env_file"],
        _env_exclude_inherit_parent=["env_file"],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _env_include_inherit_parent=["env_file"],
        _exclude_inherit_parent=["env_file"],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _env_exclude_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    config = AppConfig(
        _exclude_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _exclude_inherit_parent=["env_ignore_missing"],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_ignore_missing"]

    config = AppConfig(
        _env_include_inherit_parent=["env_ignore_missing"],
        _env_exclude_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == []

    config = AppConfig(
        _env_include_inherit_parent=["env_ignore_missing"],
        _exclude_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _env_include_inherit_parent=["env_ignore_missing"],
        _exclude_inherit_parent=["env_ignore_missing"],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["env_file"],
        _exclude_inherit_parent=["env_ignore_missing"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["env_file"],
        _exclude_inherit_parent=["env_ignore_missing", "env_file"],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_ignore_missing", "env_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_ignore_missing", "env_file"]

    # 1
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _env_include_inherit_parent=["env_ignore_missing"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _include_inherit_parent=["env_ignore_missing"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _include_inherit_parent=["env_ignore_missing"],
        _env_exclude_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == []

    config = AppConfig(
        _include_inherit_parent=["env_ignore_missing"],
        _exclude_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    # 2
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file"],
        )
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _include_inherit_parent=["env_ignore_missing"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_file"]
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["env_file"]

    config = AppConfig(
        _env_include_inherit_parent=["env_ignore_missing"],
        _env_exclude_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == []

    # 3
    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file"],
            env_exclude_inherit_parent=["env_file"],
        )

    config = AppConfig(
        _include_inherit_parent=["env_ignore_missing"],
        _env_exclude_inherit_parent=[],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.env_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == []

    # 4
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_include_inherit_parent=["env_file", "env_ignore_missing"],
            env_exclude_inherit_parent=["env_nested_delimiter"],
        )

    config = AppConfig(
        _include_inherit_parent=["env_nested_delimiter"],
    )
    assert config.settings_config.env_include_inherit_parent == []
    assert config.settings_config.env_exclude_inherit_parent == ["env_nested_delimiter"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["env_nested_delimiter"]

    config = AppConfig(
        _exclude_inherit_parent=["env_ignore_missing"],
    )
    assert config.settings_config.env_include_inherit_parent == ["env_file"]
    assert config.settings_config.env_exclude_inherit_parent == ["env_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["env_file"]
    assert config.settings_config.exclude_inherit_parent == ["env_ignore_missing"]


# @pytest.mark.current
@pytest.mark.env_config
def test_env_include_inherit_parent(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix_as_mode_dir=True,
            env_file_encoding="cp1251",
        )

    config = AppConfig()
    assert config.app.settings_config.env_prefix == "app_"
    assert config.app.settings_config.env_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.env_prefix == "app_proxy_"
    assert config.app.proxy.settings_config.env_file_encoding == "cp1251"

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_file_encoding"],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix_as_mode_dir=True,
            env_file_encoding="cp1251",
        )

    config = AppConfig()
    assert config.app.settings_config.env_prefix == ""
    assert config.app.settings_config.env_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.env_prefix == ""
    assert config.app.proxy.settings_config.env_file_encoding == "cp1251"

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()
        model_config = SettingsConfigDict(
            env_include_inherit_parent=["env_include_inherit_parent"],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix_as_mode_dir=True,
            env_file_encoding="cp1251",
            env_nested_delimiter=".",
            include_inherit_parent=["env_file_encoding"],
        )

    config = AppConfig()
    assert config.app.settings_config.env_prefix == ""
    assert config.app.settings_config.env_file_encoding == "cp1251"
    assert config.app.settings_config.env_nested_delimiter == ""
    assert config.app.proxy.settings_config.env_prefix == ""
    assert config.app.proxy.settings_config.env_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.env_nested_delimiter == ""

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()
        model_config = SettingsConfigDict(
            include_inherit_parent=["env_include_inherit_parent"],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix_as_mode_dir=True,
            env_file_encoding="cp1251",
            env_nested_delimiter=".",
            include_inherit_parent=["env_file_encoding"],
        )

    config = AppConfig()
    assert config.settings_config.env_prefix == ""
    assert config.settings_config.env_file_encoding == "cp1251"
    assert config.settings_config.env_nested_delimiter == "."
    assert config.app.settings_config.env_prefix == ""
    assert config.app.settings_config.env_file_encoding == "cp1251"
    assert config.app.settings_config.env_nested_delimiter == ""
    assert config.app.proxy.settings_config.env_prefix == ""
    assert config.app.proxy.settings_config.env_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.env_nested_delimiter == ""

    config = AppConfig(_env_file_encoding="utf-8")
    assert config.settings_config.env_prefix == ""
    assert config.settings_config.env_file_encoding == "utf-8"
    assert config.settings_config.env_nested_delimiter == "."
    assert config.app.settings_config.env_prefix == ""
    assert config.app.settings_config.env_file_encoding == "utf-8"
    assert config.app.settings_config.env_nested_delimiter == ""
    assert config.app.proxy.settings_config.env_prefix == ""
    assert config.app.proxy.settings_config.env_file_encoding == "utf-8"
    assert config.app.proxy.settings_config.env_nested_delimiter == ""

    config = AppConfig(
        _env_file_encoding="utf-8",
        app=AppSettings(
            _env_file_encoding="iso-8859-7",
        ),
    )
    assert config.settings_config.env_prefix == ""
    assert config.settings_config.env_file_encoding == "utf-8"
    assert config.settings_config.env_nested_delimiter == "."
    assert config.app.settings_config.env_prefix == ""
    assert config.app.settings_config.env_file_encoding == "iso-8859-7"
    assert config.app.settings_config.env_nested_delimiter == ""
    assert config.app.proxy.settings_config.env_prefix == ""
    assert config.app.proxy.settings_config.env_file_encoding == "iso-8859-7"
    assert config.app.proxy.settings_config.env_nested_delimiter == ""


# @pytest.mark.current
@pytest.mark.skip
@pytest.mark.todo
@pytest.mark.env_config
def test_env_include_inherit_parent_todo(cwd_to_tmp):
    # TODO: Implement !!!
    class Proxy(ArFiSettings):
        file_config_inherit_parent = False
        model_config = SettingsConfigDict(
            include_inherit_parent=["env_nested_delimiter"],
            exclude_inherit_parent=[
                "env_include_inherit_parent",
                "env_exclude_inherit_parent",
                "env_file_encoding",
            ],
        )

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()
        model_config = SettingsConfigDict(
            include_inherit_parent=["env_include_inherit_parent"],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix_as_mode_dir=True,
            env_file_encoding="cp1251",
            env_nested_delimiter=".",
            include_inherit_parent=["env_file_encoding"],
        )

    config = AppConfig(
        _env_file_encoding="utf-8",
        app=AppSettings(
            _env_file_encoding="iso-8859-7",
            _env_nested_delimiter="---@---",
        ),
    )
    assert config.settings_config.env_prefix == ""
    assert config.settings_config.env_file_encoding == "utf-8"
    assert config.settings_config.env_nested_delimiter == "."
    assert config.app.settings_config.env_prefix == ""
    assert config.app.settings_config.env_file_encoding == "iso-8859-7"
    assert config.app.settings_config.env_nested_delimiter == "---@---"
    assert config.app.proxy.settings_config.env_prefix == ""
    assert config.app.proxy.settings_config.env_file_encoding is None
    assert config.app.proxy.settings_config.env_nested_delimiter == "---@---"

    class Proxy(ArFiSettings):
        file_config_inherit_parent = False

    class AppSettings(ArFiSettings):
        proxy: Proxy
        model_config = SettingsConfigDict(
            include_inherit_parent=["env_include_inherit_parent"],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix_as_mode_dir=True,
            env_file_encoding="cp1251",
            env_nested_delimiter=".",
            include_inherit_parent=["env_file_encoding"],
        )

    config = AppConfig(
        _env_file_encoding="utf-8",
        app=AppSettings(
            _env_file_encoding="iso-8859-7",
            _env_nested_delimiter="---@---",
            proxy=Proxy(
                _include_inherit_parent=["env_nested_delimiter"],
                _exclude_inherit_parent=[
                    "env_include_inherit_parent",
                    "env_exclude_inherit_parent",
                    "env_file_encoding",
                ],
            ),
        ),
    )
    assert config.settings_config.env_prefix == ""
    assert config.settings_config.env_file_encoding == "utf-8"
    assert config.settings_config.env_nested_delimiter == "."
    assert config.app.settings_config.env_prefix == ""
    assert config.app.settings_config.env_file_encoding == "iso-8859-7"
    assert config.app.settings_config.env_nested_delimiter == "---@---"
    assert config.app.proxy.settings_config.env_prefix == ""
    assert config.app.proxy.settings_config.env_file_encoding is None
    assert config.app.proxy.settings_config.env_nested_delimiter == "---@---"


# @pytest.mark.current
@pytest.mark.env_config
def test_env_exclude_inherit_parent(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix_as_mode_dir=True,
            env_file_encoding="cp1251",
        )

    config = AppConfig()
    assert config.settings_config.env_prefix == ""
    assert config.settings_config.env_file_encoding == "cp1251"
    assert config.app.settings_config.env_prefix == "app_"
    assert config.app.settings_config.env_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.env_prefix == "app_proxy_"
    assert config.app.proxy.settings_config.env_file_encoding == "cp1251"


# @pytest.mark.current
@pytest.mark.env_config
def test_multiple_reverse_inheritance_env_exclude_inherit_parent(cwd_to_tmp):
    class Address(ArFiSettings):
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=[
                "env_exclude_inherit_parent",
                "env_prefix_as_source_mode_dir",
            ],
        )

    class City(ArFiSettings):
        address: Address
        model_config = SettingsConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_nested_delimiter",
                "env_exclude_inherit_parent",
                "env_prefix_as_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        city: City
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=[
                "env_file_encoding",
                "env_exclude_inherit_parent",
            ],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix_as_source_mode_dir=True,
            env_nested_delimiter="---@---",
            env_file_encoding="cp1251",
            env_file=[".env", ".env.prod"],
        )

    config = AppConfig()
    assert config.app.city.address.settings_config.env_prefix == "app_city_address_"
    assert config.app.city.address.settings_config.env_file_encoding is None
    assert config.app.city.address.settings_config.env_nested_delimiter == ""
    assert config.app.city.address.settings_config.env_file == [".env", ".env.prod"]
    # assert config.app.city.address.settings_config.env_exclude_inherit_parent == [
    #     "env_exclude_inherit_parent",
    #     "env_prefix_as_source_mode_dir",
    # ]
    # assert config.app.city.address.settings_config.exclude_inherit_parent == [
    #     "env_exclude_inherit_parent",
    #     "env_prefix_as_source_mode_dir",
    # ]
    assert config.app.city.settings_config.env_prefix == "city_"
    assert config.app.city.settings_config.env_file_encoding is None
    assert config.app.city.settings_config.env_nested_delimiter == ""
    assert config.app.city.settings_config.env_file == [".env", ".env.prod"]
    assert config.app.city.settings_config.env_include_inherit_parent == []
    assert config.app.city.settings_config.env_exclude_inherit_parent == [
        "env_nested_delimiter",
        "env_exclude_inherit_parent",
        "env_prefix_as_mode_dir",
    ]
    assert config.app.city.settings_config.exclude_inherit_parent == [
        "env_nested_delimiter",
        "env_exclude_inherit_parent",
        "env_prefix_as_mode_dir",
    ]
    assert config.app.settings_config.env_prefix == "app_"
    assert config.app.settings_config.env_file_encoding is None
    assert config.app.settings_config.env_nested_delimiter == "---@---"
    assert config.app.settings_config.env_file == [".env", ".env.prod"]
    assert config.settings_config.env_prefix == ""
    assert config.settings_config.env_file_encoding == "cp1251"
    assert config.settings_config.env_nested_delimiter == "---@---"
    assert config.settings_config.env_file == [".env", ".env.prod"]


# @pytest.mark.current
@pytest.mark.env_config
def test_multiple_reverse_inheritance_env_include_inherit_parent(cwd_to_tmp):
    class Address(ArFiSettings):
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=[
                "env_exclude_inherit_parent",
                "env_include_inherit_parent",
            ],
            env_include_inherit_parent=["env_prefix_as_mode_dir", "env_file"],
        )

    class City(ArFiSettings):
        address: Address
        model_config = SettingsConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_nested_delimiter",
                "env_exclude_inherit_parent",
                "env_prefix_as_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        city: City
        model_config = SettingsConfigDict(
            env_exclude_inherit_parent=[
                "env_file_encoding",
                "env_exclude_inherit_parent",
            ],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix_as_source_mode_dir=True,
            env_nested_delimiter="---@---",
            env_file_encoding="cp1251",
            env_file=[".env", ".env.prod"],
        )

    config = AppConfig()
    assert config.app.city.address.settings_config.env_prefix == "app_city_address_"
    assert config.app.city.address.settings_config.env_file_encoding is None
    assert config.app.city.address.settings_config.env_nested_delimiter == ""
    assert config.app.city.address.settings_config.env_file == [".env", ".env.prod"]
    assert config.app.city.address.settings_config.env_exclude_inherit_parent == [
        "env_exclude_inherit_parent",
        "env_include_inherit_parent",
    ]
    assert config.app.city.address.settings_config.exclude_inherit_parent == [
        "env_exclude_inherit_parent",
        "env_include_inherit_parent",
    ]
    assert config.app.city.settings_config.env_prefix == "city_"
    assert config.app.city.settings_config.env_file_encoding is None
    assert config.app.city.settings_config.env_nested_delimiter == ""
    assert config.app.city.settings_config.env_file == [".env", ".env.prod"]
    assert config.app.city.settings_config.env_include_inherit_parent == []
    assert config.app.city.settings_config.env_exclude_inherit_parent == [
        "env_nested_delimiter",
        "env_exclude_inherit_parent",
        "env_prefix_as_mode_dir",
    ]
    assert config.app.city.settings_config.exclude_inherit_parent == [
        "env_nested_delimiter",
        "env_exclude_inherit_parent",
        "env_prefix_as_mode_dir",
    ]
    assert config.app.settings_config.env_prefix == "app_"
    assert config.app.settings_config.env_file_encoding is None
    assert config.app.settings_config.env_nested_delimiter == "---@---"
    assert config.app.settings_config.env_file == [".env", ".env.prod"]
    assert config.settings_config.env_prefix == ""
    assert config.settings_config.env_file_encoding == "cp1251"
    assert config.settings_config.env_nested_delimiter == "---@---"
    assert config.settings_config.env_file == [".env", ".env.prod"]


# @pytest.mark.current
@pytest.mark.env_config
def test_env_include_inherit_parent_exclude_self(cwd_to_tmp):
    class Proxy(ArFiSettings):
        file_config_inherit_parent = False
        model_config = SettingsConfigDict(
            env_prefix="proxy_test_",
            env_exclude_inherit_parent=[
                "env_file_encoding",
                "env_prefix",
            ],
        )

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()
        model_config = SettingsConfigDict(
            env_include_inherit_parent=[
                "env_file_encoding",
            ],
            env_exclude_inherit_parent=[
                "env_include_inherit_parent",
            ],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix="test_",
            env_file_encoding="cp1251",
        )

    config = AppConfig()
    assert config.settings_config.env_prefix == "test_"
    assert config.settings_config.env_file_encoding == "cp1251"
    assert config.app.settings_config.env_prefix == ""
    assert config.app.settings_config.env_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.env_prefix == ""
    assert config.app.proxy.settings_config.env_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.env_include_inherit_parent == []
    assert config.app.proxy.settings_config.env_exclude_inherit_parent == [
        "env_include_inherit_parent",
    ]
    assert config.app.proxy.inherited_params == [
        "env_exclude_inherit_parent",
        "env_file",
        "env_prefix",
        "env_prefix_as_mode_dir",
        "env_prefix_as_nested_mode_dir",
        "env_prefix_as_source_mode_dir",
        "env_file_encoding",
        "env_case_sensitive",
        "env_nested_delimiter",
        "env_ignore_missing",
    ]

    class Proxy(ArFiSettings):
        file_config_inherit_parent = False
        model_config = SettingsConfigDict(
            env_prefix="proxy_test_",
            env_exclude_inherit_parent=[
                "env_exclude_inherit_parent",
                "env_file_encoding",
                "env_prefix",
            ],
        )

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()
        model_config = SettingsConfigDict(
            env_include_inherit_parent=[
                "env_file_encoding",
            ],
            env_exclude_inherit_parent=[
                "env_include_inherit_parent",
            ],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            env_prefix="test_",
            env_file_encoding="cp1251",
        )

    config = AppConfig()
    assert config.settings_config.env_prefix == "test_"
    assert config.settings_config.env_file_encoding == "cp1251"
    assert config.app.settings_config.env_prefix == ""
    assert config.app.settings_config.env_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.env_prefix == "proxy_test_"
    assert config.app.proxy.settings_config.env_file_encoding is None
    assert config.app.proxy.settings_config.env_include_inherit_parent == []
    assert config.app.proxy.settings_config.env_exclude_inherit_parent == [
        "env_exclude_inherit_parent",
        "env_file_encoding",
        "env_prefix",
    ]
    assert config.app.proxy.inherited_params == [
        "env_include_inherit_parent",
        "env_file",
        "env_prefix_as_mode_dir",
        "env_prefix_as_nested_mode_dir",
        "env_prefix_as_source_mode_dir",
        "env_case_sensitive",
        "env_nested_delimiter",
        "env_ignore_missing",
    ]


# @pytest.mark.current
@pytest.mark.env_config
def test_env_prefix_as_mode_dir(cwd_to_tmp):
    class Nested(ArFiSettings):
        mode_dir = "nested"

    class Child(Nested):
        mode_dir = "child"

        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_prefix_as_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        child: Child

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings

    config = AppConfig()
    assert config.app.mode_dir == "app"
    assert config.app.computed_mode_dir == "dev/app"
    assert config.app.child.mode_dir == "nested/child"
    assert config.app.child.computed_mode_dir == "dev/app/nested/child"
    assert config.app.child.settings_config.env_prefix == "dev_app_nested_child_"

    class Child(Nested):
        mode_dir = "child"

        env_config = EnvConfigDict(
            env_prefix_as_nested_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_prefix_as_nested_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        child: Child
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings

    config = AppConfig()
    assert config.app.child.settings_config.env_prefix == "nested_child_"

    class Child(Nested):
        mode_dir = "child"

        env_config = EnvConfigDict(
            env_prefix_as_source_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_prefix_as_source_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        child: Child
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings

    config = AppConfig()
    assert config.app.child.settings_config.env_prefix == "child_"

    class Child(Nested):
        mode_dir = "child"

        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_exclude_inherit_parent",
                "env_prefix_as_mode_dir",
                "env_prefix_as_nested_mode_dir",
                "env_prefix_as_source_mode_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        child: Child
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
            env_exclude_inherit_parent=[
                "env_prefix_as_mode_dir",
                "env_prefix_as_source_mode_dir",
            ],
        )

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings
        env_config = EnvConfigDict(
            env_prefix_as_source_mode_dir=True,
        )

    config = AppConfig()
    assert config.settings_config.env_prefix == "dev_"
    assert config.app.settings_config.env_prefix == "dev_app_"
    assert config.app.child.settings_config.env_prefix == "dev_app_nested_child_"

    class Child(Nested):
        mode_dir = "child"

    class AppSettings(ArFiSettings):
        child: Child

    class AppConfig(ArFiSettings):
        mode_dir = "dev"
        app: AppSettings
        env_config = EnvConfigDict(
            env_prefix_as_mode_dir=True,
        )

    config = AppConfig()
    assert config.settings_config.env_prefix == "dev_"
    assert config.app.settings_config.env_prefix == "dev_app_"
    assert config.app.child.settings_config.env_prefix == "dev_app_nested_child_"


# @pytest.mark.current
@pytest.mark.env_config
@pytest.mark.parametrize("file_env", ["", None])
def test_env_config_disable_env_file(file_env):
    class AppConfig(ArFiSettings):
        env_config = EnvConfigDict(
            env_file=file_env,
        )

    config = AppConfig()
    assert config.computed_env_config["env_file"] == file_env
    assert config.env_path == []
    assert config.settings_config.env_file == file_env
    assert config.settings_config.env_path == []
