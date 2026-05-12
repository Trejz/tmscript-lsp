from pygls.lsp.server import LanguageServer
from lsprotocol import types

from src.server.user_types.keywords import KeywordHandler
from src.server.user_types.script_functions import ScriptFunctionHandler
from src.server.user_types.script_types import ScriptTypeHandler
from src.server.completion_rules import CompletionRules
from src.server.user_types.user_variables import UserDefinedVarialbes
from src.server.diagnostics_rules import DiagnositcRules

server = LanguageServer("tmscript-lsp", "v0.0.1")

# Init 
keywordhandler = KeywordHandler()
scriptfunctionhandler = ScriptFunctionHandler()
scripttypehandler = ScriptTypeHandler()
userdefinedvariables = UserDefinedVarialbes(scripttypehandler)

completion_rules = CompletionRules(scripttypehandler, scriptfunctionhandler, userdefinedvariables)
diagnostics_rules = DiagnositcRules(scriptfunctionhandler, userdefinedvariables)

# On Completion Request
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
    items += userdefinedvariables.get_all_user_defined_variables(document)

    return types.CompletionList(
        is_incomplete=False,
        items=items,
    )


# On Change Event
@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: types.DidChangeTextDocumentParams):

    document = ls.workspace.get_text_document(params.text_document.uri)

    diagnostics = diagnostics_rules.var_value_assignmenet(document)

    ls.text_document_publish_diagnostics(
        types.PublishDiagnosticsParams(
            uri=document.uri,
            version=document.version,
            diagnostics=diagnostics,
        )
    )


# On Open Event
@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: types.DidOpenTextDocumentParams):

    document = ls.workspace.get_text_document(params.text_document.uri)

    diagnostics = diagnostics_rules.var_value_assignmenet(document)

    ls.text_document_publish_diagnostics(
        types.PublishDiagnosticsParams(
            uri=document.uri,
            version=document.version,
            diagnostics=diagnostics,
        )
    )
