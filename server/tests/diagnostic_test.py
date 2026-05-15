from src.server.user_types.script_types import ScriptTypeHandler
from src.server.user_types.user_variables import UserDefinedVarialbes
from src.server.user_types.script_functions import ScriptFunctionHandler
from src.server.diagnostics_rules import DiagnositcRules


class TestDocument:
	def __init__(self, text: str) -> None:
		self.lines = text.splitlines()


def debug_diagnostics(document_text: str) -> None:
	"""Debug diagnostics for given document text."""
	handler = ScriptTypeHandler()
	script_func_handler = ScriptFunctionHandler()
	user_vars = UserDefinedVarialbes(handler)
	document = TestDocument(document_text)
	
	diagnostics_rules = DiagnositcRules(script_func_handler, user_vars, handler)
	
	print(f"\n=== Diagnostics Debug ===")
	print(f"Document:\n{document_text}\n")
	print(f"Collected variables: {user_vars.collect_variables(document)}\n")
	
	diagnostics = diagnostics_rules.var_value_assignmenet(document)
	
	if diagnostics:
		print(f"Diagnostics found ({len(diagnostics)} total):")
		for diag in diagnostics:
			print(f"  Line {diag.range.start.line}: {diag.message} (severity: {diag.severity})")
	else:
		print("No diagnostics (valid)")


# ============ EDIT THIS SECTION TO DEBUG ============
document_text = """
int test = File_Length()
""".strip()

debug_diagnostics(document_text)
# ====================================================
