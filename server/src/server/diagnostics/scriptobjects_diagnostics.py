import re
from lsprotocol import types
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.server.user_types.script_methods import ScriptMethodHandler


class ScriptObjectsDiagnostics:
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
