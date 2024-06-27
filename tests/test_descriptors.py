import pydantic
import pytest
from pydantic import StrictBool, validate_call

from arfi_settings import ArFiSettings
from arfi_settings.descriptors import (
    ABCDescriptor,
    EnvConfigInheritParentDescriptor,
    FileConfigInheritParentDescriptor,
    ModeDirDescriptor,
    ModeDirInheritNestedDescriptor,
    ModeDirInheritParentDescriptor,
    ReadConfigDeskriptor,
    ReadConfigForceDeskriptor,
)
from arfi_settings.errors import ArFiSettingsError
from arfi_settings.types import DEFAULT_PATH_SENTINEL, SENTINEL


@pytest.mark.descriptors
def test_new_valid_descriptor():
    class NewDescriptor(ABCDescriptor):
        name: str = "attr_name"
        default: bool = True

        @staticmethod
        @validate_call
        def validate(value: StrictBool):
            return value

    new_descriptor = NewDescriptor()
    assert new_descriptor.name == "attr_name"
    assert new_descriptor.default is True
    with pytest.raises(ArFiSettingsError) as excinfo:
        _ = new_descriptor.inherited_value
    assert "Can not define `inherited_value` without owner" in str(excinfo.value)


@pytest.mark.descriptors
def test_new_descriptors_without_validate_method():
    with pytest.raises(TypeError):

        class NewDescriptor(ABCDescriptor):
            name: str = "attr_name"
            default: bool = True

        new_descriptor = NewDescriptor()
        assert new_descriptor.name == "test_name"


@pytest.mark.descriptors
@pytest.mark.parametrize(
    "attr_name, default_value, error_message",
    [
        (SENTINEL, True, "Missing or empty `name` attribut"),
        ("test_name", SENTINEL, "Missing `default` attribut"),
        (None, True, "attribut `name` must be not empty string"),
        ("", True, "attribut `name` must be not empty string"),
    ],
)
def test_new_descriptor_name_and_default_value(attr_name, default_value, error_message):
    with pytest.raises(ArFiSettingsError) as excinfo:

        class NewDescriptor(ABCDescriptor):
            name: str = attr_name
            default: bool = default_value

            @staticmethod
            @validate_call
            def validate(value: StrictBool):
                return value

    assert error_message in str(excinfo.value)


@pytest.mark.descriptors
def test_validate_init_default_value_descriptor():
    class NewDescriptor(ABCDescriptor):
        name: str = "attr_name"
        default: bool = True

        @staticmethod
        @validate_call
        def validate(value: StrictBool):
            return value

    new_descriptor = NewDescriptor(True)
    assert new_descriptor.default is True
    with pytest.raises(pydantic.ValidationError):
        new_descriptor = NewDescriptor(1)
        assert new_descriptor.default is True


@pytest.mark.descriptors
def test_read_config_descriptor():
    read_config = ReadConfigDeskriptor()
    assert read_config.name == "read_config"
    assert read_config.default is True

    class AppConfig:
        read_config = ReadConfigDeskriptor(False)

    config = AppConfig()
    assert not config.read_config


@pytest.mark.descriptors
def test_read_config_force_descriptor():
    read_config_force = ReadConfigForceDeskriptor()
    assert read_config_force.name == "read_config_force"
    assert read_config_force.default is None

    class AppConfig:
        read_config_force = ReadConfigDeskriptor(True)

    config = AppConfig()
    assert config.read_config_force is True

    class AppConfig:
        read_config_force = ReadConfigDeskriptor(False)

    config = AppConfig()
    assert config.read_config_force is False


@pytest.mark.descriptors
def test_mode_dir_inherit_nested_descriptor():
    mode_dir_inherit_nested = ModeDirInheritNestedDescriptor()
    assert mode_dir_inherit_nested.name == "mode_dir_inherit_nested"
    assert mode_dir_inherit_nested.default is True

    class AppConfig:
        _mode_dir_inherit_nested = True
        mode_dir_inherit_nested = ModeDirInheritNestedDescriptor(False)

    config = AppConfig()
    assert config.mode_dir_inherit_nested


@pytest.mark.descriptors
def test_mode_dir_inherit_parent_descriptor():
    mode_dir_inherit_parent = ModeDirInheritParentDescriptor()
    assert mode_dir_inherit_parent.name == "mode_dir_inherit_parent"
    assert mode_dir_inherit_parent.default is True

    class AppConfig:
        _mode_dir_inherit_parent = True
        mode_dir_inherit_parent = ModeDirInheritParentDescriptor(False)

    config = AppConfig()
    assert config.mode_dir_inherit_parent


@pytest.mark.descriptors
def test_file_config_inherit_parent_descriptor():
    file_config_inherit_parent = FileConfigInheritParentDescriptor()
    assert file_config_inherit_parent.name == "file_config_inherit_parent"
    assert file_config_inherit_parent.default is True

    class AppConfig:
        _file_config_inherit_parent = True
        file_config_inherit_parent = FileConfigInheritParentDescriptor(False)

    config = AppConfig()
    assert config.file_config_inherit_parent


@pytest.mark.descriptors
def test_env_config_inherit_parent_descriptor():
    env_config_inherit_parent = EnvConfigInheritParentDescriptor()
    assert env_config_inherit_parent.name == "env_config_inherit_parent"
    assert env_config_inherit_parent.default is True

    class AppConfig:
        _env_config_inherit_parent = True
        env_config_inherit_parent = EnvConfigInheritParentDescriptor(False)

    config = AppConfig()
    assert config.env_config_inherit_parent


@pytest.mark.descriptors
def test_mode_dir_descriptor():
    mode_dir = ModeDirDescriptor()
    assert mode_dir.name == "mode_dir"
    assert mode_dir.default is DEFAULT_PATH_SENTINEL

    class AppConfig:
        mode_dir_inherit_nested = True
        mode_dir = ModeDirDescriptor()

    config = AppConfig()
    assert config.mode_dir == DEFAULT_PATH_SENTINEL

    class AppConfig:
        mode_dir_inherit_nested = True
        _mode_dir = "test"
        mode_dir = ModeDirDescriptor()

    config = AppConfig()
    assert config.mode_dir == "test"


@pytest.mark.descriptors
@pytest.mark.parametrize(
    "self_mode_dir, parent_class_attr, result_mode_dir",
    [
        ("test", {}, "test"),
        ("test", {"mode_dir": "parent"}, "parent/test"),
        (DEFAULT_PATH_SENTINEL, {"mode_dir": "parent"}, "parent"),
        (None, {"mode_dir": "parent"}, "parent"),
        ("test", {"mode_dir": DEFAULT_PATH_SENTINEL}, "test"),
        ("test", {"mode_dir": SENTINEL}, "test"),
    ],
)
def test_parent_mode_dir_descriptor(self_mode_dir, parent_class_attr, result_mode_dir):
    Parent = type("Parent", (), parent_class_attr)

    class AppConfig(Parent):
        mode_dir_inherit_nested = True
        mode_dir = ModeDirDescriptor(self_mode_dir)

    config = AppConfig()
    assert config.mode_dir == result_mode_dir


@pytest.mark.descriptors
def test_mode_dir_missing_attr_descriptor():
    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig:
            mode_dir = ModeDirDescriptor()

        config = AppConfig()
        assert config.mode_dir == DEFAULT_PATH_SENTINEL
    assert "missing required attribute `mode_dir_inherit_nested`" in str(excinfo.value)


@pytest.mark.descriptors
@pytest.mark.parametrize(
    "wrong_mode_dir, error_message",
    [
        (".", "`mode_dir` can't startswith `.`"),
        ("/config", "`mode_dir` can't startswith `/`"),
        ("config/", "mode_dir` can't endswith `/`"),
    ],
)
def test_wrong_mode_dir_descriptor(wrong_mode_dir, error_message):
    with pytest.raises(ArFiSettingsError) as excinfo:

        class AppConfig:
            mode_dir_inherit_nested = True
            mode_dir = ModeDirDescriptor(wrong_mode_dir)

        config = AppConfig()
        assert config.mode_dir == wrong_mode_dir

    assert error_message in str(excinfo.value)


@pytest.mark.descriptors
def test_abc_descriptor():
    from typing import Any

    class NewDescriptor(ABCDescriptor):
        name = "test"
        default = 1

        @staticmethod
        def validate(value: Any):
            return value

    new_decriptor = NewDescriptor()
    assert new_decriptor.__get__("abstract_instance") == new_decriptor
    assert new_decriptor.validate("Any") == "Any"


@pytest.mark.descriptors
@pytest.mark.parametrize(
    """
    _read_config,
    _mode_dir_inherit_nested,
    _mode_dir_inherit_parent,
    _file_config_inherit_parent,
    _env_config_inherit_parent
    """,
    [
        ("True", True, True, True, True),
        (True, "True", True, True, True),
        (True, True, "True", True, True),
        (True, True, True, "True", True),
        (True, True, True, True, "True"),
    ],
)
def test_not_bool_value_descriptor(
    _read_config,
    _mode_dir_inherit_nested,
    _mode_dir_inherit_parent,
    _file_config_inherit_parent,
    _env_config_inherit_parent,
):
    class Proxy(ArFiSettings):
        pass

    class AppSettings(ArFiSettings):
        proxy: Proxy = Proxy()

    with pytest.raises(pydantic.ValidationError):

        class AppConfig(ArFiSettings):
            read_config = _read_config
            mode_dir_inherit_nested = _mode_dir_inherit_nested
            mode_dir_inherit_parent = _mode_dir_inherit_parent
            file_config_inherit_parent = _file_config_inherit_parent
            env_config_inherit_parent = _env_config_inherit_parent
            app: AppSettings = AppSettings()


###
