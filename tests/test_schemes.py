import pytest

from arfi_settings.schemes import FileConfigSchema, SettingsParamsSchema, SettingsConfigSchema
from pathlib import PosixPath


# @pytest.mark.current
@pytest.mark.schemes
def test_file_config_schema():
    result_dict = FileConfigSchema().conf_dict
    assert result_dict
    assert isinstance(result_dict, dict)

    data = {"conf_ext": "toml, yaml, json,ini,conf"}
    result_dict = FileConfigSchema(**data).conf_dict
    assert result_dict["conf_ext"] == ["toml", "yaml", "json", "ini", "conf"]


# @pytest.mark.current
@pytest.mark.schemes
def test_settings_config_schema():
    result_dict = SettingsConfigSchema().conf_dict
    assert result_dict
    assert isinstance(result_dict, dict)

    data = {"conf_ext": "toml, yaml, json,ini,conf"}
    result_dict = SettingsConfigSchema(**data).conf_dict
    assert result_dict["conf_ext"] == ["toml", "yaml", "json", "ini", "conf"]

    settings = SettingsConfigSchema()
    assert settings.config_model_dict == {
        "case_sensitive": False,
        "ignore_missing": True,
        "encoding": None,
        "cli": False,
        "secrets_dir": None,
        "conf_file": "config",
        "conf_dir": "config",
        "conf_ext": ["toml", "yaml", "yml", "json"],
        "conf_file_encoding": None,
        "conf_case_sensitive": False,
        "conf_ignore_missing": True,
        "conf_custom_ext_handler": None,
        "env_file": ".env",
        "env_prefix": "",
        "env_prefix_as_mode_dir": False,
        "env_prefix_as_nested_mode_dir": False,
        "env_prefix_as_source_mode_dir": False,
        "env_file_encoding": None,
        "env_case_sensitive": False,
        "env_nested_delimiter": "",
        "env_ignore_missing": True,
        "conf_path": [],
        "env_path": [],
        "conf_include_inherit_parent": [],
        "conf_exclude_inherit_parent": [],
        "env_include_inherit_parent": [],
        "env_exclude_inherit_parent": [],
        "include_inherit_parent": [],
        "exclude_inherit_parent": [],
    }


# @pytest.mark.current
@pytest.mark.schemes
def test_settings_params_schema():
    result_dict = SettingsParamsSchema().default_param_dict
    assert isinstance(result_dict, dict)
    assert result_dict == {
        "read_config": True,
        "read_config_force": False,
        "mode_dir": PosixPath("."),
        "mode_dir_inherit_nested": True,
        "mode_dir_inherit_parent": True,
        "file_config_inherit_parent": True,
        "env_config_inherit_parent": True,
        "conf_file": "config",
        "conf_dir": "config",
        "conf_ext": ["toml", "yaml", "yml", "json"],
        "conf_file_encoding": None,
        "conf_case_sensitive": False,
        "conf_ignore_missing": True,
        "conf_custom_ext_handler": None,
        "conf_include_inherit_parent": [],
        "conf_exclude_inherit_parent": [],
        "env_file": ".env",
        "env_prefix": "",
        "env_prefix_as_mode_dir": False,
        "env_prefix_as_nested_mode_dir": False,
        "env_prefix_as_source_mode_dir": False,
        "env_file_encoding": None,
        "env_case_sensitive": False,
        "env_nested_delimiter": "",
        "env_ignore_missing": True,
        "env_include_inherit_parent": [],
        "env_exclude_inherit_parent": [],
        "case_sensitive": False,
        "ignore_missing": True,
        "encoding": None,
        "cli": False,
        "secrets_dir": None,
        "include_inherit_parent": [],
        "exclude_inherit_parent": [],
        "handler": "",
        "handler_inherit_parent": True,
        "ordered_settings": [
            "cli",
            "init_kwargs",
            "env",
            "env_file",
            "secrets",
            "conf_file",
        ],
        "ordered_settings_inherit_parent": True,
    }

    data = {"_conf_ext": "toml, yaml, json,ini,conf"}
    result_dict = SettingsParamsSchema(**data).default_param_dict
    assert result_dict["conf_ext"] == ["toml", "yaml", "json", "ini", "conf"]
    _kwargs = SettingsParamsSchema(**data).get_param_dict()
    assert _kwargs and isinstance(_kwargs, dict)
    assert _kwargs == {
        "_read_config": None,
        "_read_config_force": None,
        "_mode_dir": PosixPath("."),
        "_mode_dir_inherit_nested": None,
        "_mode_dir_inherit_parent": None,
        "_file_config_inherit_parent": None,
        "_env_config_inherit_parent": None,
        "_conf_file": PosixPath("."),
        "_conf_dir": PosixPath("."),
        "_conf_ext": ["toml", "yaml", "json", "ini", "conf"],
        "_conf_file_encoding": "",
        "_conf_case_sensitive": None,
        "_conf_ignore_missing": None,
        "_conf_custom_ext_handler": "",
        "_conf_include_inherit_parent": None,
        "_conf_exclude_inherit_parent": None,
        "_env_file": PosixPath("."),
        "_env_prefix": None,
        "_env_prefix_as_mode_dir": None,
        "_env_prefix_as_nested_mode_dir": None,
        "_env_prefix_as_source_mode_dir": None,
        "_env_file_encoding": "",
        "_env_case_sensitive": None,
        "_env_nested_delimiter": None,
        "_env_ignore_missing": None,
        "_env_include_inherit_parent": None,
        "_env_exclude_inherit_parent": None,
        "_case_sensitive": None,
        "_ignore_missing": None,
        "_encoding": "",
        "_cli": None,
        "_secrets_dir": PosixPath("."),
        "_include_inherit_parent": None,
        "_exclude_inherit_parent": None,
        "_handler": "",
        "_handler_inherit_parent": None,
        "_ordered_settings": [""],
        "_ordered_settings_inherit_parent": None,
    }

    params = SettingsParamsSchema(**data)
    assert params.default_param_dict["conf_ext"] == ["toml", "yaml", "json", "ini", "conf"]
    params.update_exclude_default(**{"_conf_ext": "toml,ini"})
    assert params.default_param_dict["conf_ext"] == ["toml", "ini"]
