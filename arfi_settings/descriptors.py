from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pydantic import StrictBool, validate_call

from .errors import ArFiSettingsError
from .types import (
    DEFAULT_PATH_SENTINEL,
    LIST_STR_SENTINEL,
    SENTINEL,
    PathType,
)

__all__ = [
    "ABCDescriptor",
    "BaseDirDescriptor",
    "ReadConfigDeskriptor",
    "ReadConfigForceDeskriptor",
    "ReadPyProjectTomlDeskriptor",
    "ModeDirDescriptor",
    "ModeDirInheritNestedDescriptor",
    "ModeDirInheritParentDescriptor",
    "FileConfigInheritParentDescriptor",
    "EnvConfigInheritParentDescriptor",
    "HandlerDescriptor",
    "HandlerInheritParentDescriptor",
    "OrderedSettingsDescriptor",
    "OrderedSettingsInheritParentDescriptor",
]


class ABCDescriptor(ABC):
    """Abstract non-data descriptor."""

    name: str = SENTINEL
    default: Any = SENTINEL

    def __init__(self, default: Any = SENTINEL):
        if default is not SENTINEL:
            self.default = self.validate(default)
        self.private_name = f"_{self.name}"
        self.owner = None
        self._inherited_value = SENTINEL

    def __init_subclass__(cls):
        super().__init_subclass__()
        # skip base class
        if cls.__name__.startswith("Base"):
            return
        try:
            assert cls.name is not SENTINEL, f"Missing or empty `name` attribut in {cls.__name__}"
            assert cls.name and isinstance(
                cls.name, str
            ), f"attribut `name` must be not empty string in class {cls.__name__}"
            assert cls.default is not SENTINEL, f"Missing `default` attribut in class {cls.__name__}"
        except AssertionError as e:
            raise ArFiSettingsError(e) from e

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"
        self.owner = owner

    def __get__(self, instance, owner=None):
        if owner is None:
            return self
        self.owner = owner
        return self.computed_attr(instance, owner)

    @property
    def inherited_value(self) -> Any:
        """Value from parent."""
        if self._inherited_value is SENTINEL:
            try:
                assert self.owner, "Can not define `inherited_value` without owner"
            except AssertionError as e:
                raise ArFiSettingsError(e) from e
            for base in self.owner.__bases__:
                if hasattr(base, self.name):
                    self._inherited_value = getattr(base, self.name)
                    break
        return self._inherited_value

    @staticmethod
    @abstractmethod
    def validate(value: Any) -> Any:
        """Validate init value."""

    def computed_attr(self, instance, owner):
        if instance is not None:
            return getattr(instance, self.private_name, self.default)
        return getattr(owner, self.private_name, self.default)


class BaseStrictBoolDescriptor(ABCDescriptor):
    """Base strict bool descriptor."""

    @staticmethod
    @validate_call
    def validate(value: StrictBool):
        return value


class ReadConfigDeskriptor(BaseStrictBoolDescriptor):
    """Read config descriptor."""

    name: str = "read_config"
    default: bool = True


class ReadConfigForceDeskriptor(ABCDescriptor):
    """Force read config descriptor."""

    name: str = "read_config_force"
    default: bool | None = None

    @staticmethod
    @validate_call
    def validate(value: StrictBool | None):
        return value


class ReadPyProjectTomlDeskriptor(BaseStrictBoolDescriptor):
    """Read pyproject.toml descriptor."""

    name: str = "read_pyproject_toml"
    default: bool = True


class ModeDirInheritNestedDescriptor(BaseStrictBoolDescriptor):
    """Mode directory nested descriptor."""

    name: str = "mode_dir_inherit_nested"
    default: bool = True


class ModeDirInheritParentDescriptor(BaseStrictBoolDescriptor):
    """Mode directory parent descriptor."""

    name: str = "mode_dir_inherit_parent"
    default: bool = True


class FileConfigInheritParentDescriptor(BaseStrictBoolDescriptor):
    """Inherit parent file_config descriptor."""

    name: str = "file_config_inherit_parent"
    default: bool = True


class EnvConfigInheritParentDescriptor(BaseStrictBoolDescriptor):
    """Inherit parent env_config descriptor."""

    name: str = "env_config_inherit_parent"
    default: bool = True


class HandlerInheritParentDescriptor(BaseStrictBoolDescriptor):
    """Inherit parent handler descriptor."""

    name: str = "handler_inherit_parent"
    default: bool = True


class OrderedSettingsInheritParentDescriptor(BaseStrictBoolDescriptor):
    """Inherit parent ordered_settings descriptor."""

    name: str = "ordered_settings_inherit_parent"
    default: bool = True


class OrderedSettingsDescriptor(ABCDescriptor):
    name: str = "ordered_settings"
    default: list[str] = LIST_STR_SENTINEL

    @staticmethod
    @validate_call
    def validate(value: list[str]):
        return value


class HandlerDescriptor(ABCDescriptor):
    """Inherit parent handler descriptor."""

    name: str = "handler"
    default: str = "default_main_handler"

    @staticmethod
    @validate_call
    def validate(value: str):
        return value


class BaseDirDescriptor(ABCDescriptor):
    """Base dir descriptor."""

    name: str = "base_dir"
    default: PathType | None = None

    @staticmethod
    @validate_call
    def validate(value: PathType | None):
        if isinstance(value, str):
            value = Path(value)
        return value


class ModeDirDescriptor(ABCDescriptor):
    """Mode directory descriptor."""

    name: str = "mode_dir"
    default: PathType | None = DEFAULT_PATH_SENTINEL

    @staticmethod
    @validate_call
    def validate(value: PathType | None):
        if isinstance(value, str):
            try:
                assert not value.startswith("."), "`mode_dir` can't startswith `.`"
                assert not value.startswith("/"), "`mode_dir` can't startswith `/`"
                assert not value.endswith("/"), "`mode_dir` can't endswith `/`"
            except AssertionError as e:
                raise ArFiSettingsError(e) from e
        return value

    def computed_attr(self, instance, owner):
        if instance is not None:
            try:
                assert hasattr(
                    instance, "mode_dir_inherit_nested"
                ), f"""missing required attribute `mode_dir_inherit_nested` in class `{instance.__class__.__name__}` for correct operation `mode_dir`"""
            except AssertionError as e:
                raise ArFiSettingsError(e) from e
            mode_dir_inherit_nested = instance.mode_dir_inherit_nested
            mode_dir_attr = getattr(instance, "_mode_dir_attr", None)
            mode_dir = getattr(instance, self.private_name, self.default)
        else:
            try:
                assert hasattr(
                    owner, "mode_dir_inherit_nested"
                ), f"missing required attribute `mode_dir_inherit_nested` in class `{owner.__name__}` for correct operation `mode_dir`"
            except AssertionError as e:
                raise ArFiSettingsError(e) from e
            mode_dir_inherit_nested = owner.mode_dir_inherit_nested
            mode_dir_attr = None
            mode_dir = getattr(owner, self.private_name, self.default)

        mode_dir = (
            mode_dir
            if mode_dir != DEFAULT_PATH_SENTINEL
            else mode_dir_attr
            if mode_dir_attr is not None
            else self.default
        )

        if not mode_dir_inherit_nested:
            return mode_dir

        if self.inherited_value and self.inherited_value not in (SENTINEL, DEFAULT_PATH_SENTINEL):
            if mode_dir and mode_dir != DEFAULT_PATH_SENTINEL:
                mode_dir = f"{self.inherited_value}/{mode_dir}"
            else:
                mode_dir = self.inherited_value

        return mode_dir
