---
title:
template: home.html
---
<p align="center">
  <a href="https://py-art.github.io/arfi-settings/en/">
    <img src="https://github.com/py-art/arfi-settings/blob/main/docs/assets/images/github-logo.png?raw=true" alt="ArFiSettings">
  </a>
</p>
<p align="center">
  <i>ArFiSettings - flexible application settings management with Pydantic validation</i>
</p>
<p align="center">
  <a href="https://codecov.io/github/py-art/arfi-settings" target="_blank">
    <img alt="Codecov" src="https://img.shields.io/codecov/c/github/py-art/arfi-settings?color=008080&logo=codecov&logoColor=008080">
  </a>
  <a href="https://pypi.org/project/arfi-settings" target="_blank">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/v/arfi-settings?label=pipy%20package&color=008080" alt="Package version"/>
  </a>
  <a href="https://pypi.org/project/arfi-settings" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/arfi-settings?color=008080" alt="Supported Python versions"/>
  </a>
</p>
___

**Documentation**: [https://py-art.github.io/arfi-settings](https://py-art.github.io/arfi-settings)

**Source code**: [https://github.com/py-art/arfi-settings](https://github.com/py-art/arfi-settings)

*Logo courtesy of*: [Alex Zalevski](https://github.com/zalexstudios)


> At the moment, the documentation is only available in Russian. Any help on translation is welcome.

## Advantages

- Contains all the functionality of [pydantic-settings](https://github.com/pydantic/pydantic-settings), but with more accurate name resolving.
- Inheritance is used when reading from any source.
- Specifying [configuration sources](usage/config.md#ordered_settings) is individual for each class of settings.
- Possibility to switch all settings by changing just one [MODE](usage/config.md#MODE) parameter.
- Ability to switch between specific settings using the discriminator.
- Read configuration files with and without any extension.
- Configure reading [command line parameters](usage/cli.md) individually for the class and for the entire project.
- Flexible setting of absolutely all parameters.
- Clear configuration file structure out of the box with no need for pre-configuration. Flexible setting of absolutely all parameters.
- Easy creation of your own configuration read sources.
- Availability of [connectors](usage/connectors.md#) to the most common databases
- Specify your own default library settings in the `pyproject.toml` file.
- [Debug Mode](about/debug_mode.md#).
- And many other things ...
