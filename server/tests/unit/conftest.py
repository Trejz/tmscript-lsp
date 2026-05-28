from pathlib import Path
import sys

import pytest

from src.server.diagnostics_rules import DiagnositcRules
from src.server.user_types.script_functions import ScriptFunctionHandler
from src.server.user_types.script_types import ScriptTypeHandler
from src.server.user_types.user_variables import UserDefinedVarialbes

SERVER_ROOT = Path(__file__).resolve().parents[2]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))


class TestDocument:
    def __init__(self, text: str) -> None:
        self.lines = text.splitlines()


@pytest.fixture
def diagnostics_rules() -> DiagnositcRules:
    type_handler = ScriptTypeHandler()
    function_handler = ScriptFunctionHandler()
    user_variables = UserDefinedVarialbes(type_handler)
    return DiagnositcRules(function_handler, user_variables, type_handler)


@pytest.fixture
def make_document():
    def _make_document(text: str) -> TestDocument:
        return TestDocument(text.strip("\n"))

    return _make_document
