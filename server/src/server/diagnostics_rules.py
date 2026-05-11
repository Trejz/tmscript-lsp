import re
from lsprotocol import types
from typing import TYPE_CHECKING

from src.server.enums.enums import VarTypeEnum

if TYPE_CHECKING:
    from src.server.user_types.script_functions import ScriptFunctionHandler

class DiagnositcRules:
    def __init__(self, scriptfunctionhandler: "ScriptFunctionHandler") -> None:
        self._source: str = "tmscript-lsp"
        self._scriptfunctionhandler: "ScriptFunctionHandler" = scriptfunctionhandler


    def var_value_assignmenet(self, document) -> list[types.Diagnostic]:
        diagnostics: list[types.Diagnostic] = []

        regex_var_declaration = re.compile(r"^\s*(\w+)\s+(\w+)(?:\s*=\s*(.*))?$")
        for line_num, line in enumerate(document.lines):

            regex_match = regex_var_declaration.match(line)
            
            # Skip if no match
            if not regex_match:
                continue
            
            var_type = regex_match.group(1)
            #var_name = regex_match.group(2)
            var_value = regex_match.group(3)

            # Match to var_type
            match var_type:
                case VarTypeEnum._string:
                    
                    # Valid string
                    if var_value is None:
                        continue

                    value = var_value.strip()
                    
                    # No Value after =
                    if value == "":
                        message = "Expected string value"

                        diag_pos_start = types.Position(line=line_num,character=line.find("="))
                        diag_pos_end = types.Position(line=line_num, character=len(line))

                        diagnostics.append(types.Diagnostic(
                                range=types.Range(start=diag_pos_start,end=diag_pos_end),
                                message=message,
                                severity=types.DiagnosticSeverity.Error,
                                source=self._source,
                            )
                        )

                    # Wrong value after =
                    elif not re.match(r'^".*"$', value):
                        # Check if Function and valid Return type
                        regex_func = re.compile(r"^(\w+)\s*\(")
                        func_match = regex_func.match(value)
                        
                        diag_pos_start = types.Position(line=line_num,character=line.find("=") + 1)
                        diag_pos_end = types.Position(line=line_num, character=len(line))


                        if func_match:
                            valid, return_types = self._scriptfunctionhandler.get_valid_return_function(func_match.group(1),VarTypeEnum._string)

                            if valid:
                                continue

                            invalid_func_message = f"Invalid type. Function returns: {return_types}"

                            diagnostics.append(types.Diagnostic(
                                    range=types.Range(start=diag_pos_start,end=diag_pos_end),
                                    message=invalid_func_message,
                                    severity=types.DiagnosticSeverity.Error,
                                    source=self._source,
                                )
                            )

                            continue


                        # Check If correct String Format
                        invalid_string_format_message = "String value must be in quotes"

                        diagnostics.append(types.Diagnostic(
                                range=types.Range(start=diag_pos_start,end=diag_pos_end),
                                message=invalid_string_format_message,
                                severity=types.DiagnosticSeverity.Error,
                                source=self._source,
                            )
                        )

        return diagnostics
