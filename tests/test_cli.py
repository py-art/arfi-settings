import argparse
import sys

import pytest
from pydantic import AliasChoices, Field

from arfi_settings import (
    ArFiReader,
    ArFiSettings,
    SettingsConfigDict,
)


# @pytest.mark.current
@pytest.mark.cli
def test_cli(monkeypatch, cwd_to_tmp):
    def parse_args():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument(
            "--debug",
            type=bool,
            const=True,
            nargs="?",
            help="Debug application",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
        )
        parser.add_argument(
            "-p",
            "--price",
            type=int,
            action="store",
            help="Fruit price",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            default="default_test_name",
            action="store",
            help="Application name",
        )
        cli_options = parser.parse_args()
        return dict(cli_options._get_kwargs())

    ArFiReader.setup_cli_reader(parse_args)

    class Cost(ArFiSettings):
        DEBUG: bool = False
        price: int
        verbose: int

        model_config = SettingsConfigDict(
            cli=True,
        )

    class Fruit(ArFiSettings):
        DEBUG: bool = False
        cost: Cost
        name: str

    class AppConfig(ArFiSettings):
        DEBUG: bool = False
        name: str
        fruit: Fruit
        model_config = SettingsConfigDict(
            cli=True,
        )

    monkeypatch.setenv("name", "Orange")
    monkeypatch.setattr(sys, "argv", [sys.argv[0], "-vvv", "--debug", "-p", "99", "--name", "SuperApp"])
    config = AppConfig()
    assert config.DEBUG is True
    assert config.fruit.DEBUG is False
    assert config.fruit.cost.DEBUG is True
    assert config.name == "SuperApp"
    assert config.fruit.name == "Orange"
    assert config.fruit.cost.price == 99
    assert config.fruit.cost.verbose == 3

    class AppConfig(ArFiSettings):
        SuperName: str = Field(alias="name")
        model_config = SettingsConfigDict(
            cli=True,
        )

    config = AppConfig()
    assert config.SuperName == "SuperApp"

    monkeypatch.setenv("EnvName", "EnvName")
    monkeypatch.setattr(sys, "argv", [sys.argv[0], "--name", "CliAppName"])

    class AppConfig(ArFiSettings):
        SuperName: str = Field(validation_alias=AliasChoices("EnvName", "name"))
        model_config = SettingsConfigDict(
            cli=True,
        )

    config = AppConfig()
    assert config.SuperName == "CliAppName"

    class AppConfig(ArFiSettings):
        SuperName: str = Field(validation_alias=AliasChoices("EnvName", "name"))
        model_config = SettingsConfigDict(
            cli=True,
        )
        ordered_settings = [
            "env",
            "cli",
        ]

    config = AppConfig()
    assert config.SuperName == "EnvName"
