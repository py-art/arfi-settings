import functools
import inspect
import warnings
from pathlib import Path

import pydantic
from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import PydanticUndefined
from typing_extensions import Annotated

from .constants import (
    PYPROJECT_TOML_MAX_DEPTH,
)
from .readers import ArFiReader
from .schemes import PyProjectSchema
from .types import PathType
from .utils import search_dict_for_path

__all__ = [
    "init_settings",
]


class InitSettings(BaseModel):
    """Init settings."""

    root_dir: PathType | None = None
    base_dir: PathType | None = None
    pyproject_toml_path: PathType | None = None
    pyproject_toml_depth: Annotated[int, Field(ge=0)] | None = None
    pyproject_toml_max_depth: Annotated[int, Field(ge=0)] | None = PYPROJECT_TOML_MAX_DEPTH
    init_params: PyProjectSchema = PyProjectSchema()
    main_config_file: Path | None = None
    read_pyproject_toml: bool = True
    called_line: int | None = None
    main_config_class: str | None = None

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=False,
        validate_return=False,
    )

    def read_pyproject(
        self,
        read_once: bool = False,
        read_pyproject_toml: bool = True,
        pyproject_toml_depth: int | None = None,
        pyproject_toml_max_depth: int = PYPROJECT_TOML_MAX_DEPTH,
        class_name: str | None = None,
        search_base_dir: bool = True,
    ):
        """Searches and read pyproject.toml file."""

        if not read_pyproject_toml:
            return
        self.pyproject_toml_depth = pyproject_toml_depth
        self.pyproject_toml_max_depth = pyproject_toml_max_depth

        called_file, lineno = self._search_called_file()
        self.main_config_class = class_name
        self.called_line = lineno
        if self.main_config_file is not None and called_file == self.main_config_file.as_posix():
            return

        self.main_config_file = Path(called_file).resolve()
        if not self.read_pyproject_toml:
            return
        if read_once:
            self.read_pyproject_toml = False
        pyproject_toml_path = self._search_pyproject_toml(
            called_file,
            pyproject_toml_depth,
            pyproject_toml_max_depth,
        )
        if pyproject_toml_path is None:
            return
        if pyproject_toml_path == self.pyproject_toml_path:
            return

        if self.pyproject_toml_path is not None:
            warnings.warn_explicit(
                f"\033[33m\n"
                f"Path to pyproject.toml has been changed !!!\n"
                f"instance {class_name}()\n"
                f"    previous path:\n"
                f"{self.pyproject_toml_path.as_posix()}\n"
                f"    current path:\n"
                f"{pyproject_toml_path.as_posix()}\n"
                f"Call once\n"
                f"  from arfi_settings.init_config import init_settings\n"
                f"  init_settings.read_pyproject(read_once=True)\n"
                f"before import any instance or subclass `ArFiSettings` for fix it."
                f"\033[0m",
                category=Warning,
                filename=called_file,
                lineno=lineno,
            )

        self.pyproject_toml_path = pyproject_toml_path
        self.root_dir = pyproject_toml_path.parent.resolve()

        reader = ArFiReader(
            file_path=pyproject_toml_path,
        )
        pyproject_toml_data = reader.read()
        search_path = ["tool", "arfi_settings"]
        init_data = search_dict_for_path(search_path, pyproject_toml_data)
        if init_data is not PydanticUndefined:
            if init_data:
                try:
                    self.init_params = PyProjectSchema(**init_data)
                except pydantic.ValidationError as e:
                    e.add_note(f"Source file: \033[32m{pyproject_toml_path.as_posix()}\033[0m")
                    raise e
            else:
                self.init_params = PyProjectSchema()
        else:
            self.init_params = PyProjectSchema()

    @staticmethod
    def _search_called_file() -> tuple[str, int]:
        """Searches file which called initialization ArFiSettings."""

        called_file = ""
        lineno = 0
        for elem in reversed(inspect.stack()):
            if "importlib" in elem.filename:
                continue
            if elem.filename.endswith("/arfi_settings/main.py"):
                break
            if "/arfi_settings/" in elem.filename:
                continue
            lineno = elem.lineno
            called_file = Path(elem.filename).resolve().as_posix()

        return called_file, lineno

    def _search_pyproject_toml(
        self,
        cwd: PathType,
        depth: int | None = None,
        max_depth: int | None = PYPROJECT_TOML_MAX_DEPTH,
    ) -> Path | None:
        """Search pyproject.toml file."""

        pyproject_toml_file = None
        if isinstance(cwd, str):
            cwd = Path(cwd)
        assert isinstance(cwd, Path)

        if cwd.is_file():
            cwd = cwd.parent

        assert cwd.is_dir()

        if max_depth is None:
            max_depth = PYPROJECT_TOML_MAX_DEPTH

        real_depth = None
        if depth is not None:
            real_depth = depth
            self.pyproject_toml_max_depth = None
            if depth:
                for _ in range(0, depth):
                    cwd = cwd.parent
        elif max_depth:
            for i in range(0, max_depth + 1):
                file_path = cwd / "pyproject.toml"
                if file_path.is_file():
                    real_depth = i
                    break
                else:
                    if i < max_depth:
                        cwd = cwd.parent

        file_path = cwd / "pyproject.toml"
        if file_path.is_file():
            pyproject_toml_file = file_path.resolve()
            self.pyproject_toml_depth = real_depth
        return pyproject_toml_file

    def _search_base_dir(self):
        """Searches base dir for project."""

        current_root_dir = self.main_config_file.parent
        while self.root_dir is None:
            if Path(current_root_dir / "__init__.py").is_file():
                current_root_dir = current_root_dir.parent
                continue
            self.root_dir = current_root_dir.resolve()
        base_dir = self.main_config_file.parent
        previous_dir = base_dir
        while previous_dir != self.root_dir:
            if not Path(previous_dir / "__init__.py").is_file():
                break
            base_dir = previous_dir
            previous_dir = previous_dir.parent

        if Path(previous_dir / "__init__.py").is_file():
            base_dir = previous_dir

        source_base_dir_str = ""
        if self.base_dir is not None:
            source_base_dir_str = self.base_dir.as_posix()
        find_base_dir_str = base_dir.resolve().as_posix()
        if source_base_dir_str != find_base_dir_str:
            if not find_base_dir_str.startswith(source_base_dir_str):
                self.base_dir = base_dir.resolve()
                return
        if not self.base_dir:
            self.base_dir = base_dir.resolve()

    def _search_base_dir_decorator(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            if kwargs.get("search_base_dir"):
                self._search_base_dir()

        return wrapper

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if name == "read_pyproject":
            value = self._search_base_dir_decorator(value)
        return value


init_settings: InitSettings = InitSettings()
