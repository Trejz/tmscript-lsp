import re
from lsprotocol import types
from typing import TYPE_CHECKING

from src.server.enums.enums import VarTypeEnum
from src.server.diagnostics.scriptsclasses_diagnostics import ScriptClassDiagnostics

if TYPE_CHECKING:
    from src.server.user_types.script_functions import ScriptFunctionHandler
    from src.server.user_types.user_variables import UserDefinedVarialbes
    from src.server.user_types.script_types import ScriptTypeHandler
    from src.server.user_types.script_methods import ScriptMethodHandler

class DiagnositcRules:
    def __init__(self, 
                 scriptfunctionhandler: "ScriptFunctionHandler", 
                 userdefinedvariables: "UserDefinedVarialbes",
                 scripttypehandler: "ScriptTypeHandler",
                 scriptmethodhandler: "ScriptMethodHandler") -> None:

        self._scriptfunctionhandler: "ScriptFunctionHandler" = scriptfunctionhandler
        self._userdefinedvariables: "UserDefinedVarialbes" = userdefinedvariables
        self._scripttypehandler: "ScriptTypeHandler" = scripttypehandler
        self._scriptmethodhandler: "ScriptMethodHandler" = scriptmethodhandler
        
        self._source: str = "tmscript-lsp"
        self._diagnostics: list[types.Diagnostic] = []
        self._user_vars: dict[str,dict[str,str]] = {}
        self._diag_pos_start: types.Position = types.Position(line=0,character=0)
        self._diag_pos_end: types.Position = types.Position(line=0,character=0)
        self._document = None


    def _add_diagnostic(self, message: str, severity = types.DiagnosticSeverity.Error):
        self._diagnostics.append(types.Diagnostic(
                range=types.Range(start=self._diag_pos_start,end=self._diag_pos_end),
                message=message,
                severity=severity,
                source=self._source,
            )
        )


    def var_value_assignmenet(self, document) -> list[types.Diagnostic]:
        self._diagnostics: list[types.Diagnostic] = []
        self._user_vars = self._userdefinedvariables.collect_variables(document)
        self._document = document

        #regex_var_declaration = re.compile(r"^\s*(?:(\w+(?:\[])?)\s+)?(\w+)\s*(?:=\s*(.*))?$")
        types_regex = "|".join(map(re.escape, self._scripttypehandler.get_script_types()))

        definition_match = re.compile(rf"^\s*({types_regex})\s+(\w+)(?:\s*=\s*(.*))?$")
        assignment_match = re.compile(r"^\s*(\w+)\s*=\s*(.*)$")

        for line_num, line in enumerate(document.lines):
            line = line.lstrip("\ufeff").rstrip("\r\n")

            eq_pos = line.find("=") if "=" in line else len(line.rstrip()) - 1
            self._diag_pos_start = types.Position(line=line_num,character=max(0, eq_pos))
            self._diag_pos_end = types.Position(line=line_num, character=len(line))

            script_class_diagnostics = ScriptClassDiagnostics(
                source=self._source,
                diag_pos_start=self._diag_pos_start,
                diag_pos_end=self._diag_pos_end,
                scriptmethodhandler=self._scriptmethodhandler,
                line=line,
                linenum=line_num,
                user_vars=self._user_vars,
            )
            class_constructor_diagnostics = script_class_diagnostics.check_class_constructor()
            if class_constructor_diagnostics is not None:
                self._diagnostics.extend(class_constructor_diagnostics)
                continue

            regex_defmatch = definition_match.match(line)
            regex_assignmatch = assignment_match.match(line)
            
            # Skip if no match
            if regex_defmatch:
                var_type: str | None = regex_defmatch.group(1)
                var_name: str | None = regex_defmatch.group(2)
                var_value: str | None = regex_defmatch.group(3)
            elif regex_assignmatch:
                var_type: str | None = None
                var_name: str | None = regex_assignmatch.group(1)
                var_value: str | None = regex_assignmatch.group(2)
            else:
                continue


            # Check if type Keyword is correct
            if var_type is not None and var_name is not None: 
                if (var_type not in self._scripttypehandler.get_script_types() and
                    var_type not in self._scriptmethodhandler.get_script_methods()):
                    message: str = f"""Type Keyword "{var_type}" is not valid""" 
                    self._add_diagnostic(message)
                    continue

            # Check if Variable Defined
            if var_type is None:
                var_name = var_name.strip() if var_name is not None else var_name
                if var_name not in self._user_vars:
                    message = "Variable not defined"
                    self._add_diagnostic(message)
                    continue
            
            if var_value is None:
                continue

            # Match to var_type
            match var_type:
                case VarTypeEnum.string_:
                    value = var_value.strip()
                    self._check_string_variable_assignment(value=value, var_type=var_type)

                case VarTypeEnum.int_ | VarTypeEnum.byte_:
                    value = var_value.strip()
                    self._check_int_byte_variable_assignment(value=value,var_type=var_type)

                case VarTypeEnum.float_ | VarTypeEnum.double_:
                    value = var_value.strip()
                    self._check_float_double_variable_assignment(value=value, var_type=var_type)

                case VarTypeEnum.bool_:
                    value = var_value.strip()
                    self._check_bool_variable_assignment(value=value)

                case VarTypeEnum.string_array_:
                    value = var_value.strip()
                    self._check_string_array_variable_assignment(value=value)

                case VarTypeEnum.int_array_ | VarTypeEnum.byte_array_:
                    value = var_value.strip()
                    self._check_int_byte_array_variable_assignment(value=value, var_type=var_type)

                case VarTypeEnum.float_array_ | VarTypeEnum.double_array_:
                    value = var_value.strip()
                    self._check_float_double_array_variable_assignment(value=value, var_type=var_type)

                case VarTypeEnum.bool_array_:
                    value = var_value.strip()
                    self._check_bool_array_variable_assignment(value=value)

        return self._diagnostics


    def _function_return_type(self, value: str, var_type: str) -> bool:
        """Return True when Function returns correct type"""
        regex_func = re.compile(r"^(\w+)\s*\((.*)\)$")
        func_match = regex_func.match(value)

        if func_match:
            valid, return_types = self._scriptfunctionhandler.get_valid_return_function(func_match.group(1),var_type)
            if valid:
                return True

            message = f"Invalid type. Function returns: {return_types}"
            self._add_diagnostic(message)
            return True
        return False


    def _attribute_return_type(self, var_type: str, value: str) -> bool:
        """Return True when Attribute return correct type"""
        valid_return: bool = self._scriptmethodhandler.get_class_attribute_return_type(self._document,
                                                                  var_type,
                                                                  value)
        if valid_return:
            return True
        return False


    def _check_string_variable_assignment(self, value: str, var_type: str) -> None:
        # No Value after =
        if value == "":
            message = "Expected string value"
            self._add_diagnostic(message)

        # Wrong value after =
        elif not re.match(r'^".*"$', value):
            if value.startswith('"') or value.endswith('"'):
                if len(value) <= 1:
                    message = "Expected string value"
                    self._add_diagnostic(message)

            # Check If correct String Format
            striped_values: list[str] = [val.strip() for val in value.split("+")]
            if len(striped_values) >= 2:
                for val in striped_values:
                    if self._function_return_type(val, var_type):
                        continue
                    if self._attribute_return_type(var_type,val):
                        continue

                    # Check if valid Var
                    if val in self._user_vars:
                        continue
                    
                    if val.startswith('"') and val.endswith('"'):
                        continue

                    if val.startswith('"') and not val.endswith('"'):
                        message = f"String {val.strip(chr(34))} missing quote at the end"
                        self._add_diagnostic(message)
                        continue

                    if not val.startswith('"') and val.endswith('"'):
                        message = f"String {val.strip(chr(34))} missing quote at the start"
                        self._add_diagnostic(message)
                        continue

                    if self._function_return_type(val, var_type):
                        continue

                    message = f"String {val} value must be in quotes"
                    self._add_diagnostic(message)
            else:
                # Check if valid Var
                if self._function_return_type(value, var_type):
                    return
                if self._attribute_return_type(var_type,value):
                    return

                if value in self._user_vars:
                    return
                
                if value.startswith('"') and value.endswith('"'):
                    return

                if value.startswith('"') and not value.endswith('"'):
                    message = f"String {value.strip(chr(34))} missing quote at the end"
                    self._add_diagnostic(message)
                    return

                if not value.startswith('"') and value.endswith('"'):
                    message = f"String {value.strip(chr(34))} missing quote at the start"
                    self._add_diagnostic(message)
                    return

                if self._function_return_type(value, var_type):
                    return

                message = f"String {value} value must be in quotes"
                self._add_diagnostic(message)

#ToDo: Add diagnostics for class attributes
    def _check_int_byte_variable_assignment(self, value: str, var_type: str) -> None:
        #Check for Valid int
        value_int: int
        if re.match(r"^-?\d+$", value):
            try:
                value_int: int = int(value)
            except ValueError:
                message = f"Value is not a {var_type}"

                self._add_diagnostic(message)
                return

            if var_type == VarTypeEnum.byte_ and value_int < 0:
                message = "Byte values can't have negative values"

                self._add_diagnostic(message)
                return

        # More than 1 Value
        elif not re.match(r"^-?\d+$", value):
            striped_values: list[str] = [val.strip() for val in re.split(r'\s*([+*/-])\s+', value)
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

                        self._add_diagnostic(message)
                        continue

                    if var_type == VarTypeEnum.byte_ and value_int < 0:
                        message = "Byte values can't have negative values"

                        self._add_diagnostic(message)
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

                    self._add_diagnostic(message)
                    return

                if isinstance(value_int, int):
                    return


    def _check_float_double_variable_assignment(self, value: str, var_type: str) -> None:
        #Check for Valid int
        value_float: float
        if re.match(r"^-?(\d+\.\d+|\.\d+)$", value):
            try:
                value_float: float = float(value)
                isinstance(value_float, float)
            except ValueError:
                message = f"Value is not a {var_type}"

                self._add_diagnostic(message)
                return

        # More than 1 Value
        elif not re.match(r"^-?(\d+\.\d+|\.\d+)$", value):

            striped_values: list[str] = [val.strip() for val in re.split(r'\s*([+*/-])\s+', value)
                                         if val.strip() and val.strip() not in "+-/*"]
            if len(striped_values) >= 2:
                for val in striped_values:
                    if self._function_return_type(val, var_type):
                        continue

                    try:
                        value_float: float = float(val)
                        isinstance(value_float, float)
                        continue
                    except ValueError:
                        if val == "":
                            message = f"Expected {var_type} value"
                        else:
                            message = f"Value is not a {var_type}"

                        self._add_diagnostic(message)
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

                    self._add_diagnostic(message)
                    return

                if isinstance(value_float, float):
                    return


    def _check_bool_variable_assignment(self, value: str) -> None:
        if value.strip() == "true" or value.strip() == "false":
            return
        else:
            message = "Value is not a bool"

            self._add_diagnostic(message)
            return
    

    #Array Checks
    def _check_array_brackets(self, value, var_type: str) -> bool:
        """Returns True if diagnositc is present"""

        if value == "":
            message = f"Expected {var_type} Array Value"
            self._add_diagnostic(message)
            return True

        if value.startswith("{") and not value.endswith("}"):
            message = "Missing } at the end"
            self._add_diagnostic(message)
            return True
        
        if not value.startswith("{") and value.endswith("}"):
            message = "Missing } at the start"
            self._add_diagnostic(message)
            return True
        
        return False


    def _check_string_array_variable_assignment(self, value: str) -> None:
        stringarray_regex = re.compile(r'^"[^"]*"$')
        if value.startswith("{") and value.endswith("}"):
            content = value[1:-1].strip()
            if not content:
                return

            array_values = [v.strip() for v in content.split(",")]
            for i, val in enumerate(array_values):
                if not stringarray_regex.fullmatch(val):
                    message = f"Value at index {i} is not a string"
                    self._add_diagnostic(message)
                    return

            return
        
        if self._check_array_brackets(value=value, var_type="string"):
            return

        message = "Value is not a string Array"
        self._add_diagnostic(message)


    def _check_int_byte_array_variable_assignment(self, value: str, var_type: str) -> None:
        int_regex = re.compile(r"^-?\d+$")
        var_type = var_type.removesuffix("[]")
        if value.startswith("{") and value.endswith("}"):
            content = value[1:-1].strip()
            if not content:
                return

            array_values = [v.strip() for v in content.split(",")]
            for i, val in enumerate(array_values):
                if not int_regex.fullmatch(val):
                    try:
                        value_int: int = int(val)
                    except ValueError:
                        message = f"Value at index {i} is not a {var_type}"
                        self._add_diagnostic(message)
                        return

                    if var_type == VarTypeEnum.byte_ and value_int < 0:
                        message = "Byte values can't have negative values"

                        self._add_diagnostic(message)
                        return

                    message = f"Value is not a {var_type}"
                    self._add_diagnostic(message)
                    return
            return
        
        if self._check_array_brackets(value=value, var_type=var_type):
            return
        
        message = f"Value is not a {var_type} Array"
        self._add_diagnostic(message)


    def _check_float_double_array_variable_assignment(self, value: str, var_type: str) -> None:
        float_regex = re.compile(r"^-?(\d+\.\d+|\.\d+)$")
        var_type = var_type.removesuffix("[]")
        if value.startswith("{") and value.endswith("}"):
            content = value[1:-1].strip()
            if not content:
                return

            array_values = [v.strip() for v in content.split(",")]
            for i, val in enumerate(array_values):
                if not float_regex.fullmatch(val):
                    try:
                        float(val)
                    except ValueError:
                        message = f"Value at index {i} is not a {var_type}"
                        self._add_diagnostic(message)
                        return

                    message = f"Value is not a {var_type}"
                    self._add_diagnostic(message)
                    return          
            return
        
        if self._check_array_brackets(value=value, var_type=var_type):
            return
        
        message = f"Value is not a {var_type} Array"
        self._add_diagnostic(message)
    

    def _check_bool_array_variable_assignment(self, value: str) -> None:
        if value.startswith("{") and value.endswith("}"):
            content = value[1:-1].strip()
            if not content:
                return

            array_values = [v.strip() for v in content.split(",")]
            for i, val in enumerate(array_values):
                if val == "true" or val == "false":
                    continue
                else:
                    message = f"Value at index {i} is not a bool"
                    self._add_diagnostic(message)
                    return
            return
        
        if self._check_array_brackets(value=value, var_type="bool"):
            return

        message = "Value is not a bool Array"
        self._add_diagnostic(message)

