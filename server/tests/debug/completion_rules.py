from src.server.user_types.script_types import ScriptTypeHandler
from src.server.user_types.user_variables import UserDefinedVarialbes
from src.server.user_types.script_functions import ScriptFunctionHandler
from src.server.user_types.keywords import KeywordHandler
from src.server.user_types.script_methods import ScriptMethodHandler
from src.server.completion_rules import CompletionRules


class TestDocument:
    def __init__(self, text: str) -> None:
        self.lines = text.splitlines()


def debug_completions(before_cursor: str, document_text: str) -> None:
    """
    Mirrors the full server completion flow and prints every item that would
    be returned for the given cursor position.

    Parameters
    ----------
    before_cursor  : text on the current line up to (not including) the cursor
    document_text  : full content of the open document
    """
    handler = ScriptTypeHandler()
    script_func_handler = ScriptFunctionHandler()
    user_vars = UserDefinedVarialbes(handler)
    keyword_handler = KeywordHandler()
    scriptmethod_handler = ScriptMethodHandler()

    completion_rules = CompletionRules(
        handler, script_func_handler, user_vars, scriptmethod_handler
    )
    document = TestDocument(document_text)

    print("\n" + "=" * 60)
    print(f"Document:\n{document_text}")
    print(f"\nbefore_cursor : '{before_cursor}'")
    print("=" * 60)

    rules = [
        ("rule_return_variable_type",          completion_rules.rule_return_variable_type),
        ("rule_scriptclass_method_completions", completion_rules.rule_scriptclass_method_completions),
    ]

    for rule_name, rule_fn in rules:
        result = rule_fn(before_cursor, document)
        if result:
            print(f"\n[MATCHED RULE] {rule_name}")
            print(f"  {len(result.items)} completion item(s):\n")
            for item in result.items:
                detail = getattr(item, "detail", "")
                print(f"  {item.label:<40} detail={detail}")
            return

    # --- Fallback (same order as server.py) ---
    print("\n[NO RULE MATCHED] Fallback completions:\n")

    sections = [
        ("Keywords",       keyword_handler.get_keywords_completion()),
        ("Functions",      script_func_handler.get_script_functions_completion()),
        ("Types",          handler.get_script_types_completion()),
        ("User variables", user_vars.get_all_user_defined_variables(document)),
        ("Script classes", scriptmethod_handler.get_scriptclass_completions()),
    ]

    total = 0
    for section_name, items in sections:
        print(f"  [{section_name}]  {len(items)} item(s)")
        for item in items:
            detail = getattr(item, "detail", "")
            print(f"    {item.label:<40} detail={detail}")
        total += len(items)

    print(f"\n  Total: {total} item(s)")


# ---------------------------------------------------------------------------
# Edit these two variables and run the file to see what completions appear.
# ---------------------------------------------------------------------------

DOCUMENT_TEXT = """
MDesicion test = "test"
test.
""".strip()

BEFORE_CURSOR = "test."

debug_completions(BEFORE_CURSOR, DOCUMENT_TEXT)
