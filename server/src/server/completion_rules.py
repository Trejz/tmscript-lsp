import re
from lsprotocol import types
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.server.user_types.script_types import ScriptTypeHandler
    from server.user_types.script_functions import ScriptFunctionHandler
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

        match = re.match(r"(\w+)\s+(\w+)\s*=.*$", before_cursor)
        items = []

        if match:
            declared_type = match.group(1)
            if declared_type in self._scripttypehandler.get_script_types():
                items = self._scriptfunctionhandler.get_fitting_return_script_functions(declared_type)

            if declared_type in self._userdefinedvaraibles.collect_variables(document).values():
                items += (self._userdefinedvaraibles.get_user_defined_variables(document))

            if items == []:
                return None

            return types.CompletionList(
                    is_incomplete=False,
                    items = items
                    )
    
        return None


    def rule_(self, before_cursor: str) -> list[types.CompletionItem]:
        raise NotImplementedError

