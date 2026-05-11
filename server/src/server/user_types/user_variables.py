import re
from lsprotocol import types

class UserDefinedVarialbes:
    def __init__(self) -> None:
        self.user_variables: dict[str,dict[str,str]] = {}


    def collect_variables(self, document) -> dict[str,dict[str,str]]:
        """Scans Document for Variables"""
        var_match = re.compile(r"(\w+)?\s+(\w+)\s*=\s*(.*)?$")
        
        user_variables: dict[str,dict[str,str]] = {}

        for line in document.lines:
            regex_match = var_match.match(line)

            if not regex_match:
                continue
            
            var_type = regex_match.group(1)
            var_name = regex_match.group(2)
            var_value = regex_match.group(3)

            user_variables[var_name] = {"var_type": var_type if var_type is not None else "",
                                        "var_value": var_value}

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
                    documentation=f"Value = {var_data.get("var_value", "None")}"
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
                    documentation=f"Value = {var_data.get("var_value", "None")}"
                    )
                 ])

        return items
