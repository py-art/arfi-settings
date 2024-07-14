import os
import functools
import inspect
import typing
from pathlib import Path
from typing import Any, Callable

from pydantic._internal._typing_extra import NONE_TYPES, origin_is_union
from pydantic._internal._utils import (
    IMMUTABLE_NON_COLLECTIONS_TYPES,
    is_model_class,
    lenient_issubclass,
)
from pydantic.aliases import AliasPath
from pydantic_core import PydanticUndefined
from typing_extensions import get_args, get_origin

from .errors import ArFiSettingsError

__all__ = [
    "is_settings",
    "is_pydantic",
    "extract_unique_annotations",
    "create_dict_for_path",
    "search_dict_for_path",
    "allow_json_parse_failure",
    "validate_cli_reader",
    "clean_value",
    "is_descriptor",
]


def is_settings(_class: type) -> bool:
    """Check class is subclass of ArFiSettings."""

    from arfi_settings import ArFiSettings

    if lenient_issubclass(_class, ArFiSettings) and _class is not ArFiSettings:
        return True
    return False


def is_pydantic(_class: type) -> bool:
    """Check class is subclass of BaseModel."""
    return is_model_class(_class)


def extract_unique_annotations(args_types: type[Any] | tuple[type[Any], ...] | None) -> set[type[Any]]:
    """Searches for unique annotations in the tuple of types."""

    annotation_typyes = set()
    if not isinstance(args_types, tuple):
        origin_type = get_origin(args_types)
        if origin_type is None:
            annotation_typyes.add(args_types)
        args_types = get_args(args_types)

    for ann in args_types:
        ann_args = get_args(ann)
        if ann_args:
            ext_ann_args = extract_unique_annotations(ann_args)
            annotation_typyes = annotation_typyes.union(ext_ann_args)
        else:
            annotation_typyes.add(ann)
    return annotation_typyes


def create_dict_for_path(
    alias_path: AliasPath | list[str | int],
    value: Any = PydanticUndefined,
) -> dict[str | int, Any]:
    """Creates a dictionary for the path specified by the alias."""

    if isinstance(alias_path, AliasPath):
        alias_path = alias_path.convert_to_aliases()
    last_value = alias_path[-1]
    if value is not PydanticUndefined:
        last_value = {last_value: value}
    for key_alias in reversed(alias_path[:-1]):
        last_value = {key_alias: last_value}
    return last_value


def search_dict_for_path(
    alias_path: AliasPath | list[str | int],
    search_dict: dict,
    case_sensitive: bool = True,
) -> Any:
    """Searches a dictionary for the path specified by the alias.

    Returns:
        The value at the specified path, or `PydanticUndefined` if the path is not found.
    """
    if isinstance(alias_path, AliasPath):
        alias_path = alias_path.convert_to_aliases()

    assert isinstance(alias_path, list), "`alias_path` must be a AliasPath or list[str | int]"

    value = search_dict
    for key in alias_path:
        if isinstance(value, str):
            return PydanticUndefined

        if case_sensitive:
            try:
                value = value[key]
            except (KeyError, IndexError, TypeError):
                return PydanticUndefined
        else:
            if isinstance(key, str):
                search_value = dict()
                if value and isinstance(value, dict):
                    value_by_origin_key = value.get(key, PydanticUndefined)
                    if value_by_origin_key is not PydanticUndefined:
                        value = value_by_origin_key
                        continue
                    key = key.lower()
                    for k, v in value.items():
                        if isinstance(k, str):
                            k = k.lower()
                        if k not in search_value:
                            search_value[k] = v
                else:
                    search_value = value
                try:
                    value = search_value[key]
                except (KeyError, IndexError, TypeError):
                    return PydanticUndefined
            else:
                try:
                    value = value[key]
                except (KeyError, IndexError, TypeError):
                    return PydanticUndefined

    return value


def allow_json_parse_failure(field, field_name: str | None = None) -> bool:
    """Searches non json serializable fields."""

    origin_type = get_origin(field.annotation)
    if not origin_is_union(origin_type):
        if type(field.annotation) in IMMUTABLE_NON_COLLECTIONS_TYPES:
            return True
        if type(field.annotation) in NONE_TYPES:
            return True
        if isinstance(type(field.annotation), type(typing._LiteralGenericAlias)):
            return True
        if field.annotation is Any:
            return True
    else:
        args_types = get_args(field.annotation)
        if any([type(arg) in IMMUTABLE_NON_COLLECTIONS_TYPES for arg in args_types]):
            return True
        if any([type(arg) in NONE_TYPES for arg in args_types]):
            return True
        if any([isinstance(type(arg), type(typing._LiteralGenericAlias)) for arg in args_types]):
            return True
        if Any in args_types:
            return True
    return False


def validate_cli_reader(cli_reader: Callable) -> Callable:
    """Validate and returns cli reader."""

    if not callable(cli_reader):
        raise ArFiSettingsError(f"`cli_reader` must be callable. Got {type(cli_reader)}")

    if inspect.isfunction(cli_reader):
        # Append `self` as firest parameter to function
        oldsig = inspect.signature(cli_reader)
        params = list(oldsig.parameters.values())
        first_sels_params = inspect.Parameter(
            "self",
            inspect.Parameter.POSITIONAL_ONLY,
            default=inspect.Parameter.empty,
        )
        new_params = [first_sels_params]
        new_params.extend(params)
        sig = oldsig.replace(parameters=new_params)

        @functools.wraps(cli_reader)
        def wrapper(*args, **kwargs):
            ba = sig.bind(*args, **kwargs)
            ba.apply_defaults()
            if inspect.getfullargspec(cli_reader).args:
                return cli_reader(*ba.args[1:], **ba.kwargs)
            else:
                return cli_reader(**ba.kwargs)

        wrapper.__signature__ = sig
        return wrapper

    return cli_reader


def clean_value(data: dict[str, Any] | list[Any]) -> dict[str, Any]:
    new_data = dict()
    if isinstance(data, (list, set, tuple)):
        new_iterable = []
        for item in data:
            ni = clean_value(item)
            new_iterable.append(ni)
        return new_iterable

    assert isinstance(data, dict), f"Unexpected type {type(data)}"

    for k, v in data.items():
        if isinstance(k, str) and k.startswith("_"):
            continue
        elif isinstance(v, Path):
            v = v.as_posix()
        elif isinstance(v, dict):
            v = clean_value(v)
        elif isinstance(data, os.PathLike):
            v = str(v)
        new_data[k] = v
    return new_data


def is_descriptor(obj, name: str):
    """Simple check if an attribute is a descriptor."""

    value = inspect.getattr_static(obj, name)
    if getattr(type(value), "__get__", None):
        return True
    return False
