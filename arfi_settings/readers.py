import json
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from dotenv import dotenv_values

from .errors import ArFiSettingsError
from .types import PathType
from .utils import validate_cli_reader

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        tomllib = None
    import tomli
    import yaml
else:
    yaml = None
    tomllib = None
    tomli = None

__all__ = (
    "ArFiBaseReader",
    "ArFiReader",
)


def import_yaml() -> None:
    global yaml
    if yaml is not None:
        return
    try:
        import yaml
    except ImportError as e:
        raise ArFiSettingsError("PyYaml is not installed, run `pip install arfi-settings[yaml]`") from e


def import_toml() -> None:
    global tomli
    global tomllib
    if sys.version_info < (3, 11):
        if tomli is not None:
            return
        try:
            import tomli
        except ImportError as e:
            raise ArFiSettingsError("tomli is not installed, run `pip install arfi-settings[toml]`") from e
    else:
        if tomllib is not None:
            return
        import tomllib


class ArFiBaseReader(ABC):
    """Readers of the source settings."""

    default_cli_reader: Callable | None = None
    ROOT_DIR: PathType | None = None
    BASE_DIR: PathType | None = None

    def __init__(
        self,
        file_path: PathType | None = None,
        file_encoding: str | None = None,
        is_env_file: bool = False,
        is_env: bool = False,
        is_cli: bool = False,
        is_secret_file: bool = False,
        reader: str = "",
        ignore_missing: bool = False,
        **options,
    ) -> None:
        self.file_path = self._validate_file_path(file_path)
        self.file_encoding = file_encoding
        self.is_env_file = is_env_file
        self.is_env = is_env
        self.is_cli = is_cli
        self.is_secret_file = is_secret_file
        self.ignore_missing = ignore_missing
        self.reader = reader
        if self.reader:
            self.reader = self._normalize_reader_name(self.reader)
        self.options = options
        self._resolve_file_path()

    def _resolve_file_path(self):
        """Resolves file path."""

        if self.file_path is None:
            return
        if self.BASE_DIR is not None:
            self.BASE_DIR = Path(self.BASE_DIR).resolve()
        if self.ROOT_DIR is not None:
            self.ROOT_DIR = Path(self.ROOT_DIR).resolve()
        if not Path(self.file_path).is_absolute():
            if self.is_env_file and self.ROOT_DIR is not None:
                env_file_resolve = Path(self.ROOT_DIR) / self.file_path
                if env_file_resolve.is_file():
                    self.file_path = env_file_resolve
                else:
                    if self.BASE_DIR is not None:
                        self.file_path = Path(self.BASE_DIR) / self.file_path
            else:
                if self.BASE_DIR is not None:
                    self.file_path = Path(self.BASE_DIR) / self.file_path

    @staticmethod
    def _normalize_reader_name(name: str) -> str:
        """Normalizesza reader name."""

        try:
            assert name and isinstance(name, str), "Reader `name` must be not empty string"
            assert not name.startswith("_"), "Reader `name` must not start with `_`"
        except AssertionError as e:
            raise ArFiSettingsError(e) from e
        suffix = "reader"
        if not name.endswith(suffix):
            name = f"{name}_{suffix}"
        return name

    @classmethod
    def _is_exist_reader(cls, name: str) -> bool:
        """Check is exist reader."""

        name = cls._normalize_reader_name(name)
        return hasattr(cls, name)

    def _get_reader(self, name: str) -> Callable:
        """Get reader."""

        name = self._normalize_reader_name(name)
        if not self._is_exist_reader(name):
            raise ArFiSettingsError(f"{self.__class__.__name__}: `{name}` is not defined")
        return self.__getattribute__(name)

    @staticmethod
    def _validate_file_path(file_path: PathType | None) -> Path | None:
        """Validate and return file path."""

        if file_path is not None:
            try:
                if isinstance(file_path, str):
                    assert file_path
                if not isinstance(file_path, Path):
                    file_path = Path(file_path).expanduser()
                assert Path(file_path).as_posix().strip(".").strip("\\").strip("/")
            except (AssertionError, TypeError) as e:
                raise ArFiSettingsError(f"File path is not set or invalid: `{file_path}`") from e
            else:
                return file_path.expanduser()
        return file_path

    @classmethod
    def is_exist_file(cls, file_path: PathType | None) -> bool:
        """Checks if the file path is specified and if the file exists."""

        try:
            file_path: Path | None = cls._validate_file_path(file_path)
            if file_path is None:
                return False
        except ArFiSettingsError:
            return False
        if not file_path.exists():
            return False
        if not file_path.is_file():
            return False
        return True

    def toml_reader(self) -> dict[str, Any]:
        """Reads settings from TOML file."""

        import_toml()
        try:
            with open(self.file_path, mode="rb") as toml_file:
                if sys.version_info < (3, 11):
                    return tomli.load(toml_file)
                return tomllib.load(toml_file)
        except FileNotFoundError as e:
            if self.ignore_missing:
                return {}
            raise ArFiSettingsError(f"File not found: `{self.file_path.resolve().as_posix()}`") from e

    def yaml_reader(self) -> dict[str, Any]:
        """Reads settings from YAML file."""

        import_yaml()
        try:
            with open(self.file_path, encoding=self.file_encoding) as yaml_file:
                return yaml.safe_load(yaml_file)
        except FileNotFoundError as e:
            if self.ignore_missing:
                return {}
            raise ArFiSettingsError(f"File not found: `{self.file_path.resolve().as_posix()}`") from e

    def yml_reader(self) -> dict[str, Any]:
        """Reads settings from YAML file."""

        return self.yaml_reader()

    def json_reader(self) -> dict[str, Any]:
        """Reads settings from JSON file."""

        try:
            with open(self.file_path, encoding=self.file_encoding) as json_file:
                return json.load(json_file)
        except FileNotFoundError as e:
            if self.ignore_missing:
                return {}
            raise ArFiSettingsError(f"File not found: `{self.file_path.resolve().as_posix()}`") from e

    def env_file_reader(self) -> dict[str, str | None]:
        """Reads settings from .env file."""

        if not self.ignore_missing:
            if not self.is_exist_file(self.file_path):
                raise ArFiSettingsError(f"File not found: `{self.file_path.resolve().as_posix()}`")
        data: dict[str, str | None] = dotenv_values(self.file_path, encoding=self.file_encoding)
        return dict(data)

    def env_reader(self) -> dict[str, str | None]:
        """Reads settings from environment."""
        return dict(os.environ)

    def secret_file_reader(self) -> dict[str, str]:
        """Reads settings from secrets directory."""

        data = {}
        if not self.is_exist_file(self.file_path):
            if not self.ignore_missing:
                raise ArFiSettingsError(f"File not found: `{self.file_path.resolve().as_posix()}`")
            return data

        key_name = self.file_path.stem
        data[key_name] = self.file_path.read_text(encoding=self.file_encoding).strip()
        return data

    def cli_reader(self) -> dict[str, Any]:
        """Reads settings from CLI."""

        if self.default_cli_reader is not None:
            data = self.default_cli_reader()
            try:
                assert isinstance(data, dict)
            except AssertionError as e:
                raise ArFiSettingsError(f"CLI reader must return a dict. Got: {type(data)}") from e
            return data
        return {}

    @classmethod
    def setup_cli_reader(cls, cli_reader: Callable) -> None:
        """Setup default CLI reader.

        cli_reader: Callable Class or Function that returns a dict[srt, Any]
        """
        cls.default_cli_reader = validate_cli_reader(cli_reader)

    @abstractmethod
    def read(self) -> dict[str, Any]:
        """Read and return settings."""


class ArFiReader(ArFiBaseReader):
    """Reads settings from file."""

    def read(self) -> dict[str, Any]:
        if self.reader:
            reader = self._get_reader(self.reader)
            return reader()
        elif self.is_cli:
            return self.cli_reader()
        elif self.is_env:
            return self.env_reader()
        elif self.is_secret_file:
            return self.secret_file_reader()
        elif self.file_path is not None:
            if self.is_env_file:
                return self.env_file_reader()
            reader_name = self.file_path.suffix.strip(".")
            if not reader_name and not self.reader:
                raise ArFiSettingsError(f"No reader provided for file `{self.file_path.resolve().as_posix()}`.")
            reader_name = self._normalize_reader_name(reader_name or self.reader)
            if not self._is_exist_reader(reader_name):
                raise ArFiSettingsError(
                    f"{self.__class__.__name__}: reader `{reader_name}` is not defined "
                    f"for file `{self.file_path.resolve().as_posix()}`."
                )
            reader = self._get_reader(reader_name)
            return reader()
        else:
            raise ArFiSettingsError("No sources provided for the reading.")
