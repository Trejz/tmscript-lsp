from src.server.user_types.script_types import ScriptTypeHandler
from src.server.user_types.user_variables import UserDefinedVarialbes
from src.server.completion_rules import CompletionRules
from src.server.user_types.script_functions import ScriptFunctionHandler
from src.server.user_types.keywords import KeywordHandler
from pprint import pprint

class TestDocument:
	def __init__(self, text: str) -> None:
		self.lines = text.splitlines()


def debug_completion_full_flow(before_cursor: str, document_text: str) -> None:
	"""Debug FULL completion flow like the actual server does."""
	handler = ScriptTypeHandler()
	script_func_handler = ScriptFunctionHandler()
	user_vars = UserDefinedVarialbes(handler)
	keywordhandler = KeywordHandler()
	document = TestDocument(document_text)
	
	completion_rules = CompletionRules(handler, script_func_handler, user_vars)
	
	print(f"\n=== Full Completion Flow Debug ===")
	print(f"Document:\n{document_text}\n")
	print(f"before_cursor: '{before_cursor}'")
	print(f"Collected variables: {user_vars.collect_variables(document)}\n")
	
	# Step 1: Try rule
	rule_result = completion_rules.rule_return_variable_type(before_cursor, document)
	
	if rule_result:
		print(f"Rule returned result with {len(rule_result.items)} items:")
		for item in rule_result.items:  # Show first 10
			print(f"  - {item.label} (type: {item.detail})")
		return
	
	# Step 2: Fallback (like server does)
	print("Rule returned None, using fallback completions:")
	items = keywordhandler.get_keywords_completion()
	print(f"  Keywords: {len(items)} items")
	items += script_func_handler.get_script_functions_completion()
	print(f"  + Functions: {len(script_func_handler.get_script_functions_completion())} items")
	items += handler.get_script_types_completion()
	print(f"  + Types: {len(handler.get_script_types_completion())} items")
	items += user_vars.get_all_user_defined_variables(document)
	print(f"  + User variables: {len(user_vars.get_all_user_defined_variables(document))} items")
	
	print(f"\nFallback total: {len(items)} items")
	print("User variables in fallback:")
	for item in user_vars.get_all_user_defined_variables(document):
		print(f"  - {item.label} (type: {item.detail})")
	print("\n[Server would return fallback]")


document_text = """
string test
string test2 = String_ToUpper() + ""
""".strip()

before_cursor = "string test2 = "

debug_completion_full_flow(before_cursor, document_text)