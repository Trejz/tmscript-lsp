import json
from pathlib import Path
from lsprotocol import types
import sys

class KeywordHandler:
    def __init__(self) -> None:
        self._keywords: list[types.CompletionItem] = []
        self._data: dict[str, list]
        # Resolve to src/server/assets
        self._assets_dir = self._get_assets_dir()

        self._get_json()


    def _get_assets_dir(self) -> Path:
        """Get path to bundled resource."""
        if getattr(sys, "frozen", False):
            base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent), "assets")
        else:
            base_path = Path(__file__).parent.parent / "assets"

        return base_path


    def _get_json(self) -> None:
        with open(f"{self._assets_dir}/tmscript_keywords.json") as f:
            self._data = json.load(f).get("keywords", [])


    def get_keywords_completion(self) -> list[types.CompletionItem]:

        self._keywords = [types.CompletionItem(
                            label=keyword,
                            kind=types.CompletionItemKind.Keyword
                            ) for keyword in self._data
                        ]

        return self._keywords
