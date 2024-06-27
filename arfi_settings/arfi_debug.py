import json
from pathlib import Path
from typing import Literal
import copy

from .utils import is_settings, clean_value


class debug:
    def __init__(self, instance, func, mode: str = "", **kwargs):
        if not is_settings(type(instance)):
            return
        self.mode = mode
        if func == "__init__":
            self.show_init_info(instance, **kwargs)

    def show_init_info(self, instance, **kwargs):
        values = kwargs.get("values")
        if self.mode == "after":
            if instance._arfi_debug and instance.read_config:
                print("\033[34m")
                print("values after handler:")
                clear_value = clean_value(copy.deepcopy(values))
                print(json.dumps(clear_value, indent=4))
                print("\033[0m")
                return
        else:
            if instance._arfi_debug and instance.read_config or kwargs.get("arfi_debug"):
                conf_path = self._convert_debug_path(instance, instance.conf_path, "conf")
                env_path = self._convert_debug_path(instance, instance.env_path, "env")

                print("\033[34m")
                print(f"[PRE INIT] {instance.__class__.__name__}")
                print(f"root_dir = {instance.root_dir}")
                print(f"BASE_DIR = {instance.BASE_DIR}")
                print(f"pyproject_toml_path = {instance.pyproject_toml_path}")
                print("conf_path =", json.dumps(conf_path, indent=4))
                print("env_path =", json.dumps(env_path, indent=4))

                if instance._arfi_debug and instance.read_config:
                    print(f"mode_dir_path = {instance.mode_dir_path}")
                    print(f"computed_mode_dir = {instance.computed_mode_dir}")
                    print(f"source_mode_dir = {instance.source_mode_dir}")
                    print(f"nested_mode_dir = {instance.nested_mode_dir}")
                    print(f"parent_mode_dir = {instance.parent_mode_dir}")
                    print("settings_config =", instance.settings_config.model_dump_json(indent=4))
                    clear_value = clean_value(copy.deepcopy(values))
                    print("values before handler:")
                    print(json.dumps(clear_value, indent=4))

                print("\033[0m")
                return

    @staticmethod
    def _convert_debug_path(instance, list_path: list[Path], mode: Literal["conf", "env"]) -> list[str]:
        result = []
        base_dir = instance.BASE_DIR
        root_dir = instance.root_dir
        if instance.BASE_DIR is not None:
            base_dir = Path(instance.BASE_DIR).resolve()
        if instance.root_dir is not None:
            root_dir = Path(instance.root_dir).resolve()
        for path in list_path:
            if mode == "conf":
                if base_dir is not None:
                    path = base_dir / path
            elif mode == "env":
                if root_dir is not None:
                    if Path(root_dir / path).is_file():
                        path = root_dir / path
                    else:
                        if base_dir is not None:
                            path = base_dir / path
                else:
                    if base_dir is not None:
                        path = base_dir / path
            result.append(path.resolve().as_posix())
        return result
