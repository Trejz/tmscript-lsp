import json
from pathlib import Path
from lsprotocol import types


class ScriptFunctionHandler:
    def __init__(self) -> None:
        self._script_functions: list[types.CompletionItem]
        self._data: dict[str,dict]
        # Resolve to src/assets
        self._assets_dir = Path(__file__).parent.parent.parent / "assets"

        self._read_json()


    def _read_json(self) -> None:
        with open(f"{self._assets_dir}/tmscript_functions.json") as f:
            self._data = json.load(f).get("functions", {})


    def get_script_functions_completion(self) -> list[types.CompletionItem]:

        self._script_functions = [types.CompletionItem(
                            label=function_name,
                            kind=types.CompletionItemKind.Function,
                            detail=function_data.get("category", ""),
                            documentation=types.MarkupContent(
                                kind=types.MarkupKind.Markdown,
                                value="\n".join(function_data.get("documentation", []))
                                ),
                            sort_text=f"{function_data.get("category", "")}_{function_name.lower()}"
                            ) for function_name, function_data in self._data.items()
                        ]

        return self._script_functions
        

    def get_fitting_return_script_functions(self, script_type: str) -> list[types.CompletionItem]:
        fitting_functions: list[types.CompletionItem] = []

        for function_name, function_data in self._data.items():
            if script_type in function_data.get("return", []) or "any" in function_data.get("return", []) or "any[]" in function_data.get("return", []):
                fitting_functions += [types.CompletionItem(
                            label=function_name,
                            kind=types.CompletionItemKind.Function,
                            detail=function_data.get("category", ""),
                            documentation=types.MarkupContent(
                                kind=types.MarkupKind.Markdown,
                                value="\n".join(function_data.get("documentation", []))
                                ),
                            sort_text=f"{function_data.get("category", "")}_{function_name.lower()}"
                            ) 
                        ]

        return fitting_functions

            
