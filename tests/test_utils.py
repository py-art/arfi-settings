import pytest
from pydantic.aliases import AliasPath
from pydantic_core import PydanticUndefined

from arfi_settings.utils import create_dict_for_path, search_dict_for_path


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
