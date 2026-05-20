import re
from lsprotocol import types
from typing import TYPE_CHECKING

from src.server.enums.enums import VarTypeEnum


if TYPE_CHECKING:
    from src.server.user_types.script_types import ScriptTypeHandler
    from src.server.user_types.script_functions import ScriptFunctionHandler
    from src.server.user_types.user_variables import UserDefinedVarialbes

class CompletionRules:
    def __init__(self,
                 scripttypehandler: "ScriptTypeHandler",
                 scriptfunctionhandler: "ScriptFunctionHandler",
                 userdefinedvariables: "UserDefinedVarialbes") -> None:

        self._scripttypehandler: "ScriptTypeHandler" = scripttypehandler
        self._scriptfunctionhandler: "ScriptFunctionHandler" = scriptfunctionhandler
        self._userdefinedvaraibles: "UserDefinedVarialbes" = userdefinedvariables

    
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


    def rule_(self, before_cursor: str, document) -> list[types.CompletionItem]:
        raise NotImplementedError

