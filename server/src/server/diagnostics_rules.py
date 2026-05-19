import re
from lsprotocol import types
from typing import TYPE_CHECKING

from src.server.enums.enums import VarTypeEnum

if TYPE_CHECKING:
    from src.server.user_types.script_functions import ScriptFunctionHandler
    from src.server.user_types.user_variables import UserDefinedVarialbes
    from src.server.user_types.script_types import ScriptTypeHandler

class DiagnositcRules:
    def __init__(self, 
                 scriptfunctionhandler: "ScriptFunctionHandler", 
                 userdefinedvariables: "UserDefinedVarialbes",
                 scripttypehandler: "ScriptTypeHandler") -> None:

        self._source: str = "tmscript-lsp"
        self._scriptfunctionhandler: "ScriptFunctionHandler" = scriptfunctionhandler
        self._userdefinedvariables: "UserDefinedVarialbes" = userdefinedvariables
        self._scripttypehandler: "ScriptTypeHandler" = scripttypehandler
        
        self._diagnostics: list[types.Diagnostic] = []
        self._user_vars: dict[str,dict[str,str]] = {}
        self._diag_pos_start: types.Position = types.Position(line=0,character=0)
        self._diag_pos_end: types.Position = types.Position(line=0,character=0)


    def var_value_assignmenet(self, document) -> list[types.Diagnostic]:
        self._diagnostics: list[types.Diagnostic] = []

        regex_var_declaration = re.compile(r"^\s*(?:(\w+)\s+)?(\w+\s*)(?:=\s*(.*))?$")

        for line_num, line in enumerate(document.lines):
            line = line.lstrip("\ufeff").rstrip("\r\n")
            regex_match = regex_var_declaration.match(line)
            
            # Skip if no match
            if not regex_match:
                continue
            
            var_type: str | None = regex_match.group(1)
            var_name: str | None = regex_match.group(2)
            var_value: str | None = regex_match.group(3)

            self._user_vars = self._userdefinedvariables.collect_variables(document)

            eq_pos = line.find("=") if "=" in line else len(line.rstrip()) - 1
            self._diag_pos_start = types.Position(line=line_num,character=max(0, eq_pos))
            self._diag_pos_end = types.Position(line=line_num, character=len(line))

            # Check if type Keyword is correct
            if var_type is not None and var_name is not None: 
                if var_type not in self._scripttypehandler.get_script_types():
                    
                    message: str = f"""Type Keyword "{var_type}" is not valid""" 
                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                            message=message,
                            severity=types.DiagnosticSeverity.Error,
                            source=self._source,
                        )
                    )
                    continue

            # Check if Variable Defined
            if var_type is None:
                var_name = var_name.strip() if var_name is not None else var_name
                if var_name not in self._user_vars:
                    message = "Variable not defined"

                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
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
                    self._check_string_variable_assignment(value=value, var_type=var_type)

                case VarTypeEnum._int | VarTypeEnum._byte:
                    # Valid var definition
                    if var_value is None:
                        continue

                    value = var_value.strip()
                    self._check_int_byte_variable_assignment(value=value,var_type=var_type)

                case VarTypeEnum._float | VarTypeEnum._double:
                    # Valid var definition
                    if var_value is None:
                        continue

                    value = var_value.strip()
                    self._check_float_double_variable_assignment(value=value, var_type=var_type)

        return self._diagnostics


    def _function_return_type(self, value: str, var_type: str) -> bool:
        """Return True when value is a function expression (valid or invalid)."""
        regex_func = re.compile(r"^(\w+)\s*\((.*)\)$")
        func_match = regex_func.match(value)

        if func_match:
            valid, return_types = self._scriptfunctionhandler.get_valid_return_function(func_match.group(1),var_type)

            if valid:
                return True

            message = f"Invalid type. Function returns: {return_types}"

            self._diagnostics.append(types.Diagnostic(
                    range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                    message=message,
                    severity=types.DiagnosticSeverity.Error,
                    source=self._source,
                )
            )

            # Function call was recognized and diagnosed; callers should not add
            # a second "Value is not a <type>" diagnostic for the same expression.
            return True

        return False


    def _check_string_variable_assignment(self, value: str, var_type: str) -> None:
        # No Value after =
        if value == "":
            message = "Expected string value"

            self._diagnostics.append(types.Diagnostic(
                    range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                    message=message,
                    severity=types.DiagnosticSeverity.Error,
                    source=self._source,
                )
            )

        # Wrong value after =
        elif not re.match(r'^".*"$', value):
            if self._function_return_type(value, var_type):
                return

            if value.startswith('"') or value.endswith('"'):
                if len(value) <= 1:
                    message = "Expected string value"
                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                            message=message,
                            severity=types.DiagnosticSeverity.Error,
                            source=self._source,
                        )
                    )


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
                        message = f"String {val.strip(chr(34))} missing quote at the end"
                        self._diagnostics.append(types.Diagnostic(
                                range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                                message=message,
                                severity=types.DiagnosticSeverity.Error,
                                source=self._source,
                            )
                        )
                        continue

                    if not val.startswith('"') and val.endswith('"'):
                        message = f"String {val.strip(chr(34))} missing quote at the start"
                        self._diagnostics.append(types.Diagnostic(
                                range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                                message=message,
                                severity=types.DiagnosticSeverity.Error,
                                source=self._source,
                            )
                        )
                        continue

                    if self._function_return_type(val, var_type):
                        continue

                    message = f"String {val} value must be in quotes"

                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                            message=message,
                            severity=types.DiagnosticSeverity.Error,
                            source=self._source,
                        )
                    )
            else:
                # Check if valid Var
                if value in self._user_vars:
                    return
                
                if value.startswith('"') and value.endswith('"'):
                    return

                if value.startswith('"') and not value.endswith('"'):
                    message = f"String {value.strip(chr(34))} missing quote at the end"
                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                            message=message,
                            severity=types.DiagnosticSeverity.Error,
                            source=self._source,
                        )
                    )
                    return

                if not value.startswith('"') and value.endswith('"'):
                    message = f"String {value.strip(chr(34))} missing quote at the start"
                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                            message=message,
                            severity=types.DiagnosticSeverity.Error,
                            source=self._source,
                        )
                    )
                    return

                if self._function_return_type(value, var_type):
                    return

                message = f"String {value} value must be in quotes"

                self._diagnostics.append(types.Diagnostic(
                        range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                        message=message,
                        severity=types.DiagnosticSeverity.Error,
                        source=self._source,
                    )
                )



    def _check_int_byte_variable_assignment(self, value: str, var_type: str) -> None:
        #Check for Valid int
        value_int: int
        if re.match(r"^-?\d+$", value):
            try:
                value_int: int = int(value)
            except ValueError:
                message = f"Value is not a {var_type}"

                self._diagnostics.append(types.Diagnostic(
                        range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                        message=message,
                        severity=types.DiagnosticSeverity.Error,
                        source=self._source,
                    )
                )
                return

            if var_type == VarTypeEnum._byte and value_int < 0:
                message = "Byte values can't have negative values"

                self._diagnostics.append(types.Diagnostic(
                        range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                        message=message,
                        severity=types.DiagnosticSeverity.Error,
                        source=self._source,
                    )
                )
                return

        # More than 1 Value
        elif not re.match(r"^-?\d+$", value):

            striped_values: list[str] = [val.strip() for val in re.split(r'\s*([+\*/-])\s+', value) 
                                         if val.strip() and val.strip() not in "+-/*"]
            if len(striped_values) >= 2:
                for val in striped_values:

                    if self._function_return_type(val, var_type):
                        continue

                    try:
                        value_int: int = int(val)
                    except ValueError:
                        if val == "":
                            message = f"Expected {var_type} Value"
                        else:
                            message = f"Value is not a {var_type}"

                        self._diagnostics.append(types.Diagnostic(
                                range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                                message=message,
                                severity=types.DiagnosticSeverity.Error,
                                source=self._source,
                            )
                        )
                        continue

                    if var_type == VarTypeEnum._byte and value_int < 0:
                        message = "Byte values can't have negative values"

                        self._diagnostics.append(types.Diagnostic(
                                range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                                message=message,
                                severity=types.DiagnosticSeverity.Error,
                                source=self._source,
                            )
                        )
                        continue

                    if isinstance(value_int, int):
                        continue

            else:        
                if self._function_return_type(value, var_type):
                    return

                try:
                    value_int: int = int(value)
                except ValueError:
                    if value == "":
                        message = f"Expected {var_type} Value"
                    else:
                        message = f"Value is not a {var_type}"

                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                            message=message,
                            severity=types.DiagnosticSeverity.Error,
                            source=self._source,
                        )
                    )
                    return

                if isinstance(value_int, int):
                    return

    def _check_float_double_variable_assignment(self, value: str, var_type: str) -> None:
        #Check for Valid int
        value_float: float
        if re.match(r"^-?(\d+\.\d+|\.\d+)$", value):
            try:
                value_float: float = float(value)
            except ValueError:
                message = f"Value is not a {var_type}"

                self._diagnostics.append(types.Diagnostic(
                        range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                        message=message,
                        severity=types.DiagnosticSeverity.Error,
                        source=self._source,
                    )
                )
                return

        # More than 1 Value
        elif not re.match(r"^-?(\d+\.\d+|\.\d+)$", value):

            striped_values: list[str] = [val.strip() for val in re.split(r'\s*([+\*/-])\s+', value) 
                                         if val.strip() and val.strip() not in "+-/*"]
            if len(striped_values) >= 2:
                for val in striped_values:
                    if self._function_return_type(val, var_type):
                        continue

                    try:
                        value_float: float = float(val)
                        continue
                    except ValueError:
                        if val == "":
                            message = f"Expected {var_type} value"
                        else:
                            message = f"Value is not a {var_type}"

                        self._diagnostics.append(types.Diagnostic(
                                range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                                message=message,
                                severity=types.DiagnosticSeverity.Error,
                                source=self._source,
                            )
                        )
                        continue

            else:        
                if self._function_return_type(value, var_type):
                    return

                try:
                    value_float: float = float(value)
                except ValueError:
                    if value == "":
                        message = f"Expected {var_type} value"
                    else:
                        message = f"Value is not a {var_type}"

                    self._diagnostics.append(types.Diagnostic(
                            range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                            message=message,
                            severity=types.DiagnosticSeverity.Error,
                            source=self._source,
                        )
                    )
                    return

                if isinstance(value_float, float):
                    return


    def _check_bool_variable_assignment(self, value: str) -> None:
        raise NotImplementedError
    

    def _check_string_array_variable_assignment(self, value: str) -> None:
        raise NotImplementedError
    

    def _check_int_array_variable_assignment(self, value: str) -> None:
        raise NotImplementedError


    def _check_float_array_variable_assignment(self, value: str) -> None:
        raise NotImplementedError
    

    def _check_double_array_variable_assignment(self, value: str) -> None:
        raise NotImplementedError
    

    def _check_byte_array_variable_assignment(self, value: str) -> None:
        raise NotImplementedError
    

    def _check_bool_arra_variable_assignment(self, value: str) -> None:
        raise NotImplementedError
