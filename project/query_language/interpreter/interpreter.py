import sys
import typing

from antlr4 import *

from project.automata import get_nondeterministic_automata_from_graph
from project.graph_utils import load_graph_from_dot
from project.query_language.grammar.QueryLanguageLexer import QueryLanguageLexer
from project.query_language.grammar.QueryLanguageParser import QueryLanguageParser
from project.query_language.grammar.QueryLanguageVisitor import QueryLanguageVisitor
from project.query_language.grammar.parser import check_script_file_correct
from project.query_language.interpreter.types import *


class Interpreter:
    def execute_from_path(self, path: str):
        if not check_script_file_correct(path):
            return
        input_stream = FileStream(path)
        lexer = QueryLanguageLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = QueryLanguageParser(stream)
        tree = parser.prog()
        visitor = InterpretVisitor()
        visitor.visit(tree)


class Expression:
    def __init__(self, value: typing.Any, expr_type: Type):
        self.value = value
        self.type = expr_type

    def __str__(self):
        return str(self.value)


class InterpretVisitor(QueryLanguageVisitor):
    def __init__(self, file=sys.stdout):
        self.vars_dict: dict[str, Expression] = {}
        self.file = file

    def visitDeclaration(self, ctx: QueryLanguageParser.DeclarationContext):
        var_name = ctx.children[0].getText()
        if var_name in self.vars_dict:
            raise Exception("Redeclaring a variable")
        expr = self.visit(ctx.children[2])
        self.vars_dict[var_name] = expr

    def visitPrint(self, ctx: QueryLanguageParser.PrintContext):
        expr = self.visit(ctx.children[1])
        self.file.write(str(expr))
        return self.visitChildren(ctx)

    def visitName(self, ctx: QueryLanguageParser.NameContext):
        var_name = ctx.getText()
        if var_name in self.vars_dict:
            raise Exception("Unknown name")
        return self.vars_dict[var_name]

    def visitString(self, ctx: QueryLanguageParser.StringContext):
        return Expression(ctx.getText(), StringType())

    def visitInteger(self, ctx: QueryLanguageParser.IntegerContext):
        return Expression(int(ctx.getText()), IntType())

    def visitBool(self, ctx: QueryLanguageParser.BoolContext):
        return Expression(ctx.getText() == str(True), BoolType())

    def visitVal(self, ctx: QueryLanguageParser.ValContext):
        return self.visitChildren(ctx)

    def visitSetStart(self, ctx: QueryLanguageParser.SetStartContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#setFinal.
    def visitSetFinal(self, ctx: QueryLanguageParser.SetFinalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#addStart.
    def visitAddStart(self, ctx: QueryLanguageParser.AddStartContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#addFinal.
    def visitAddFinal(self, ctx: QueryLanguageParser.AddFinalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#getStart.
    def visitGetStart(self, ctx: QueryLanguageParser.GetStartContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#getFinal.
    def visitGetFinal(self, ctx: QueryLanguageParser.GetFinalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#getReachable.
    def visitGetReachable(self, ctx: QueryLanguageParser.GetReachableContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#getVertices.
    def visitGetVertices(self, ctx: QueryLanguageParser.GetVerticesContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#getEdges.
    def visitGetEdges(self, ctx: QueryLanguageParser.GetEdgesContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#map.
    def visitMap(self, ctx: QueryLanguageParser.MapContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#filter.
    def visitFilter(self, ctx: QueryLanguageParser.FilterContext):
        return self.visitChildren(ctx)

    def visitLoad(self, ctx: QueryLanguageParser.LoadContext):
        path = ctx.children[1].getText()
        graph = load_graph_from_dot(path)
        fa = get_nondeterministic_automata_from_graph(graph)
        return Expression(fa, FAType())

    # Visit a parse tree produced by QueryLanguageParser#intersect.
    def visitIntersect(self, ctx: QueryLanguageParser.IntersectContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#concat.
    def visitConcat(self, ctx: QueryLanguageParser.ConcatContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#union.
    def visitUnion(self, ctx: QueryLanguageParser.UnionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#star.
    def visitStar(self, ctx: QueryLanguageParser.StarContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#smb.
    def visitSmb(self, ctx: QueryLanguageParser.SmbContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#brakets.
    def visitBrakets(self, ctx: QueryLanguageParser.BraketsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#in.
    def visitIn(self, ctx: QueryLanguageParser.InContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#listElement.
    def visitListElement(self, ctx: QueryLanguageParser.ListElementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#list.
    def visitList(self, ctx: QueryLanguageParser.ListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#set.
    def visitSet(self, ctx: QueryLanguageParser.SetContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#elements.
    def visitElements(self, ctx: QueryLanguageParser.ElementsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#lambdaArgs.
    def visitLambdaArgs(self, ctx: QueryLanguageParser.LambdaArgsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by QueryLanguageParser#lambda.
    def visitLambda(self, ctx: QueryLanguageParser.LambdaContext):
        return self.visitChildren(ctx)
