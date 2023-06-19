import sys
import typing

from project.automata import *
from project.graph_utils import load_graph_from_dot
from project.query_language.grammar.QueryLanguageParser import QueryLanguageParser
from project.query_language.grammar.QueryLanguageVisitor import QueryLanguageVisitor
from project.query_language.interpreter.types import *
from project.rpq.all_pairs import (
    finite_automata_intersection,
    get_reachable_by_intersection_pairs,
    regular_query_fa,
)


class InterpretException(Exception):
    """
    Base exception for interpretation
    """

    def __init__(self, statement, msg):
        self.statement = statement
        self.msg = msg

    def __str__(self):
        return f"Statement - {self.statement}: {self.msg}"


class UnknownVariable(InterpretException):
    """
    Exception for undefined variable usage
    """

    pass


class TypesException(InterpretException):
    pass


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
            raise InterpretException(self.statement_count, "Bad frames state")
        self.cur_frame = self.frames[-1]
        self.frames = self.frames[:-1]

    def visitStmt(self, ctx: QueryLanguageParser.StmtContext):
        self.statement_count += 1
        return self.visitChildren(ctx)

    def visitDeclaration(self, ctx: QueryLanguageParser.DeclarationContext):
        var_name = ctx.children[0].getText()
        if self._get_value(var_name) is not None:
            raise InterpretException(self.statement_count, "Redeclaring a variable")
        try:
            expr = self.visit(ctx.children[2])
        except UnknownVariable:
            self._set_value(var_name, Expression(RFA(), RSMType()))
            expr = self.visit(ctx.children[2])
            if not isinstance(expr.type, RSMType):
                raise InterpretException(
                    self.statement_count,
                    f"Recursion allowed only for RSM, not for {expr.type}",
                )
        self._set_value(var_name, expr)

    def visitPrint(self, ctx: QueryLanguageParser.PrintContext):
        expr = self.visit(ctx.children[1])
        if isinstance(expr.type, AutomataType):
            self.file.write(str(expr.type) + "\n")
        else:
            self.file.write(str(expr) + "\n")
        return self.defaultResult()

    def visitBrakets(self, ctx: QueryLanguageParser.BraketsContext):
        return self.visit(ctx.children[1])

    def visitName(self, ctx: QueryLanguageParser.NameContext):
        var_name = ctx.getText()
        value = self._get_value(var_name)
        if value is None:
            raise UnknownVariable(self.statement_count, f"Unknown name - {var_name}")
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
        starts_expr = self.visit(ctx.children[3])
        expr = self.visit(ctx.children[1])
        self._check_automata_operation(expr)
        if isinstance(starts_expr.type, SetType):
            new_fa: EpsilonNFA = expr.value.copy()
            new_fa.start_states.clear()
            for state in starts_expr.value:
                new_fa.add_start_state(state)
            return Expression(new_fa, expr.type)
        raise TypesException(
            self.statement_count, "States can't defined as {starts_expr.type}"
        )

    def visitSetFinal(self, ctx: QueryLanguageParser.SetFinalContext):
        finals_expr = self.visit(ctx.children[3])
        expr = self.visit(ctx.children[1])
        self._check_automata_operation(expr)
        if isinstance(finals_expr.type, SetType):
            new_fa: EpsilonNFA = expr.value.copy()
            new_fa.final_states.clear()
            for state in finals_expr.value:
                new_fa.add_final_state(state)
            return Expression(new_fa, expr.type)
        # if finals_expr.type == SetType(
        #     tuple([ListType([IntType(), SetType([StringType])])])
        # ):
        #     return Expression(expr.value.set, RSMType())
        raise TypesException(
            self.statement_count, "States can't defined as {finals_expr.type}"
        )

    def visitAddStart(self, ctx: QueryLanguageParser.AddStartContext):
        start_expr = self.visit(ctx.children[3])
        expr = self.visit(ctx.children[1])
        self._check_automata_operation(expr)
        new_fa: EpsilonNFA = expr.value.copy()
        new_fa.add_start_state(start_expr.value)
        return Expression(new_fa, expr.type)
        # if start_expr.type == ListType([IntType(), SetType([StringType])]):
        #     return Expression(expr.value.set, RSMType())
        # raise Exception(
        #     f"Statement - {self.statement_count}: States can't defined as {start_expr.type}"
        # )

    def visitAddFinal(self, ctx: QueryLanguageParser.AddFinalContext):
        final_expr = self.visit(ctx.children[3])
        expr = self.visit(ctx.children[1])
        self._check_automata_operation(expr)
        # if isinstance(final_expr.type, IntType):
        new_fa: EpsilonNFA = expr.value.copy()
        new_fa.add_final_state(final_expr.value)
        return Expression(new_fa, expr.type)
        # if final_expr.type == ListType([IntType(), SetType([StringType])]):
        #     return Expression(expr.value.set, RSMType())
        # raise Exception(
        #     f"Statement - {self.statement_count}: States can't defined as {final_expr.type}"
        # )

    def visitGetStart(self, ctx: QueryLanguageParser.GetStartContext):
        expr = self.visit(ctx.children[1])
        self._check_automata_operation(expr)
        return Expression(
            tuple([el.value for el in expr.value.start_states]), SetType()
        )

    def visitGetFinal(self, ctx: QueryLanguageParser.GetFinalContext):
        expr = self.visit(ctx.children[1])
        self._check_automata_operation(expr)
        return Expression(
            tuple([el.value for el in expr.value.final_states]), SetType()
        )

    def visitGetReachable(self, ctx: QueryLanguageParser.GetReachableContext):
        expr = self.visit(ctx.children[1])
        if len(ctx.children) == 4:
            query_expr = self.visit(ctx.children[3])
            self._check_automata_operation(expr)
            self._check_automata_operation(query_expr)
            return Expression(
                tuple(set(regular_query_fa(query_expr.value, expr.value))),
                SetType(),
            )
        self._check_automata_operation(expr)
        return Expression(
            tuple(set(get_reachable_by_intersection_pairs(expr.value))),
            SetType(),
        )

    def _check_automata_operation(self, expr: Expression):
        if not isinstance(expr.type, AutomataType):
            raise TypesException(
                self.statement_count, "Can't apply automata operation to non automata"
            )

    def visitGetVertices(self, ctx: QueryLanguageParser.GetVerticesContext):
        expr = self.visit(ctx.children[1])
        self._check_automata_operation(expr)
        return Expression(tuple([el.value for el in expr.value.states]), SetType())

    def visitGetEdges(self, ctx: QueryLanguageParser.GetEdgesContext):
        expr = self.visit(ctx.children[1])
        self._check_automata_operation(expr)
        return Expression(
            tuple(set([(v.value, label.value, u.value) for v, label, u in expr.value])),
            SetType(),
        )

    def visitGetLabels(self, ctx: QueryLanguageParser.GetLabelsContext):
        expr = self.visit(ctx.children[1])
        self._check_automata_operation(expr)
        return Expression(
            tuple(map(lambda sym: sym.value, expr.value.symbols)),
            SetType(),
        )

    def visitMap(self, ctx: QueryLanguageParser.MapContext):
        container_expr = self.visit(ctx.children[3])
        if not isinstance(container_expr.type, ContainerType):
            raise TypesException(
                self.statement_count, "Can't map lambda to {container_expr.type}"
            )
        lambda_func = self.visit(ctx.children[1])
        if len(lambda_func.args) != 1:
            raise InterpretException(
                self.statement_count, "Wrong number of parameters in lambda"
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
            raise TypesException(
                self.statement_count, f"Can't map lambda to {container_expr.type}"
            )
        lambda_func = self.visit(ctx.children[1])
        if len(lambda_func.args) != 1:
            raise InterpretException(
                self.statement_count, f"Wrong number of parameters in lambda"
            )
        self._enter_frame()
        result = []
        result_types = []
        for el, el_type in zip(container_expr.value, container_expr.type.params):
            self._set_value(lambda_func.args[0], Expression(el, el_type))
            is_accepted = self.visit(lambda_func.expr_ctx)
            if not isinstance(is_accepted.type, BoolType):
                raise InterpretException(
                    self.statement_count,
                    f"Filter accepts lambda which returns bool value",
                )
            if is_accepted.value:
                result.append(el)
                result_types.append(el_type)
        self._exit_frame()
        return Expression(tuple(result), ListType(tuple(result_types)))

    def visitLoad(self, ctx: QueryLanguageParser.LoadContext):
        path_expr = self.visit(ctx.children[1])
        try:
            graph = load_graph_from_dot(path_expr.value)
            fa = get_nondeterministic_automata_from_graph(graph)
        except Exception:
            raise InterpretException(self.statement_count, "Can't load graph")
        return Expression(fa, FAType())

    def visitIntersect(self, ctx: QueryLanguageParser.IntersectContext):
        left = self.visit(ctx.children[1])
        right = self.visit(ctx.children[3])
        if isinstance(left.type, SetType) and isinstance(right.type, SetType):
            types = dict(
                list(zip(left.value, left.type.params))
                + list(zip(right.value, right.type.params))
            )
            result = tuple(set(left.value).intersection(set(right.value)))
            return Expression(result, SetType([types[el] for el in result]))
        if isinstance(left.type, FAType) and isinstance(right.type, FAType):
            return Expression(
                finite_automata_intersection(left.value, right.value), FAType()
            )
        if isinstance(left.type, RSMType) and isinstance(right.type, RSMType):
            raise InterpretException(
                self.statement_count, f"Intersections for RSM is not supported"
            )
        if isinstance(left.type, RSMType) or isinstance(right.type, RSMType):
            raise InterpretException(
                self.statement_count, f"Intersections for RSM is not implemented"
            )
        raise TypesException(
            self.statement_count, f"Intersection possible only for automata and set"
        )

    def visitConcat(self, ctx: QueryLanguageParser.ConcatContext):
        left = self.visit(ctx.children[1])
        right = self.visit(ctx.children[3])
        if isinstance(left.type, ListType) and isinstance(right.type, ListType):
            result = list(zip(left.value, left.type.params)) + list(
                zip(right.value, right.type.params)
            )
            return Expression(
                tuple([val for val, _ in result]),
                ListType([type_ for _, type_ in result]),
            )
        if not (
            isinstance(left.type, AutomataType) and isinstance(right.type, AutomataType)
        ):
            raise TypesException(
                self.statement_count, f"Concat possible only for automatas or lists"
            )
        result_type = (
            RSMType()
            if isinstance(left.type, RSMType) or isinstance(right.type, RSMType)
            else FAType()
        )
        return Expression(automatas_concat(left.value, right.value), result_type)

    def visitUnion(self, ctx: QueryLanguageParser.UnionContext):
        left = self.visit(ctx.children[1])
        right = self.visit(ctx.children[3])
        if isinstance(left.type, SetType) and isinstance(right.type, SetType):
            types = dict(
                list(zip(left.value, left.type.params))
                + list(zip(right.value, right.type.params))
            )
            result = tuple(set(left.value + right.value))
            return Expression(result, SetType([types[el] for el in result]))
        if not (
            isinstance(left.type, AutomataType) and isinstance(right.type, AutomataType)
        ):
            raise TypesException(
                self.statement_count, f"Union possible only for automatas or sets"
            )
        result_type = (
            RSMType()
            if isinstance(left.type, RSMType) or isinstance(right.type, RSMType)
            else FAType()
        )
        return Expression(automatas_union(left.value, right.value), result_type)

    def visitStar(self, ctx: QueryLanguageParser.StarContext):
        automata_expr = self.visit(ctx.children[1])
        if isinstance(automata_expr.type, AutomataType):
            return Expression(automata_expr.value.kleene_star(), automata_expr.type)
        raise TypesException(
            self.statement_count, f"Can't apply kleene star to non automata"
        )

    def visitSmb(self, ctx: QueryLanguageParser.SmbContext):
        expr = self.visit(ctx.children[1])
        if expr.type != StringType():
            raise TypesException(
                self.statement_count, f"Automatas with non string labels are forbidden"
            )
        return Expression(Regex(expr.value).to_epsilon_nfa().minimize(), FAType())

    def visitIn(self, ctx: QueryLanguageParser.InContext):
        expr = self.visit(ctx.children[1])
        container_expr = self.visit(ctx.children[3])
        if not isinstance(container_expr.type, ContainerType):
            raise TypesException(
                self.statement_count,
                f"'in' operator works for containers not for {container_expr.type}",
            )
        return Expression(expr.value in container_expr.value, BoolType())

    def visitListElement(self, ctx: QueryLanguageParser.ListElementContext):
        listExpr = self.visit(ctx.children[1])
        expr = self.visit(ctx.children[3])
        if not isinstance(listExpr.type, ListType):
            raise TypesException(
                self.statement_count, f"{listExpr.type} is not subscriptable"
            )
        if not isinstance(expr.type, IntType):
            raise TypesException(
                self.statement_count, f"List indices must be integers, not {expr.type}"
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
            return Expression(tuple(), SetType())
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
