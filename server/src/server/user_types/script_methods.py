import json
from pathlib import Path
from lsprotocol import types
import sys


class ScriptFunctionHandler:
    def __init__(self) -> None:
        self._script_functions: list[types.CompletionItem] = []
        self._data: dict[str,dict]
        self._scriptclasses: dict[str,dict] = {}
        self._parametrized_objects: dict[str,dict] = {}

        # Resolve to src/server/assets
        self._assets_dir = self._get_assets_dir()

        self._read_json()


    def _get_assets_dir(self) -> Path:
        """Get path to bundled resource."""
        if getattr(sys, "frozen", False):
            base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent), "assets")
        else:
            base_path = Path(__file__).parent.parent / "assets"

        return base_path


    def _read_json(self) -> None:
        with open(f"{self._assets_dir}/tmscript_methods.json") as f:
            self._data = json.load(f)
            
        self._scriptclasses = self._data.get("scriptclasses", {})
        self._parametrized_objects = self._data.get("parameterizedObjects", {})
    

    def get_scriptclasses(self):
        raise NotImplementedError
