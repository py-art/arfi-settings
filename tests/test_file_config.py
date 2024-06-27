from pathlib import Path

import pydantic
import pytest

from arfi_settings import ArFiSettings, FileConfigDict, SettingsConfigDict
from arfi_settings.errors import ArFiSettingsError


@pytest.mark.file_config
def test_default_value_file_config():
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig()
    assert config.computed_file_config["conf_file"] == "config"
    assert config.computed_file_config["conf_dir"] == "config"
    assert config.computed_file_config["conf_ext"] == ["toml", "yaml", "yml", "json"]
    assert config.computed_file_config["conf_file_encoding"] is None
    assert config.computed_file_config["conf_case_sensitive"] is False
    assert config.computed_file_config["conf_ignore_missing"] is True
    assert config.computed_file_config["conf_custom_ext_handler"] is None


# @pytest.mark.current
@pytest.mark.file_config
@pytest.mark.parametrize("config_file", ["", None])
def test_conf_file_disable_conf_file(config_file):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_file=config_file,
        )

    config = AppConfig()
    assert config.computed_file_config["conf_file"] == config_file
    assert config.conf_path == []


# @pytest.mark.current
@pytest.mark.file_config
@pytest.mark.parametrize("config_dir", ["", None])
def test_conf_file_disable_conf_dir(config_dir):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_dir=config_dir,
        )

    config = AppConfig()
    assert config.computed_file_config["conf_dir"] == config_dir
    assert config.conf_path == [Path("config")]


# @pytest.mark.current
@pytest.mark.file_config
def test_conf_file_file_config():
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_file="test_data/config.yaml",
        )

    config = AppConfig()
    assert config.computed_file_config["conf_file"] == "test_data/config.yaml"
    assert config.conf_path == [Path("config/test_data/config.yaml")]


@pytest.mark.file_config
@pytest.mark.parametrize(
    "test_conf_dir, result_conf_path",
    [
        ("test_data", [Path("test_data/config")]),
        ("test_data/", [Path("test_data/config")]),
        ("/test_data/", [Path("/test_data/config")]),
        (("test_data"), [Path("test_data/config")]),
        (
            ["test_data", "/opt/myapp"],
            [
                Path("test_data/config"),
                Path("/opt/myapp/config"),
            ],
        ),
    ],
)
def test_conf_dir_file_config(test_conf_dir, result_conf_path):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_dir=test_conf_dir,
        )

    config = AppConfig()
    assert config.computed_file_config["conf_dir"] == test_conf_dir
    assert config.conf_path == result_conf_path


@pytest.mark.file_config
@pytest.mark.parametrize(
    "ext, result_ext",
    [
        ("json", ["json"]),
        ("toml,conf", ["toml", "conf"]),
        (["yaml", "yml"], ["yaml", "yml"]),
    ],
)
def test_conf_ext_file_config(ext, result_ext):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_ext=ext,
        )

    config = AppConfig()
    assert config.computed_file_config["conf_ext"] == result_ext


# @pytest.mark.current
@pytest.mark.file_config
def test_non_conf_ext_file_config():
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_ext="",
            # conf_ext=[""],
            conf_custom_ext_handler="toml",
        )

    config = AppConfig()
    assert config.computed_file_config["conf_ext"] == [""]

    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig(ArFiSettings):
            file_config = FileConfigDict(
                conf_ext="",
            )

        _ = AppConfig()

    assert "`conf_custom_ext_handler` must be defined" in str(excinfo.value)


@pytest.mark.file_config
@pytest.mark.parametrize("f_encoding", [None, "utf-8"])
def test_conf_file_encoding_file_config(f_encoding):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_file_encoding=f_encoding,
        )

    config = AppConfig()
    assert config.computed_file_config["conf_file_encoding"] == f_encoding


@pytest.mark.file_config
def test_conf_case_sensitive_file_config():
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_case_sensitive=True,
        )

    config = AppConfig()
    assert config.computed_file_config["conf_case_sensitive"] is True


@pytest.mark.file_config
def test_conf_ignore_missing_file_config():
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_file="",
            conf_ignore_missing=False,
        )

    config = AppConfig()
    assert config.computed_file_config["conf_ignore_missing"] is False


# @pytest.mark.current
@pytest.mark.file_config
def test_not_exist_conf_custom_ext_handler_file_config():
    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig(ArFiSettings):
            file_config = FileConfigDict(
                conf_ext="",
                conf_custom_ext_handler="aslkdjflkj",
            )

        _ = AppConfig()
    assert "is not defined" in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.file_config
@pytest.mark.parametrize(
    "test_conf_ext, custom_handler",
    [
        ("", "toml"),
        ("", ".toml"),
        ("", "toml_ext_handler"),
        ("", {"": "toml"}),
        ("", {"": "toml_ext_handler"}),
        (["", "toml"], {"": "toml"}),
        (["", "toml"], {"": ".toml"}),
    ],
)
def test_conf_custom_ext_handler_file_config(test_conf_ext, custom_handler):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_ext=test_conf_ext,
            conf_custom_ext_handler=custom_handler,
        )

    config = AppConfig()
    assert config.computed_file_config["conf_custom_ext_handler"] == custom_handler


# @pytest.mark.current
@pytest.mark.xfail
@pytest.mark.file_config
@pytest.mark.parametrize(
    "test_conf_ext, custom_handler",
    [
        (None, "toml"),
        (None, ".toml"),
        (None, "toml_ext_handler"),
        (None, {None: "toml"}),
        (None, {None: "toml_ext_handler"}),
        ([None, "toml"], {None: "toml"}),
        ([None, "toml"], {None: ".toml"}),
    ],
)
def test_fail_conf_custom_ext_handler_file_config(test_conf_ext, custom_handler):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_ext=test_conf_ext,
            conf_custom_ext_handler=custom_handler,
        )

    config = AppConfig()
    assert config.computed_file_config["conf_custom_ext_handler"] == custom_handler


# @pytest.mark.current
@pytest.mark.file_config
def test_class_conf_exclude_inherit_parent_valid_input(
    cwd_to_tmp,
    conf_include_exclude_expected,
    conf_include_exclude_msg,
):
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig()
    assert config.settings_config.conf_exclude_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class A(ArFiSettings):
            file_config = FileConfigDict(
                conf_exclude_inherit_parent=True,
            )

        A()

    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": (
                "file_config",
                "conf_exclude_inherit_parent",
            ),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_exclude_inherit_parent=[],
        )

    config = AppConfig()
    assert config.settings_config.conf_exclude_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class B(ArFiSettings):
            file_config = FileConfigDict(
                conf_exclude_inherit_parent=["test"],
            )

        B()

    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "literal_error",
            "loc": (
                "conf_exclude_inherit_parent",
                0,
            ),
            "ctx": {
                "expected": conf_include_exclude_expected,
            },
            "msg": conf_include_exclude_msg,
            "input": "test",
        },
    ]


# @pytest.mark.current
@pytest.mark.file_config
def test_class_conf_exclude_inherit_parent(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_dir"],
        )

    config = AppConfig()
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
            exclude_inherit_parent=["conf_dir"],
        )

    config = AppConfig()
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_exclude_inherit_parent"],
            exclude_inherit_parent=["conf_dir"],
        )

    config = AppConfig()
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]


# @pytest.mark.current
@pytest.mark.file_config
def test_only_init_conf_exclude_inherit_parent_valid_input(
    cwd_to_tmp,
    conf_include_exclude_expected,
    conf_include_exclude_msg,
):
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig(
        _conf_exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_exclude_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    config = AppConfig(
        _exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_exclude_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:
        AppConfig(
            _conf_exclude_inherit_parent=True,
        )
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": ("_conf_exclude_inherit_parent",),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    with pytest.raises(pydantic.ValidationError) as excinfo:
        AppConfig(
            _conf_exclude_inherit_parent=["test"],
        )
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "literal_error",
            "loc": (
                "_conf_exclude_inherit_parent",
                0,
            ),
            "ctx": {
                "expected": conf_include_exclude_expected,
            },
            "msg": conf_include_exclude_msg,
            "input": "test",
        },
    ]

    config = AppConfig(
        _conf_exclude_inherit_parent=["conf_file"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _exclude_inherit_parent=["conf_file"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _conf_exclude_inherit_parent=["conf_file"],
        _exclude_inherit_parent=["conf_dir"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]


# @pytest.mark.current
@pytest.mark.file_config
def test_init_and_class_conf_exclude_inherit_parent_valid_input(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _conf_exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _conf_exclude_inherit_parent=["conf_ignore_missing"],
        _exclude_inherit_parent=["conf_dir"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _conf_exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_dir"],
        )

    config = AppConfig(
        _conf_exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _conf_exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
            exclude_inherit_parent=["conf_dir"],
        )

    config = AppConfig(
        _conf_exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_exclude_inherit_parent"],
            exclude_inherit_parent=["conf_dir"],
        )

    config = AppConfig(
        _conf_exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]


# @pytest.mark.current
@pytest.mark.file_config
def test_class_conf_include_inherit_parent_valid_input(
    cwd_to_tmp,
    conf_include_exclude_expected,
    conf_include_exclude_msg,
):
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class A(ArFiSettings):
            file_config = FileConfigDict(
                conf_include_inherit_parent=True,
            )

        A()

    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": (
                "file_config",
                "conf_include_inherit_parent",
            ),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=[],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class B(ArFiSettings):
            file_config = FileConfigDict(
                conf_include_inherit_parent=["test"],
            )

        B()

    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "literal_error",
            "loc": (
                "conf_include_inherit_parent",
                0,
            ),
            "ctx": {
                "expected": conf_include_exclude_expected,
            },
            "msg": conf_include_exclude_msg,
            "input": "test",
        },
    ]

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class C(ArFiSettings):
            model_config = SettingsConfigDict(
                conf_include_inherit_parent=True,
            )

        C()

    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": ("conf_include_inherit_parent",),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    with pytest.raises(pydantic.ValidationError) as excinfo:

        class D(ArFiSettings):
            model_config = SettingsConfigDict(
                include_inherit_parent=True,
            )

        D()

    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": ("include_inherit_parent",),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]


# @pytest.mark.current
@pytest.mark.file_config
def test_class_conf_include_inherit_parent(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_dir"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            include_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file"],
            include_inherit_parent=["conf_dir"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_exclude_inherit_parent"],
            include_inherit_parent=["conf_dir"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]


# @pytest.mark.current
@pytest.mark.file_config
def test_only_init_conf_include_inherit_parent_valid_input(
    cwd_to_tmp,
    conf_include_exclude_expected,
    conf_include_exclude_msg,
):
    class AppConfig(ArFiSettings):
        pass

    config = AppConfig(
        _conf_include_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []

    config = AppConfig(
        _include_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []

    with pytest.raises(pydantic.ValidationError) as excinfo:
        AppConfig(
            _conf_include_inherit_parent=True,
        )
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "list_type",
            "loc": ("_conf_include_inherit_parent",),
            "msg": "Input should be a valid list",
            "input": True,
        },
    ]

    with pytest.raises(pydantic.ValidationError) as excinfo:
        AppConfig(
            _conf_include_inherit_parent=["test"],
        )
    assert excinfo.value.errors(include_url=False) == [
        {
            "type": "literal_error",
            "loc": (
                "_conf_include_inherit_parent",
                0,
            ),
            "ctx": {
                "expected": conf_include_exclude_expected,
            },
            "msg": conf_include_exclude_msg,
            "input": "test",
        },
    ]

    config = AppConfig(
        _conf_include_inherit_parent=["conf_file"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]

    config = AppConfig(
        _conf_include_inherit_parent=["conf_file"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]

    config = AppConfig(
        _conf_include_inherit_parent=["conf_file"],
        _include_inherit_parent=["conf_dir"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]


# @pytest.mark.current
@pytest.mark.file_config
def test_init_and_class_conf_include_inherit_parent_valid_input(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
        _include_inherit_parent=["conf_dir"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_dir"],
        )

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            include_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file"],
            include_inherit_parent=["conf_dir"],
        )

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_exclude_inherit_parent"],
            include_inherit_parent=["conf_dir"],
        )

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]


# @pytest.mark.current
@pytest.mark.file_config
def test_combination_conf_include_exclude_parent(cwd_to_tmp):
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file"],
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file"],
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            include_inherit_parent=["conf_file"],
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=[],
        )
        model_config = SettingsConfigDict(
            include_inherit_parent=["conf_file"],
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file", "conf_ignore_missing"],
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file", "conf_ignore_missing"],
        )
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file", "conf_ignore_missing"],
        )
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file", "conf_ignore_missing"],
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file", "conf_ignore_missing"],
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            include_inherit_parent=["conf_file", "conf_ignore_missing"],
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig()
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]


# @pytest.mark.current
@pytest.mark.file_config
def test_combination_init_and_class_conf_include_exclude_parent(cwd_to_tmp):
    # 0
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _conf_include_inherit_parent=["conf_file"],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _conf_include_inherit_parent=["conf_file"],
        _conf_exclude_inherit_parent=["conf_file"],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _conf_include_inherit_parent=["conf_file"],
        _exclude_inherit_parent=["conf_file"],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _conf_exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == []

    config = AppConfig(
        _exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
        _conf_exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == []

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
        _exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["conf_file"],
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]

    config = AppConfig(
        _include_inherit_parent=["conf_file"],
        _exclude_inherit_parent=["conf_ignore_missing", "conf_file"],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing", "conf_file"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing", "conf_file"]

    # 1
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
        _conf_exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == []

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
        _exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    # 2
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file"],
        )
        model_config = SettingsConfigDict(
            exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_file"]
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == ["conf_file"]

    config = AppConfig(
        _conf_include_inherit_parent=["conf_ignore_missing"],
        _conf_exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == []

    # 3
    class AppConfig(ArFiSettings):
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file"],
            conf_exclude_inherit_parent=["conf_file"],
        )

    config = AppConfig(
        _include_inherit_parent=["conf_ignore_missing"],
        _conf_exclude_inherit_parent=[],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.conf_exclude_inherit_parent == []
    assert config.settings_config.include_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.exclude_inherit_parent == []

    # 4
    class AppConfig(ArFiSettings):
        file_config = FileConfigDict(
            conf_include_inherit_parent=["conf_file", "conf_ignore_missing"],
            conf_exclude_inherit_parent=["conf_case_sensitive"],
        )

    config = AppConfig(
        _include_inherit_parent=["conf_case_sensitive"],
    )
    assert config.settings_config.conf_include_inherit_parent == []
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_case_sensitive"]
    assert config.settings_config.include_inherit_parent == []
    assert config.settings_config.exclude_inherit_parent == ["conf_case_sensitive"]

    config = AppConfig(
        _exclude_inherit_parent=["conf_ignore_missing"],
    )
    assert config.settings_config.conf_include_inherit_parent == ["conf_file"]
    assert config.settings_config.conf_exclude_inherit_parent == ["conf_ignore_missing"]
    assert config.settings_config.include_inherit_parent == ["conf_file"]
    assert config.settings_config.exclude_inherit_parent == ["conf_ignore_missing"]


# @pytest.mark.current
@pytest.mark.file_config
def test_conf_include_inherit_parent(cwd_to_tmp):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            conf_dir="test",
            conf_file_encoding="cp1251",
        )

    config = AppConfig()
    assert config.settings_config.conf_dir == "test"
    assert config.settings_config.conf_file_encoding == "cp1251"
    assert config.app.settings_config.conf_dir == "test"
    assert config.app.settings_config.conf_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.conf_dir == "test"
    assert config.app.proxy.settings_config.conf_file_encoding == "cp1251"

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=["conf_file_encoding"],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            conf_dir="test",
            conf_file_encoding="cp1251",
        )

    config = AppConfig()
    assert config.settings_config.conf_dir == "test"
    assert config.settings_config.conf_file_encoding == "cp1251"
    assert config.app.settings_config.conf_dir == "config"
    assert config.app.settings_config.conf_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.conf_dir == "config"
    assert config.app.proxy.settings_config.conf_file_encoding == "cp1251"


# @pytest.mark.current
@pytest.mark.file_config
def test_conf_include_inherit_parent_exclude_self(cwd_to_tmp):
    class Proxy(ArFiSettings):
        env_config_inherit_parent = False
        model_config = SettingsConfigDict(
            conf_dir="proxy_dir",
            conf_exclude_inherit_parent=[
                "conf_file_encoding",
                "conf_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=[
                "conf_file_encoding",
            ],
            conf_exclude_inherit_parent=[
                "conf_include_inherit_parent",
            ],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            conf_dir="test",
            conf_file_encoding="cp1251",
        )

    config = AppConfig()
    assert config.settings_config.conf_dir == "test"
    assert config.settings_config.conf_file_encoding == "cp1251"
    assert config.app.settings_config.conf_dir == "config"
    assert config.app.settings_config.conf_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.conf_dir == "config"
    assert config.app.proxy.settings_config.conf_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.conf_include_inherit_parent == []
    assert config.app.proxy.settings_config.conf_exclude_inherit_parent == [
        "conf_include_inherit_parent",
    ]
    assert config.app.proxy.inherited_params == [
        "conf_exclude_inherit_parent",
        "conf_file",
        "conf_dir",
        "conf_ext",
        "conf_file_encoding",
        "conf_case_sensitive",
        "conf_ignore_missing",
        "conf_custom_ext_handler",
    ]

    class Proxy(ArFiSettings):
        env_config_inherit_parent = False
        model_config = SettingsConfigDict(
            conf_dir="proxy_dir",
            conf_exclude_inherit_parent=[
                "conf_exclude_inherit_parent",
                "conf_file_encoding",
                "conf_dir",
            ],
        )

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()
        model_config = SettingsConfigDict(
            conf_include_inherit_parent=[
                "conf_file_encoding",
            ],
            conf_exclude_inherit_parent=[
                "conf_include_inherit_parent",
            ],
        )

    class AppConfig(ArFiSettings):
        app: AppSettings
        model_config = SettingsConfigDict(
            conf_dir="test",
            conf_file_encoding="cp1251",
        )

    config = AppConfig()
    assert config.settings_config.conf_dir == "test"
    assert config.settings_config.conf_file_encoding == "cp1251"
    assert config.app.settings_config.conf_dir == "config"
    assert config.app.settings_config.conf_file_encoding == "cp1251"
    assert config.app.proxy.settings_config.conf_dir == "proxy_dir"
    assert config.app.proxy.settings_config.conf_file_encoding is None
    assert config.app.proxy.settings_config.conf_include_inherit_parent == []
    assert config.app.proxy.settings_config.conf_exclude_inherit_parent == [
        "conf_exclude_inherit_parent",
        "conf_file_encoding",
        "conf_dir",
    ]
    assert config.app.proxy.inherited_params == [
        "conf_include_inherit_parent",
        "conf_file",
        "conf_ext",
        "conf_case_sensitive",
        "conf_ignore_missing",
        "conf_custom_ext_handler",
    ]


"""










"""
###
