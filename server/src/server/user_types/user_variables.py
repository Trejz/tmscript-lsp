import re
from lsprotocol import types

class UserDefinedVarialbes:
    def __init__(self) -> None:
        pass


    def collect_variables(self, document) -> dict[str,str]:
        """Scans Document for Variables"""
        var_match = re.compile(r"(\w+)\s+(\w+)\s*=")
        
        user_variables: dict[str,str] = {}

        for line in document.lines:
            match = var_match.match(line)

            if not match:
                continue
            
            var_type = match.group(1)
            var_name = match.group(2)

            user_variables[var_name] = var_type

        return user_variables

    
    def get_user_defined_variables(self, document) -> list[types.CompletionItem]:
        user_variables = self.collect_variables(document)
        return [types.CompletionItem(
                    label=var_name,
                    kind=types.CompletionItemKind.Variable,
                    detail=var_type
                    ) for var_name, var_type in user_variables.items()
                ]

