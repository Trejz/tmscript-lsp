import re
from lsprotocol import types
from typing import TYPE_CHECKING

from src.server.enums.enums import VarTypeEnum

if TYPE_CHECKING:
    from src.server.user_types.script_functions import ScriptFunctionHandler
    from src.server.user_types.user_variables import UserDefinedVarialbes

class DiagnositcRules:
    def __init__(self, 
                 scriptfunctionhandler: "ScriptFunctionHandler", 
                 userdefinedvariables: "UserDefinedVarialbes") -> None:

        self._source: str = "tmscript-lsp"
        self._scriptfunctionhandler: "ScriptFunctionHandler" = scriptfunctionhandler
        self._userdefinedvariables: "UserDefinedVarialbes" = userdefinedvariables
        
        self._diagnostics: list[types.Diagnostic]
        self._user_vars: dict[str,dict[str,str]] = {}


    def var_value_assignmenet(self, document) -> list[types.Diagnostic]:
        self._diagnostics: list[types.Diagnostic] = []

        regex_var_declaration = re.compile(r"^\s*(?:(\w+)\s+)?(\w+)\s*=\s*(.*)$")
        for line_num, line in enumerate(document.lines):

            regex_match = regex_var_declaration.match(line)
            
            # Skip if no match
            if not regex_match:
                continue
            
            var_type = regex_match.group(1)
            var_name = regex_match.group(2)
            var_value = regex_match.group(3)

            self._user_vars = self._userdefinedvariables.collect_variables(document)

            # Check if Variable Defined
            if var_type is None:
                if var_name not in self._user_vars:
                    message = "Variable not defined"

                    diag_pos_start = types.Position(line=line_num,character=line.find("="))
                    diag_pos_end = types.Position(line=line_num, character=len(line))

                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=diag_pos_start,end=diag_pos_end),
                            message=message,
                            severity=types.DiagnosticSeverity.Error,
                            source=self._source,
                        )
                    )

                    continue
                

            # Match to var_type
            match var_type:
                case VarTypeEnum._string:
                    
                    # Valid var definition
                    if var_value is None:
                        continue

                    value = var_value.strip()
                    
                    self._check_variable_assignment(var_type=var_type,
                                                    value=value,
                                                    line=line,
                                                    line_num=line_num)

        return self._diagnostics


    def _check_variable_assignment(self, var_type: str, value: str, line, line_num) -> None:
        # No Value after =
        if value == "":
            message = "Expected string value"

            diag_pos_start = types.Position(line=line_num,character=line.find("="))
            diag_pos_end = types.Position(line=line_num, character=len(line))

            self._diagnostics.append(types.Diagnostic(
                    range=types.Range(start=diag_pos_start,end=diag_pos_end),
                    message=message,
                    severity=types.DiagnosticSeverity.Error,
                    source=self._source,
                )
            )

        # Wrong value after =
        elif not re.match(r'^".*"$', value):
            diag_pos_start = types.Position(line=line_num,character=line.find("=") + 1)
            diag_pos_end = types.Position(line=line_num, character=len(line))

            if not self._function_return_type(value,diag_pos_start,diag_pos_end):
                return

            # Check If correct String Format
            striped_values: list[str] = [val.strip() for val in value.split("+")]
            if len(striped_values) >= 2:
                for val in striped_values:
                    # Check if valid Var
                    if val in self._user_vars:
                        continue
                    
                    if val.startswith('"') and val.endswith('"'):
                        continue

                    if val.startswith('"') and not val.endswith('"'):
                        message = f"String {val.strip('"')} missing quote at the end"
                        self._diagnostics.append(types.Diagnostic(
                                range=types.Range(start=diag_pos_start,end=diag_pos_end),
                                message=message,
                                severity=types.DiagnosticSeverity.Error,
                                source=self._source,
                            )
                        )
                        continue

                    if not val.startswith('"') and val.endswith('"'):
                        message = f"String {val.strip('"')} missing quote at the start"
                        self._diagnostics.append(types.Diagnostic(
                                range=types.Range(start=diag_pos_start,end=diag_pos_end),
                                message=message,
                                severity=types.DiagnosticSeverity.Error,
                                source=self._source,
                            )
                        )
                        continue

                    if not self._function_return_type(val,diag_pos_start,diag_pos_end):
                        continue

                    message = f"String {val} value must be in quotes"

                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=diag_pos_start,end=diag_pos_end),
                            message=message,
                            severity=types.DiagnosticSeverity.Error,
                            source=self._source,
                        )
                    )

    def _function_return_type(self, value:str, diag_pos_start, diag_pos_end) -> bool:
        """Return True if continue"""
        if value.endswith("()"):
            value = value[:-2]

        regex_func = re.compile(r"^(\w+)\s*\(")
        func_match = regex_func.match(value)

        if func_match:
            valid, return_types = self._scriptfunctionhandler.get_valid_return_function(func_match.group(1),VarTypeEnum._string)

            if valid:
                return True

            message = f"Invalid type. Function returns: {return_types}"

            self._diagnostics.append(types.Diagnostic(
                    range=types.Range(start=diag_pos_start,end=diag_pos_end),
                    message=message,
                    severity=types.DiagnosticSeverity.Error,
                    source=self._source,
                )
            )

        return False
