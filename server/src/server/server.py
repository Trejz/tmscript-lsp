from pygls.lsp.server import LanguageServer
from lsprotocol import types

from src.server.user_types.keywords import KeywordHandler
from src.server.user_types.script_functions import ScriptFunctionHandler
from src.server.user_types.script_types import ScriptTypeHandler
from src.server.completion_rules import CompletionRules
from src.server.user_types.user_variables import UserDefinedVarialbes

server = LanguageServer("tmscript-lsp", "v0.0.1")

# Init 
keywordhandler = KeywordHandler()
scriptfunctionhandler = ScriptFunctionHandler()
scripttypehandler = ScriptTypeHandler()
userdefinedvariables = UserDefinedVarialbes()

completion_rules = CompletionRules(scripttypehandler, scriptfunctionhandler, userdefinedvariables)

@server.feature(types.TEXT_DOCUMENT_COMPLETION)
def completions(ls: LanguageServer, params: types.CompletionParams):

    document = ls.workspace.get_text_document(params.text_document.uri)

    line: str = document.lines[params.position.line]
    before_cursor: str = line[:params.position.character]

    rules = [
            completion_rules.rule_return_variable_type
            ]

    for rule in rules:
        result = rule(before_cursor, document)
        if result:
            return result

    # Fallback Completions
    items = keywordhandler.get_keywords_completion()
    items += scriptfunctionhandler.get_script_functions_completion()
    items += scripttypehandler.get_script_types_completion()

    return types.CompletionList(
        is_incomplete=False,
        items=items,
    )


