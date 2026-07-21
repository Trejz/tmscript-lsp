import json
from pathlib import Path
from lsprotocol import types
import sys
import re

from lsprotocol.types import InsertTextFormat


class ScriptMethodHandler:
    def __init__(self) -> None:
        self._script_methods: list[types.CompletionItem] = []
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
    

    def get_script_methods(self) -> dict:
        """Returns Scriptclasses and Parametrized Objects"""
        return self._scriptclasses | self._parametrized_objects


    def get_script_classes(self) -> dict:
        return self._scriptclasses


    def get_script_parametritzed_objects(self) -> dict:
        return self._parametrized_objects
    

    def get_scriptclass_completions(self) -> list[types.CompletionItem]:
        items: list[types.CompletionItem] = []

        for class_name, class_data in self._scriptclasses.items():
            constructor_data = class_data.get("constructor", "")
            if isinstance(constructor_data, list):
                constructor = "\n".join(constructor_data)
            else:
                constructor = str(constructor_data)

            description = class_data.get("description", "")
            doc_sections = [section for section in [description, constructor] if section]

            items.append(
                types.CompletionItem(
                    label=class_name,
                    kind=types.CompletionItemKind.Class,
                    detail="Script Class",
                    documentation=types.MarkupContent(
                        kind=types.MarkupKind.Markdown,
                        value="\n\n".join(doc_sections),
                    ),
                    sort_text=f"script_class_{class_name.lower()}",
                )
            )

        for object_name, object_data in self._parametrized_objects.items():
            description = object_data.get("description", "")
            items.append(
                types.CompletionItem(
                    label=object_name,
                    kind=types.CompletionItemKind.Class,
                    detail="Parameterized Object",
                    documentation=types.MarkupContent(
                        kind=types.MarkupKind.Markdown,
                        value=description,
                    ),
                    insert_text=f"{object_name}[$1]" if object_name != "Env" else object_name,
                    insert_text_format=InsertTextFormat.Snippet,
                    sort_text=f"parameterized_object_{object_name.lower()}",
                )
            )
        return items


    def collect_classes(self, document) -> dict:
        classes_regex = "|".join(map(re.escape, self._scriptclasses))

        definition_match = re.compile(rf"^\s*({classes_regex})\s+(\w+)(?:\s*=\s*(.*))?$")

        user_classes: dict[str,dict[str,str]] = {}

        for line in document.lines:
            line = line.lstrip("\ufeff").rstrip("\r\n")
            definition_regex_match = definition_match.match(line)

            if definition_regex_match:
                class_type = definition_regex_match.group(1)
                class_name = definition_regex_match.group(2)
                class_value = definition_regex_match.group(3)

                user_classes[class_name] = {"class_type": class_type,
                                            "class_value": class_value if class_value is not None else "None"}
                continue
        return user_classes


    def get_class_attribute_return_type(self, document, class_type: str, value: str) -> bool:
        user_classes: dict[str,dict[str,str]] = self.collect_classes(document)
        regex_match = re.search(r"(\w+)\.(\w+)", value)

        if regex_match:
            var_name = regex_match.group(1)
            var_attribute = regex_match.group(2)
        else:
            return False

        for class_name, class_data in user_classes.items():
            if class_name == var_name:
                var_type = class_data.get("class_type", "")

                class_data: dict = self._scriptclasses.get(var_type, {})
                for attribute_name, attribute_data in class_data.get("attributes", {}).items():
                    if var_attribute == attribute_name:
                        if class_type == attribute_data.get("return", ""):
                            return True
                        break
                break
        return False

    def get_object_attribute_return_type(self):
        raise NotImplementedError