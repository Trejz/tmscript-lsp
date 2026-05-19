import re
from lsprotocol import types
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.server.user_types.script_types import ScriptTypeHandler


class UserDefinedVarialbes:
    def __init__(self, scripttypehandler: "ScriptTypeHandler") -> None:
        self.defined_user_variables: dict[str,dict[str,str]] = {}
        self._scripttypehandler: "ScriptTypeHandler" = scripttypehandler


    def collect_variables(self, document) -> dict[str,dict[str,str]]:
        """Scans Document for Variables"""
        types_regex = "|".join(map(re.escape, self._scripttypehandler.get_script_types()))

        definition_match = re.compile(rf"^\s*({types_regex})\s+(\w+)(?:\s*=\s*(.*))?$")
        assignment_match = re.compile(r"^\s*(\w+)\s*=\s*(.*)$")
        
        user_variables: dict[str,dict[str,str]] = {}

        for line in document.lines:
            line = line.lstrip("\ufeff").rstrip("\r\n")
            definition_regex_match = definition_match.match(line)
            assignment_regex_match = assignment_match.match(line)

            if definition_regex_match:
                var_type = definition_regex_match.group(1)
                var_name = definition_regex_match.group(2)
                var_value = definition_regex_match.group(3)

                user_variables[var_name] = {"var_type": var_type,
                                            "var_value": var_value if var_value is not None else "None"}

                continue


            if assignment_regex_match:
                var_name = assignment_regex_match.group(1)
                var_value = assignment_regex_match.group(2)

                if var_name in user_variables:
                    var_type = user_variables[var_name].get("var_type", "None")
                    user_variables[var_name] = {"var_type": var_type,
                                                "var_value": var_value if var_value is not None else "None"}

                continue

        return user_variables

    
    def get_user_defined_variables(self, document, defined_var: str, declared_type: str = "") -> list[types.CompletionItem]:
        user_variables: dict = self.collect_variables(document)
        items = []

        for var_name, var_data in user_variables.items():
            if var_data.get("var_type") == declared_type:
                if var_name == defined_var:
                    continue

                items += ([types.CompletionItem(
                    label=var_name,
                    kind=types.CompletionItemKind.Variable,
                    detail=var_data.get("var_type", ""),
                    documentation=f"Value = {var_data.get('var_value', 'None')}"
                    )
                 ])

        return items


    def get_all_user_defined_variables(self, document) -> list[types.CompletionItem]:
        user_variables: dict = self.collect_variables(document)
        items = []

        for var_name, var_data in user_variables.items():
                items += ([types.CompletionItem(
                    label=var_name,
                    kind=types.CompletionItemKind.Variable,
                    detail=var_data.get("var_type", ""),
                    documentation=f"Value = {var_data.get('var_value', 'None')}"
                    )
                 ])

        return items
