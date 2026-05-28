import json
from pathlib import Path
from lsprotocol import types
import sys

class ScriptTypeHandler:
    def __init__(self) -> None:
        self._script_types: list[types.CompletionItem] = []
        self._data: list[str]
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
        with open(f"{self._assets_dir}/tmscript_types.json") as f:
            self._data = json.load(f).get("types", [])
    

    def get_script_types_completion(self) -> list[types.CompletionItem]:

        self._script_types = [types.CompletionItem(
                            label=type_name,
                            kind=types.CompletionItemKind.Keyword
                            ) for type_name in self._data
                        ]

        return self._script_types


    def get_script_types(self) -> list[str]:
        return self._data
