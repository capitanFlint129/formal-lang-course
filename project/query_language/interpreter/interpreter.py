import sys
import typing

from antlr4 import *
from pyformlang.regular_expression import Regex

from project import automata
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
        try:
            visitor.visit(tree)
        except Exception as e:
            raise Exception(f"Statement - {visitor.statement_count}: {e}")


class Expression:
    def __init__(self, value: typing.Any, expr_type: Type):
        self.value = value
        self.type = expr_type

    def __str__(self):
        # if isinstance(self.type, SetType):
        #     return '{' + str(self.value)[1: -1] + '}'
        return str(self.value)


class InterpretVisitor(QueryLanguageVisitor):
    def __init__(self, file=sys.stdout):
        self.frames = []
        self.cur_frame: dict[str, Expression] = {}
        self.file = file
        self.statement_count = 0

    def _get_value(self, name: str) -> typing.Optional[Expression]:
        if name in self.cur_frame:
            return self.cur_frame[name]
        for frame in reversed(self.frames):
            if name in frame:
                return frame[name]
        return None

    def _set_value(self, name: str, expr: Expression):
        self.cur_frame[name] = expr

    def _enter_frame(self):
        self.frames.append(self.cur_frame)
        self.cur_frame = {}

    def _exit_frame(self):
        if len(self.frames) == 0:
            raise Exception(f"Statement - {self.statement_count}: Bad frames state")
        self.cur_frame = self.frames[-1]
        self.frames = self.frames[:-1]

    def visitStmt(self, ctx: QueryLanguageParser.StmtContext):
        self.statement_count += 1
        return self.visitChildren(ctx)

    def visitDeclaration(self, ctx: QueryLanguageParser.DeclarationContext):
        var_name = ctx.children[0].getText()
        if self._get_value(var_name) is not None:
            raise Exception(
                f"Statement - {self.statement_count}: Redeclaring a variable"
            )
        self._set_value(var_name, Expression(None, RSMType()))
        expr = self.visit(ctx.children[2])
        self._set_value(var_name, expr)

    def visitPrint(self, ctx: QueryLanguageParser.PrintContext):
        expr = self.visit(ctx.children[1])
        self.file.write(str(expr) + "\n")
        return self.visitChildren(ctx)

    def visitBrakets(self, ctx: QueryLanguageParser.BraketsContext):
        return self.visit(ctx.children[1])

    def visitName(self, ctx: QueryLanguageParser.NameContext):
        var_name = ctx.getText()
        value = self._get_value(var_name)
        if value is None:
            raise Exception(f"Statement - {self.statement_count}: Unknown name")
        return value

    def visitStringVal(self, ctx: QueryLanguageParser.StringValContext):
        if len(ctx.children) == 1:
            return Expression("", StringType())
        return Expression(ctx.children[1].getText(), StringType())

    def visitInteger(self, ctx: QueryLanguageParser.IntegerContext):
        return Expression(int(ctx.getText()), IntType())

    def visitBool(self, ctx: QueryLanguageParser.BoolContext):
        return Expression(ctx.getText() == str(True), BoolType())

    def visitSetStart(self, ctx: QueryLanguageParser.SetStartContext):
        startsExpr = self.visitChildren(ctx.children[1])
        expr = self.visitChildren(ctx.children[3])
        if not isinstance(expr.type, AutomataType):
            raise Exception(
                f"Statement - {self.statement_count}: Can't apply automata operation to non automata"
            )
        if startsExpr.type == SetType([IntType]):
            return Expression(expr.value.set, expr.type)
        elif startsExpr.type == SetType(
            tuple([ListType([IntType(), SetType([StringType])])])
        ):
            return Expression(expr.value.set, RSMType())
        raise Exception(
            f"Statement - {self.statement_count}: Start states can't defined as {startsExpr.type}"
        )

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

    def visitMap(self, ctx: QueryLanguageParser.MapContext):
        container_expr = self.visit(ctx.children[3])
        if not isinstance(container_expr.type, ContainerType):
            raise Exception(
                f"Statement - {self.statement_count}: Can't map lambda to {container_expr.type}"
            )
        lambda_func = self.visit(ctx.children[1])
        if len(lambda_func.args) != 1:
            raise Exception(
                f"Statement - {self.statement_count}: Wrong number of parameters in lambda"
            )
        self._enter_frame()
        result = []
        for el, el_type in zip(container_expr.value, container_expr.type.params):
            self._set_value(lambda_func.args[0], Expression(el, el_type))
            result.append(self.visit(lambda_func.expr_ctx))
        self._exit_frame()
        return Expression(
            tuple([el.value for el in result]),
            ListType(tuple([el.type for el in result])),
        )

    def visitFilter(self, ctx: QueryLanguageParser.FilterContext):
        container_expr = self.visit(ctx.children[3])
        if not isinstance(container_expr.type, ContainerType):
            raise Exception(
                f"Statement - {self.statement_count}: Can't map lambda to {container_expr.type}"
            )
        lambda_func = self.visit(ctx.children[1])
        if len(lambda_func.args) != 1:
            raise Exception(
                f"Statement - {self.statement_count}: Wrong number of parameters in lambda"
            )
        self._enter_frame()
        result = []
        result_types = []
        for el, el_type in zip(container_expr.value, container_expr.type.params):
            self._set_value(lambda_func.args[0], Expression(el, el_type))
            is_accepted = self.visit(lambda_func.expr_ctx)
            if not isinstance(is_accepted.type, BoolType):
                raise Exception(
                    f"Statement - {self.statement_count}: Filter accepts lambda which returns bool value"
                )
            if is_accepted.value:
                result.append(el)
                result_types.append(el_type)
        self._exit_frame()
        return Expression(tuple(result), ListType(tuple(result_types)))

    def visitLoad(self, ctx: QueryLanguageParser.LoadContext):
        path = ctx.children[1].getText()
        try:
            graph = load_graph_from_dot(path)
            fa = get_nondeterministic_automata_from_graph(graph)
        except Exception:
            raise Exception(f"Statement - {self.statement_count}: Can't load graph")
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

    def visitSmb(self, ctx: QueryLanguageParser.SmbContext):
        expr = self.visitChildren(ctx)
        if expr.type != StringType():
            raise Exception(
                f"Statement - {self.statement_count}: Automatas with non string labels are forbidden"
            )
        return Expression(
            automata.get_deterministic_automata_from_regex(Regex(expr.value)), FAType()
        )

    def visitIn(self, ctx: QueryLanguageParser.InContext):
        expr = self.visitChildren(ctx.children[1])
        container_expr = self.visitChildren(ctx.children[3])
        return Expression(expr.value in container_expr.value, BoolType())

    def visitListElement(self, ctx: QueryLanguageParser.ListElementContext):
        listExpr = self.visitChildren(ctx.children[1])
        expr = self.visit(ctx.children[3])
        if not isinstance(listExpr.type, ListType):
            raise Exception(
                f"Statement - {self.statement_count}: {listExpr.type} is not subscriptable"
            )
        if expr.type != IntType():
            raise Exception(
                f"Statement - {self.statement_count}: List indices must be integers, not {expr.type}"
            )
        return Expression(listExpr.value[expr.value], listExpr.type.params[expr.value])

    def visitList(self, ctx: QueryLanguageParser.ListContext):
        if len(ctx.children) == 1:
            return Expression(tuple(), ListType([]))
        elements = self.visit(ctx.children[1])
        return Expression(
            tuple(map(lambda el: el.value, elements)),
            ListType([el.type for el in elements]),
        )

    def visitSet(self, ctx: QueryLanguageParser.SetContext):
        if len(ctx.children) == 1:
            return Expression(tuple(), SetType([]))
        elements = set(self.visit(ctx.children[1]))
        visited = set()
        result = []
        for el in elements:
            if el.value not in visited:
                result.append(el)
                visited.add(el.value)
        result = list(result)
        return Expression(
            tuple(map(lambda el: el.value, result)),
            SetType(tuple([el.type for el in result])),
        )

    def visitElements(self, ctx: QueryLanguageParser.ElementsContext):
        element_expr = self.visit(ctx.children[0])
        if len(ctx.children) > 2:
            return [element_expr] + self.visit(ctx.children[2])
        return [element_expr]

    def visitRange(self, ctx: QueryLanguageParser.RangeContext):
        return [
            Expression(i, IntType())
            for i in range(
                int(ctx.children[0].getText()), int(ctx.children[2].getText())
            )
        ]

    def visitLambdaArgs(self, ctx: QueryLanguageParser.LambdaArgsContext):
        arg_name = ctx.children[0].getText()
        if len(ctx.children) > 2:
            return [arg_name] + self.visit(ctx.children[2])
        return [arg_name]

    def visitLambda(self, ctx: QueryLanguageParser.LambdaContext):
        args = self.visit(ctx.children[1])
        return Lambda(args, ctx.children[3])


class Lambda:
    def __init__(self, args: tuple[str], expr_ctx: QueryLanguageParser.ExprContext):
        self.args = args
        self.expr_ctx = expr_ctx
