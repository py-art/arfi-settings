import inspect
import os
from pathlib import Path, PosixPath, PurePath, WindowsPath
from typing import Any, Literal, Union, Callable

import pytest
from pydantic import BaseModel
from pydantic.aliases import AliasPath
from pydantic_core import PydanticUndefined

from arfi_settings import ArFiSettings
from arfi_settings.utils import (
    allow_json_parse_failure,
    clean_value,
    create_dict_for_path,
    search_dict_for_path,
    validate_cli_reader,
)


@pytest.mark.utils
def test_create_dict_for_path():
    path = AliasPath("foo", "bar", "baz")
    res = create_dict_for_path(path)
    assert res == {"foo": {"bar": "baz"}}

    res = create_dict_for_path(path, "asd")
    assert res == {"foo": {"bar": {"baz": "asd"}}}

    path = ["foo", "bar", "baz"]
    res = create_dict_for_path(path)
    assert res == {"foo": {"bar": "baz"}}

    res = create_dict_for_path(path, "asd")
    assert res == {"foo": {"bar": {"baz": "asd"}}}


# @pytest.mark.current
@pytest.mark.utils
def test_search_dict_for_path():
    search_dict = {"foo": {"bar": {"baz": "asd"}}}
    path = AliasPath("foo", "bar", "baz")
    value = search_dict_for_path(path, search_dict)
    assert value == "asd"

    path = ["foo", "bar", "baz"]
    value = search_dict_for_path(path, search_dict)
    assert value == "asd"

    path = ["params", 1]
    search_dict = {"params": ["foo", "bar"]}
    value = search_dict_for_path(path, search_dict)
    assert value == "bar"

    value = search_dict_for_path(["params", 8], search_dict)
    assert value is PydanticUndefined

    value = search_dict_for_path(["params", 8], search_dict, case_sensitive=False)
    assert value is PydanticUndefined

    value = search_dict_for_path(["params", 8], "search_dict")
    assert value is PydanticUndefined

    value = search_dict_for_path(["params", 8], "search_dict", case_sensitive=False)
    assert value is PydanticUndefined

    with pytest.raises(AssertionError) as excinfo:
        search_dict_for_path("params", search_dict)
    assert "`alias_path` must be a AliasPath or list" in str(excinfo.value)

    with pytest.raises(AssertionError) as excinfo:
        search_dict_for_path("params", search_dict, case_sensitive=False)

    assert "`alias_path` must be a AliasPath or list" in str(excinfo.value)

    value = search_dict_for_path(AliasPath("params"), search_dict, case_sensitive=False)
    assert value == ["foo", "bar"]

    value = search_dict_for_path(["params"], search_dict, case_sensitive=False)
    assert value == ["foo", "bar"]

    search_dict = {"foo": {"BAR": {"baz": "asd"}}}
    path = AliasPath("FOO", "Bar", "baZ")
    value = search_dict_for_path(path, search_dict, case_sensitive=False)
    assert value == "asd"

    search_dict = {"FOO": {"BAR": {"BAZ": "ASD"}}}
    path = AliasPath("foo", "bar", "baz")
    value = search_dict_for_path(path, search_dict, case_sensitive=False)
    assert value == "ASD"

    search_dict = {"foo": {"BAR": {3: "asd"}}}
    path = AliasPath("FOO", "Bar", 3)
    value = search_dict_for_path(path, search_dict, case_sensitive=False)
    assert value == "asd"

    search_dict = {"foo": {3: {"BAR": "asd"}}}
    path = AliasPath("FOO", 3, "Bar")
    value = search_dict_for_path(path, search_dict, case_sensitive=False)
    assert value == "asd"

    search_dict = {3: {2: {1: []}}}
    path = AliasPath(3, 2, 1)
    value = search_dict_for_path(path, search_dict, case_sensitive=False)
    assert value == []

    search_dict = {3: {2: {(1, 0): []}}}
    path = AliasPath(3, 2, (1, 0))
    value = search_dict_for_path(path, search_dict, case_sensitive=False)
    assert value == []

    path = ["params", "foo"]
    search_dict = {"params": ["foo", "bar"]}
    value = search_dict_for_path(path, search_dict, case_sensitive=False)
    assert value is PydanticUndefined

    path = ["params", "foo"]
    search_dict = {"params": {"FOO": "baz", ("bar",): 22, 1: 44}}
    value = search_dict_for_path(path, search_dict, case_sensitive=False)
    assert value == "baz"


# @pytest.mark.current
@pytest.mark.utils
def test_validate_cli_reader():
    def custom_cli_reader_without_self():
        return dict(foo="bar")

    cli_reader = validate_cli_reader(custom_cli_reader_without_self)
    sig = inspect.signature(cli_reader)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "self"
    assert cli_reader(None) == {"foo": "bar"}

    def custom_cli_reader_with_self(self):
        return dict(foo="bar")

    cli_reader = validate_cli_reader(custom_cli_reader_with_self)
    sig = inspect.signature(cli_reader)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "self"
    assert cli_reader(None) == {"foo": "bar"}

    def custom_cli_reader_with_kwargs(asd=123):
        return dict(foo=asd)

    cli_reader = validate_cli_reader(custom_cli_reader_with_kwargs)
    sig = inspect.signature(cli_reader)
    params = list(sig.parameters.values())
    assert len(params) == 2
    assert params[0].name == "self"
    assert cli_reader(None) == {"foo": 123}


# @pytest.mark.current
@pytest.mark.utils
def test_clean_value(platform_system):
    common_path = Path("/settings")
    if platform_system == "Windows":
        path = WindowsPath("/config")
    else:
        path = PosixPath("/config")

    pure_path = PurePath("config\\settings")
    data = {
        "_param": 1,
        "common_path": common_path,
        "path": path,
        "my_dict": {
            "val": [1, 2, 3],
        },
        "os_path": os.path.join(common_path, path),
        "pure_path": pure_path,
    }
    value = clean_value(data)
    assert value == {
        "path": "/config",
        "common_path": "/settings",
        "my_dict": {"val": [1, 2, 3]},
        "os_path": os.path.join(common_path, path),
        "pure_path": "config\\settings",
    }

    wrong_data = (1, 2, 3)
    with pytest.raises(AssertionError) as excinfo:
        value = clean_value(wrong_data)

    assert "Unexpected type" in str(excinfo.value)

    iter_data = [
        {"id": 1, "name": "foo", "items": [1, 2, 3]},
        {"id": 2, "name": "bar", "items": [4, 5, 6]},
    ]
    clear_iter_value = clean_value(iter_data)
    assert clear_iter_value == [
        {"id": 1, "name": "foo", "items": [1, 2, 3]},
        {"id": 2, "name": "bar", "items": [4, 5, 6]},
    ]


# @pytest.mark.current
@pytest.mark.utils
def test_allow_json_parse_failure():
    class PidanticModel(BaseModel):
        asd: str = "asd"

    class AppConfig(ArFiSettings):
        str_field: str
        none_field: None
        int_field: int
        list_field: list
        any_field: Any
        literal_field: Literal["foo", "bar"]
        path_field: Path
        pydantic_field: PidanticModel
        union_1: Union[str, int]
        union_2: Union[PidanticModel, int]
        union_3: Union[PidanticModel, None]
        union_4: Union[PidanticModel, list[str]]
        union_5: Union[dict, int]
        union_6: Union[dict, Literal["foo", "bar"]]
        func: Callable

    str_field = AppConfig.model_fields["str_field"]
    none_field = AppConfig.model_fields["none_field"]
    int_field = AppConfig.model_fields["int_field"]
    list_field = AppConfig.model_fields["list_field"]
    any_field = AppConfig.model_fields["any_field"]
    literal_field = AppConfig.model_fields["literal_field"]
    path_field = AppConfig.model_fields["path_field"]
    pydantic_field = AppConfig.model_fields["pydantic_field"]
    union_1 = AppConfig.model_fields["union_1"]
    union_2 = AppConfig.model_fields["union_2"]
    union_3 = AppConfig.model_fields["union_3"]
    union_4 = AppConfig.model_fields["union_4"]
    union_5 = AppConfig.model_fields["union_5"]
    union_6 = AppConfig.model_fields["union_6"]
    func = AppConfig.model_fields["func"]

    is_allow_str = allow_json_parse_failure(str_field, "str_field")
    is_allow_none = allow_json_parse_failure(none_field, "none_field")
    is_allow_int = allow_json_parse_failure(int_field, "int_field")
    is_allow_list = allow_json_parse_failure(list_field, "list_field")
    is_allow_any = allow_json_parse_failure(any_field, "any_field")
    is_allow_literal = allow_json_parse_failure(literal_field, "literal_field")
    is_allow_path = allow_json_parse_failure(path_field, "path_field")
    is_allow_pydantic = allow_json_parse_failure(pydantic_field, "pydantic_field")
    is_allow_union_1 = allow_json_parse_failure(union_1, "union_1")
    is_allow_union_2 = allow_json_parse_failure(union_2, "union_2")
    is_allow_union_3 = allow_json_parse_failure(union_3, "union_3")
    is_allow_union_4 = allow_json_parse_failure(union_4, "union_4")
    is_allow_union_5 = allow_json_parse_failure(union_5, "union_5")
    is_allow_union_6 = allow_json_parse_failure(union_6, "union_6")
    is_allow_func = allow_json_parse_failure(func, "func")

    assert is_allow_str is True
    assert is_allow_none is True
    assert is_allow_int is True
    assert is_allow_list is False
    assert is_allow_any is True
    assert is_allow_literal is True
    assert is_allow_path is False
    assert is_allow_pydantic is False
    assert is_allow_union_1 is True
    assert is_allow_union_2 is True
    assert is_allow_union_3 is True
    assert is_allow_union_4 is False
    assert is_allow_union_5 is True
    assert is_allow_union_6 is True
    assert is_allow_func is False
