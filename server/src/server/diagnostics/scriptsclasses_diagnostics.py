import re
from lsprotocol import types
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.server.user_types.script_methods import ScriptMethodHandler


class ScriptClassDiagnostics:
    def __init__(self,
                 source: str,
                 diag_pos_start,
                 diag_pos_end,
                 scriptmethodhandler,
                 line,
                 linenum, 
                 user_vars: dict[str, dict[str, str]] | None = None) -> None:

        self._diagnostics: list[types.Diagnostic] = []
        self._diag_pos_start = diag_pos_start
        self._diag_pos_end = diag_pos_end
        self._source = source
        self._scriptmethodhandler: ScriptMethodHandler = scriptmethodhandler
        self._line = line
        self._linenum = linenum
        self._user_vars: dict[str, dict[str, str]] = user_vars if user_vars is not None else {}

    def _add_diagnostic(self, message: str, severity=types.DiagnosticSeverity.Error):
        self._diagnostics.append(
            types.Diagnostic(
                range=types.Range(start=self._diag_pos_start, end=self._diag_pos_end),
                message=message,
                severity=severity,
                source=self._source,
            )
        )

    def check_class_constructor(self) -> list[types.Diagnostic] | None:
        script_classes = self._scriptmethodhandler.get_script_classes()
        if not script_classes:
            return None

        types_regex = "|".join(map(re.escape, script_classes))
        constructor_match = re.compile(rf"^\s*({types_regex})\s+(\w+)(?:\s*=\s*(.*))?$")
        regex_match = constructor_match.match(self._line)

        if not regex_match:
            return None

        class_type = regex_match.group(1)
        all_values: str | None = regex_match.group(3)

        constructors = script_classes.get(class_type, {}).get("constructors", [])
        expected_signatures: list[list[str]] = []
        for constructor in constructors:
            signature = constructor.get("types", []) if isinstance(constructor, dict) else []
            expected_signatures.append(self._normalize_constructor_types(signature))

        actual_values = self._split_values(all_values)
        actual_types = self._get_value_types(actual_values)
        args_len = len(actual_values)

        for expected_types in expected_signatures:
            if self._constructor_matches(expected_types, actual_types):
                return []

        if not expected_signatures:
            self._add_diagnostic(f'Class "{class_type}" has no constructor metadata')
            return self._diagnostics

        closest_signature = min(
            expected_signatures,
            key=lambda expected: self._constructor_distance(expected, actual_types),
        )

        mismatch_messages: list[str] = []
        if len(closest_signature) != args_len:
            mismatch_messages.append(
                f"expected {len(closest_signature)} arguments, got {args_len}"
            )

        for index, (expected, actual) in enumerate(zip(closest_signature, actual_types), start=1):
            if not self._type_matches(expected, actual):
                mismatch_messages.append(f"arg {index}: expected {expected}, got {actual}")

        if not mismatch_messages:
            mismatch_messages.append("constructor arguments do not match")

        signature_text = self._signature_to_text(class_type, closest_signature)
        self._add_diagnostic(
            f"Invalid constructor for {class_type}. Closest match: {signature_text}. "
            + "; ".join(mismatch_messages)
        )

        return self._diagnostics

    def _normalize_constructor_types(self, constructor_types: list[str]) -> list[str]:
        if len(constructor_types) == 1 and constructor_types[0] == "":
            return []
        return constructor_types

    def _split_values(self, all_values: str | None) -> list[str]:
        if all_values is None:
            return []

        all_values = all_values.strip()
        if all_values == "":
            return []

        values: list[str] = []
        current: list[str] = []
        in_string = False
        escape_next = False
        brace_depth = 0
        bracket_depth = 0
        paren_depth = 0

        for char in all_values:
            if escape_next:
                current.append(char)
                escape_next = False
                continue

            if char == "\\" and in_string:
                current.append(char)
                escape_next = True
                continue

            if char == '"':
                in_string = not in_string
                current.append(char)
                continue

            if not in_string:
                if char == "{":
                    brace_depth += 1
                elif char == "}":
                    brace_depth = max(0, brace_depth - 1)
                elif char == "[":
                    bracket_depth += 1
                elif char == "]":
                    bracket_depth = max(0, bracket_depth - 1)
                elif char == "(":
                    paren_depth += 1
                elif char == ")":
                    paren_depth = max(0, paren_depth - 1)

                if (
                    char == ","
                    and brace_depth == 0
                    and bracket_depth == 0
                    and paren_depth == 0
                ):
                    values.append("".join(current).strip())
                    current = []
                    continue

            current.append(char)

        values.append("".join(current).strip())
        return values

    def _constructor_matches(self, expected_types: list[str], actual_types: list[str]) -> bool:
        if len(expected_types) != len(actual_types):
            return False

        for expected, actual in zip(expected_types, actual_types):
            if not self._type_matches(expected, actual):
                return False

        return True

    def _constructor_distance(self, expected_types: list[str], actual_types: list[str]) -> int:
        distance = abs(len(expected_types) - len(actual_types)) * 4
        for expected, actual in zip(expected_types, actual_types):
            if self._type_matches(expected, actual):
                continue
            if actual == "unknown":
                distance += 2
            else:
                distance += 3

        return distance

    def _type_matches(self, expected: str, actual: str) -> bool:
        if expected == actual:
            return True

        # int literals are valid for float parameters.
        if expected == "float" and actual == "int":
            return True

        if expected == "float[]" and actual == "int[]":
            return True

        return False

    def _signature_to_text(self, class_type: str, signature: list[str]) -> str:
        if not signature:
            return f"{class_type}()"
        return f"{class_type}({', '.join(signature)})"

    def _get_value_types(self, all_values: list[str]) -> list[str]:
        value_types: list[str] = []

        for value in all_values:
            value_types.append(self._get_single_value_type(value.strip()))

        return value_types

    def _get_single_value_type(self, value: str) -> str:
        if value == "":
            return "None"

        if value in self._user_vars:
            return self._user_vars[value].get("var_type", "unknown")

        if value in {"true", "false"}:
            return "bool"

        if re.fullmatch(r'"(?:\\.|[^"])*"', value):
            return "string"

        if re.fullmatch(r"-?\d+", value):
            return "int"

        if re.fullmatch(r"-?(?:\d+\.\d+|\.\d+)", value):
            return "float"

        if value.startswith("{") and value.endswith("}"):
            return self._get_array_value_type(value)

        return "unknown"

    def _get_array_value_type(self, value: str) -> str:
        content = value[1:-1].strip()
        if content == "":
            return "unknown[]"

        elements = self._split_values(content)
        element_types = [self._get_single_value_type(element) for element in elements]

        if all(element_type == "string" for element_type in element_types):
            return "string[]"

        if all(element_type == "bool" for element_type in element_types):
            return "bool[]"

        if all(element_type in {"int", "float"} for element_type in element_types):
            if any(element_type == "float" for element_type in element_types):
                return "float[]"
            return "int[]"

        return "unknown[]"



