import sys

from antlr4 import *

from project.query_language.grammar.QueryLanguageLexer import QueryLanguageLexer
from project.query_language.grammar.QueryLanguageParser import QueryLanguageParser
from project.query_language.grammar.parser import (
    check_script_file_correct,
    check_script_correct,
)
from project.query_language.interpreter.interpret_visitor import InterpretVisitor


class Interpreter:
    def __init__(self, file=None):
        if file is None:
            self.file = sys.stdout
        else:
            self.file = file

    def execute_from_path(self, path: str):
        if not check_script_file_correct(path):
            return
        self._interpret_stream(FileStream(path))

    def execute_script(self, script: str):
        if not check_script_correct(script):
            return
        self._interpret_stream(InputStream(script))

    def _interpret_stream(self, input_stream):
        lexer = QueryLanguageLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = QueryLanguageParser(stream)
        tree = parser.prog()
        visitor = InterpretVisitor(self.file)
        try:
            visitor.visit(tree)
        except Exception as e:
            raise Exception(f"Statement - {visitor.statement_count}: {e}")
