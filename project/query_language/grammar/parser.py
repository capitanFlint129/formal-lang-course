from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from pydot import Dot, Node, Edge

from project.query_language.grammar.QueryLanguageLexer import QueryLanguageLexer
from project.query_language.grammar.QueryLanguageParser import QueryLanguageParser


class CountErrorListener(ErrorListener):
    def __init__(self):
        self.errors_number = 0

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors_number += 1

    def reportAmbiguity(
        self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs
    ):
        self.errors_number += 1

    def reportAttemptingFullContext(
        self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs
    ):
        self.errors_number += 1

    def reportContextSensitivity(
        self, recognizer, dfa, startIndex, stopIndex, prediction, configs
    ):
        self.errors_number += 1


class DotGeneratorListener(ParseTreeListener):
    def __init__(self):
        self.tree = Dot("parsing_tree", graph_type="graph")
        self.path_to_root = []
        self.new_node_id = 0

    def enterEveryRule(self, ctx: ParserRuleContext):
        current_node = self._new_node(QueryLanguageParser.ruleNames[ctx.getRuleIndex()])
        self.tree.add_node(current_node)
        if self.path_to_root:
            self.tree.add_edge(
                Edge(self.path_to_root[-1].get_name(), current_node.get_name())
            )
        self.path_to_root.append(current_node)

    def exitEveryRule(self, ctx: ParserRuleContext):
        self.path_to_root = self.path_to_root[:-1]

    def visitTerminal(self, node: TerminalNode):
        current_node = self._new_node(node.getText())
        self.tree.add_node(current_node)
        if self.path_to_root:
            self.tree.add_edge(
                Edge(self.path_to_root[-1].get_name(), current_node.get_name())
            )

    def _new_node(self, rule_name):
        # escape special characters
        rule_name = rule_name.translate(str.maketrans({"\\": r"\\"}))
        node = Node(self.new_node_id, label=rule_name)
        self.new_node_id += 1
        return node


def check_script_correct(script: str) -> bool:
    """
    Checks that input program is correct query language program

    Parameters
    ----------
    script :
        Input program on query language

    Returns
    ----------
    result :
        Returns True if and only if input is accepted by query language grammar
    """
    return _check_script(InputStream(script))


def check_script_file_correct(path: str) -> bool:
    """
    Checks that input program is correct query language program

    Parameters
    ----------
    path :
        File with input program on query language

    Returns
    ----------
    result :
        Returns True if and only if input is accepted by query language grammar
    """
    return _check_script(FileStream(path))


def _check_script(input_stream):
    lexer = QueryLanguageLexer(input_stream)
    lexer_error_listener = CountErrorListener()
    lexer.addErrorListener(lexer_error_listener)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    parser.prog()
    errors = parser.getNumberOfSyntaxErrors()
    return errors == 0 and lexer_error_listener.errors_number == 0


def export_script_to_dot(script: str, result_path: str):
    """
    Exports parsing tree of input program to dot format

    Parameters
    ----------
    script :
        Input program on query language
    result_path :
        The path to the file where you want to write the result

    Returns
    ----------
    result :
        Returns True if and only if input is accepted by query language grammar
    """
    _export_to_dot(InputStream(script), result_path)


def export_script_file_to_dot(script_path: str, result_path: str):
    """
    Exports parsing tree of input program to dot format

    Parameters
    ----------
    script_path :
        The path to the file with input program on query language
    result_path :
        The path to the file where you want to write the result

    Returns
    ----------
    result :
        Returns True if and only if input is accepted by query language grammar
    """
    _export_to_dot(FileStream(script_path), result_path)


def _export_to_dot(input_stream, result_path: str):
    lexer = QueryLanguageLexer(input_stream)
    lexer_error_listener = CountErrorListener()
    lexer.addErrorListener(lexer_error_listener)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    errors = parser.getNumberOfSyntaxErrors()
    if errors != 0 or lexer_error_listener.errors_number != 0:
        raise Exception(
            f"Lexer errors - {lexer_error_listener.errors_number}, parser errors - {errors}"
        )
    listener = DotGeneratorListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    listener.tree.write(result_path)
