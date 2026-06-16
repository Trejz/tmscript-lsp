import json
from pathlib import Path
from lsprotocol import types
import sys
import re
from typing import Any


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
    

    def get_scriptclasses(self) -> list[types.CompletionItem]:
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
                    sort_text=f"parameterized_object_{object_name.lower()}",
                )
            )

        return items

    
    def collect_methods(self, document) -> dict:
        classes_regex = "|".join(map(re.escape, self._scriptclasses))

        definition_match = re.compile(rf"^\s*({classes_regex})\s+(\w+)(?:\s*=\s*(.*))?$")
        #assignment_match = re.compile(r"^\s*(\w+)\s*=\s*(.*)$")

        user_classes: dict[str,dict[str,str]] = {}

        for line in document.lines:
            line = line.lstrip("\ufeff").rstrip("\r\n")
            definition_regex_match = definition_match.match(line)
            #assignment_regex_match = assignment_match.match(line)

            if definition_regex_match:
                class_type = definition_regex_match.group(1)
                class_name = definition_regex_match.group(2)
                class_value = definition_regex_match.group(3)

                user_classes[class_name] = {"class_type": class_type,
                                            "class_value": class_value if class_value is not None else "None"}

                continue
        
        return user_classes


    def get_member_completions(self, before_cursor: str, document) -> list[types.CompletionItem]:
        """Return member completions for script class instances and parameterized objects."""

        object_member_match = re.match(r"^\s*(\w+)\.(\w*)$", before_cursor)
        parameterized_member_match = re.match(r"^\s*(\w+)\[[^\]]*\]\.(\w*)$", before_cursor)

        if parameterized_member_match:
            object_name = parameterized_member_match.group(1)
            prefix = parameterized_member_match.group(2)
            return self._get_parameterized_attribute_items(object_name, prefix)

        if object_member_match:
            object_name = object_member_match.group(1)
            prefix = object_member_match.group(2)

            user_classes = self.collect_methods(document)

            if object_name in user_classes:
                class_type = user_classes[object_name].get("class_type", "")
                return self._get_scriptclass_member_items(class_type, prefix)

            parameterized_data = self._parametrized_objects.get(object_name, {})
            if parameterized_data.get("indexType", "") == "none":
                return self._get_parameterized_attribute_items(object_name, prefix)

        return []


    def _get_scriptclass_member_items(self, class_type: str, prefix: str = "") -> list[types.CompletionItem]:
        class_data = self._scriptclasses.get(class_type, {})
        attributes = class_data.get("attributes", {})
        methods = class_data.get("methods", {})

        items: list[types.CompletionItem] = []
        items += self._build_attribute_items(attributes, prefix)
        items += self._build_method_items(methods, prefix)

        return items


    def _get_parameterized_attribute_items(self, object_name: str, prefix: str = "") -> list[types.CompletionItem]:
        object_data = self._parametrized_objects.get(object_name, {})
        attributes = object_data.get("attributes", {})
        return self._build_attribute_items(attributes, prefix)


    def _build_attribute_items(self, attributes: dict[str, Any], prefix: str = "") -> list[types.CompletionItem]:
        items: list[types.CompletionItem] = []

        for attribute_name, attribute_data in attributes.items():
            if prefix and not attribute_name.lower().startswith(prefix.lower()):
                continue

            if isinstance(attribute_data, dict):
                attribute_type = attribute_data.get("type", "")
                mode = attribute_data.get("mode", "")
                description = attribute_data.get("description", "")
                detail = f"{attribute_type} ({mode})" if mode else attribute_type
                documentation = description
            else:
                attribute_type = str(attribute_data)
                detail = attribute_type
                documentation = f"Type: {attribute_type}"

            items.append(
                types.CompletionItem(
                    label=attribute_name,
                    kind=types.CompletionItemKind.Property,
                    detail=detail,
                    documentation=types.MarkupContent(
                        kind=types.MarkupKind.Markdown,
                        value=documentation,
                    ),
                    sort_text=f"1_attr_{attribute_name.lower()}",
                )
            )

        return items


    def _build_method_items(self, methods: dict[str, Any], prefix: str = "") -> list[types.CompletionItem]:
        items: list[types.CompletionItem] = []

        for method_name, method_data in methods.items():
            if prefix and not method_name.lower().startswith(prefix.lower()):
                continue

            method_return = method_data.get("return", "")
            parameters: list[str] = method_data.get("parameters", [])
            documentation = method_data.get("documentation", "")

            if parameters:
                parameter_text = "\n".join([f"- {param}" for param in parameters])
            else:
                parameter_text = "- none"

            full_documentation = (
                f"{documentation}\n\n"
                f"**Parameters**\n{parameter_text}\n\n"
                f"**Return**\n{method_return}"
            )

            items.append(
                types.CompletionItem(
                    label=method_name,
                    kind=types.CompletionItemKind.Method,
                    detail=f"returns {method_return}",
                    documentation=types.MarkupContent(
                        kind=types.MarkupKind.Markdown,
                        value=full_documentation,
                    ),
                    sort_text=f"0_method_{method_name.lower()}",
                )
            )

        return items

