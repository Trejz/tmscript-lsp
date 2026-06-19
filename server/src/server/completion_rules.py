import re
from lsprotocol import types
from typing import TYPE_CHECKING

from src.server.enums.enums import VarTypeEnum


if TYPE_CHECKING:
    from src.server.user_types.script_types import ScriptTypeHandler
    from src.server.user_types.script_functions import ScriptFunctionHandler
    from src.server.user_types.user_variables import UserDefinedVarialbes
    from src.server.user_types.script_methods import ScriptMethodHandler

class CompletionRules:
    def __init__(self,
                 scripttypehandler: "ScriptTypeHandler",
                 scriptfunctionhandler: "ScriptFunctionHandler",
                 userdefinedvariables: "UserDefinedVarialbes",
                 scriptmethodhandler: "ScriptMethodHandler") -> None:

        self._scripttypehandler: "ScriptTypeHandler" = scripttypehandler
        self._scriptfunctionhandler: "ScriptFunctionHandler" = scriptfunctionhandler
        self._userdefinedvaraibles: "UserDefinedVarialbes" = userdefinedvariables
        self._scriptmehtodhandler: "ScriptMethodHandler" = scriptmethodhandler

    
    def rule_return_variable_type(self, before_cursor: str, document) -> types.CompletionList | None:
        """Returns only functions and user variables that return the correct data type"""

        regex_match = re.match(r"^(?:(\w+)\s+)?(\w+)\s*=\s*.*?$", before_cursor)

        items = []
        declared_type: str = ""

        if regex_match:
            if regex_match.group(1) is not None:
                declared_type = regex_match.group(1)

            else:
                for var_name, var_data in self._userdefinedvaraibles.collect_variables(document).items():
                    if regex_match.group(2) == var_name:
                        declared_type = var_data.get("var_type", "") 

            if declared_type in self._scripttypehandler.get_script_types():
                items = self._scriptfunctionhandler.get_fitting_return_script_functions(declared_type)
            
            user_vars = self._userdefinedvaraibles.get_user_defined_variables(document=document,
                                                                              defined_var=regex_match.group(2),
                                                                              declared_type=declared_type) 

            if declared_type == VarTypeEnum._bool:
                pass

            items += user_vars if user_vars is not None else [] 

            if items == []:
                return None

            return types.CompletionList(
                    is_incomplete=False,
                    items = items
                    )
        return None


    def rule_scriptclass_method_completions(self, before_cursor: str, document) -> types.CompletionList | None:
        script_classes = self._scriptmehtodhandler.get_script_classes()
        items = []
        regex_match = re.search(r'(\w+)\.', before_cursor)

        if not regex_match:
            return None

        current_var = regex_match.group(1)
        user_vars = self._scriptmehtodhandler.collect_classes(document)

        if current_var in user_vars:
            var_class = user_vars[current_var].get("class_type")
        else:
            return None

        for class_name, class_values in script_classes.items():
            if not class_name == var_class:
                continue

            for method_name, method_val in class_values.get("methods", {}).items():
                items.extend([types.CompletionItem(
                            label=method_name,
                            kind=types.CompletionItemKind.Function,
                            detail=f"{class_name} Class Method",
                            documentation=types.MarkupContent(
                                kind=types.MarkupKind.Markdown,
                                value=method_val.get("documentation", "")
                                ),
                            sort_text=f"method_{method_name}"
                            ) 
                        ])

        if not items:
            return None

        return types.CompletionList(
                is_incomplete=False,
                items = items
                )
        

    def rule_scriptclass_attributes_completions(self, before_cursor, document) -> types.CompletionList | None:
        script_classes = self._scriptmehtodhandler.get_script_classes()
        items = []
        regex_match = re.search(r'(\w+)\.', before_cursor)

        if not regex_match:
            return None

        current_var = regex_match.group(1)
        user_vars = self._scriptmehtodhandler.collect_classes(document)

        if current_var in user_vars:
            var_class = user_vars[current_var].get("class_type")
        else:
            return None

        for class_name, class_values in script_classes.items():
            if not class_name == var_class:
                continue

            for attribute_name, attribute_val in class_values.get("attributes", {}).items():
                items.extend([types.CompletionItem(
                            label=attribute_name,
                            kind=types.CompletionItemKind.Value,
                            detail=f"{class_name} Class Attribute",
                            documentation=types.MarkupContent(
                                kind=types.MarkupKind.Markdown,
                                value=attribute_val.get("description", "")
                                ),
                            sort_text=f"attribute_{attribute_name}"
                            ) 
                        ])

        if not items:
            return None

        return types.CompletionList(
                is_incomplete=False,
                items = items
                )


