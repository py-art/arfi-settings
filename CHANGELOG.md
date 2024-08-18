# Change Log


## Development ...

### Fixes

- Fix allow_json_parse_failure
- Fix not valid value in init kwargs for field_is_settings
- Fix sqlite connector
- Fix behavior _read_pyproject_toml param
- Fix inherit instance_id and ordered_settings params


## [0.4.0] - (2024-07-26) latest

### Features

- Add `read_force` argument to `arfi_settings.init_settings.read_pyproject` function

### Fixes

- Fix resolve BASE_DIR

### Docs

- Update a description of the pyproject


## [0.3.1] - (2024-07-26)

### Fixes

- Fix read_pyproject


### Docs

- Add a description of the application configuration
- Update a description of the pyproject


## [0.3.0] - (2024-07-24)

### Fixes

- Fix work conf_custom_ext_handler. Add explicit reader indication for file ext handlers
- Fix duplicate `self` parameter in validate_cli_reader


### Docs

- Add a description of the handlers
- Add a description of the readers
- Add a description about usage cli
- Add a description of the connectors


## [0.2.1] - (2024-07-16)

### Fixes

- Fix incorrect definition of the `computed_mode_dir` property. The classic inheritance of the `mode_dir` parameter is disabled, since it participates in reverse inheritance.
- Fix inherit main handler from parent


### Docs

- Update "about". Add library_goals, why, debug_mode.
- Add "usage"


## [0.2.0] - (2024-07-16)

Yanked


## [0.1.1] - (2024-06-27)

### Docs

- Add documentation


## [0.1.0] - (2024-06-27)

Initial release

[0.1.0]: https://github.com/py-art/arfi-settings/releases/tag/0.1.0
[0.1.1]: https://github.com/py-art/arfi-settings/releases/tag/0.1.1
[0.2.0]: https://github.com/py-art/arfi-settings/releases/tag/0.2.0
[0.2.1]: https://github.com/py-art/arfi-settings/releases/tag/0.2.1
[0.3.0]: https://github.com/py-art/arfi-settings/releases/tag/0.3.0
[0.3.1]: https://github.com/py-art/arfi-settings/releases/tag/0.3.1
[0.4.0]: https://github.com/py-art/arfi-settings/releases/tag/0.4.0
