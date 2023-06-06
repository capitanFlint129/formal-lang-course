from antlr4 import *

from project.query_language.grammar.QueryLanguageLexer import QueryLanguageLexer
from project.query_language.grammar.QueryLanguageParser import QueryLanguageParser
from project.query_language.interpreter.interpret_visitor import InterpretVisitor
from project.query_language.interpreter.types import *


def test_simple_types():
    variables = [
        ("a", "1", 1),
        ("b", "2", 2),
        ("c", "-2", -2),
        ("d", "10000000000", 10000000000),
        ("e", "a", 1),
        ("f", "e", 1),
        ("s", '"aaaaa"', "aaaaa"),
        ("q", '""', ""),
        ("r", '"One. Two three. /Four  "', "One. Two three. /Four  "),
        ("___s__A_", "False", False),
        ("A___s__A_", "True", True),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_value in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        assert expr.value == expected_value


def test_lists():
    variables = [
        ("p", "[ 1, 2, 3 ]", (1, 2, 3)),
        ("p2", "( p ++ p )", (1, 2, 3, 1, 2, 3)),
        ("a", "[ 1, 2, 3, 4, 5, 6 ]", (1, 2, 3, 4, 5, 6)),
        ("a1", "[]", tuple()),
        ("b", "[ -1, 2, -3, 4, -5, -6 ]", (-1, 2, -3, 4, -5, -6)),
        ("c", "[ 0..10 ]", tuple(range(10))),
        ("d", "[ 2..10 ]", tuple(range(2, 10))),
        ("e", "[ -2..10 ]", tuple(range(-2, 10))),
        (
            "f",
            "[ a, b, c, d, e ]",
            (
                (1, 2, 3, 4, 5, 6),
                (-1, 2, -3, 4, -5, -6),
                tuple(range(10)),
                tuple(range(2, 10)),
                tuple(range(-2, 10)),
            ),
        ),
        (
            "g",
            '[ [ 1, 2, 3, 4 ], [ "aa", 1 ], [ a, b, c ] ]',
            (
                (1, 2, 3, 4),
                ("aa", 1),
                ((1, 2, 3, 4, 5, 6), (-1, 2, -3, 4, -5, -6), tuple(range(10))),
            ),
        ),
        (
            "g1",
            '[ [ 1, [ 2 ], [ 3, [ False ] ], [ 4 ] ], [ "aa", 1 ], [ a, b, c ] ]',
            (
                (1, (2,), (3, (False,)), (4,)),
                ("aa", 1),
                ((1, 2, 3, 4, 5, 6), (-1, 2, -3, 4, -5, -6), tuple(range(10))),
            ),
        ),
        ("g1_el", "( ( ( ( g1 )[ 0 ] )[ 2 ] )[ 1 ] )[ 0 ]", False),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_value in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        assert expr.value == expected_value


def test_sets():
    variables = [
        ("a", "[ 1, 2, 3, 4, 5, 6 ]", (1, 2, 3, 4, 5, 6)),
        ("a1", "[]", tuple()),
        ("b", "[ -1, 2, -3, 4, -5, -6 ]", (-1, 2, -3, 4, -5, -6)),
        ("c", "[ 0..10 ]", tuple(range(10))),
        ("d", "[ 2..10 ]", tuple(range(2, 10))),
        ("e", "[ -2..10 ]", tuple(range(-2, 10))),
        (
            "f",
            "[ a, b, c, d, e ]",
            (
                (1, 2, 3, 4, 5, 6),
                (-1, 2, -3, 4, -5, -6),
                tuple(range(10)),
                tuple(range(2, 10)),
                tuple(range(-2, 10)),
            ),
        ),
        ("s", "{ 1, 2, 3 }", {1, 2, 3}),
        ("s2", "{ 1, 2 }", {1, 2}),
        ("a_set", "{ 1, 2, 3, 4, 5, 6 }", {1, 2, 3, 4, 5, 6}),
        ("a1_set", "{}", set()),
        ("a_set_2", "{ 1, 1, 2, 3, 4, 5, 6 }", {1, 1, 2, 3, 4, 5, 6}),
        (
            "a_set_3",
            "{ [ 1, 2, 3 ], 2, 3, [ 1, 2 ], [ 1, 2, 3 ] }",
            {(1, 2, 3), 2, 3, (1, 2), (1, 2, 3)},
        ),
        ("b_set", "{ -1, 2, -3, 4, -5, -6 }", {-1, 2, -3, 4, -5, -6}),
        ("c_set", "{ 0..10 }", set(range(0, 10))),
        ("d_set", "{ 2..10 }", set(range(2, 10))),
        ("e_set", "{ -2..10 }", set(range(-2, 10))),
        (
            "f_set",
            "{ a, b, c, d, e }",
            {
                (1, 2, 3, 4, 5, 6),
                (-1, 2, -3, 4, -5, -6),
                tuple(range(10)),
                tuple(range(2, 10)),
                tuple(range(-2, 10)),
            },
        ),
        ("q", "( 0 ) in a", False),
        ("s_1", "( s | s )", {1, 2, 3}),
        ("s_2", "( s & s )", {1, 2, 3}),
        ("s_3", "( s & s2 )", {1, 2}),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_value in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        if isinstance(expected_value, set):
            assert set(expr.value) == expected_value
        else:
            assert expr.value == expected_value


def test_lambdas():
    variables = [
        ("a", "[ 1, 2, 3, 4, 5, 6 ]", (1, 2, 3, 4, 5, 6)),
        ("a_set", "{ 1..7 }", set(range(1, 7))),
        ("fff", "map ( \el -> el ) ( a )", (1, 2, 3, 4, 5, 6)),
        ("fff_", "map ( \el -> el ) ( a_set )", {1, 2, 3, 4, 5, 6}),
        ("fff_1", "map ( \el -> 1 ) ( a )", {1, 1, 1, 1, 1, 1}),
        ("fff_2", "map ( \el -> 1 ) ( a_set )", (1, 1, 1, 1, 1, 1)),
        ("eee", 'map ( \el -> "" ) ( a )', tuple([""] * 6)),
        ("eee_", 'map ( \el -> "a" ) ( a_set )', tuple(["a"] * 6)),
        ("aaa", "map ( \el -> [ a ] ) ( a )", tuple([((1, 2, 3, 4, 5, 6),)] * 6)),
        (
            "b",
            '[ a, 1, "a", [ "", "a", "b" ] ]',
            ((1, 2, 3, 4, 5, 6), 1, "a", ("", "a", "b")),
        ),
        ("y", "map ( \el -> el ) ( b )", ((1, 2, 3, 4, 5, 6), 1, "a", ("", "a", "b"))),
        ("aa", "{ 1, 2, 3, [ 1, 2, 3 ] }", {1, 2, 3, (1, 2, 3)}),
        ("g", "filter ( \el -> ( el ) in aa ) ( a )", (1, 2, 3)),
        (
            "qq",
            "filter ( \el -> ( el ) in aa ) ( { [ 1, 2, 3 ], [ 1, 2, 3 ] } )",
            ((1, 2, 3),),
        ),
        ("bb", '{ "" }', {""}),
        (
            "bb2",
            'filter ( \el -> ( el ) in bb ) ( map ( \el -> "" ) ( a ) )',
            ("", "", "", "", "", ""),
        ),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_value in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        if isinstance(expected_value, set):
            assert set(expr.value) == expected_value
        else:
            assert expr.value == expected_value


def test_fa():
    variables = [
        ("fa1", 'smb "a"', ["a"]),
        ("fa1_1", "getStart ( fa1 )", {"0"}),
        ("fa1_2", "getFinal ( fa1 )", {"1"}),
        ("fa1_3", "getVertices ( fa1 )", {"0", "1"}),
        ("fa1_4", "getEdges ( fa1 )", {("0", "a", "1")}),
        (
            "fa1_5",
            "getLabels ( fa1 )",
            {
                "a",
            },
        ),
        ("fa1_6", "getReachable ( fa1 )", {("0", "1")}),
        ("fa1_7", "getStart ( setStart ( fa1 ) ( { 1 } ) )", {1}),
        ("fa1_8", "getStart ( setFinal ( fa1 ) ( { 0, 1 } ) )", {"0"}),
        ("fa1_9", "getFinal ( setStart ( fa1 ) ( { 1 } ) )", {"1"}),
        ("fa1_11", "getFinal ( setFinal ( fa1 ) ( { 0, 1 } ) )", {0, 1}),
        ("fa1_12", 'getVertices ( setStart ( fa1 ) ( { "0", "1" } ) )', {"0", "1"}),
        ("fa1_13", 'getVertices ( setFinal ( fa1 ) ( { "0", "1" } ) )', {"0", "1"}),
        ("fa1_14", "getEdges ( setStart ( fa1 ) ( { 0, 1 } ) )", {("0", "a", "1")}),
        ("fa1_15", "getEdges ( setFinal ( fa1 ) ( { 0, 1 } ) )", {("0", "a", "1")}),
        (
            "fa1_16",
            "getLabels ( setStart ( fa1 ) ( { 0, 1 } ) )",
            {
                "a",
            },
        ),
        (
            "fa1_17",
            "getLabels ( setFinal ( fa1 ) ( { 0, 1 } ) )",
            {
                "a",
            },
        ),
        ("fa1_18", "getReachable ( setStart ( fa1 ) ( { 0, 1 } ) )", set()),
        ("fa1_19", "getReachable ( setFinal ( fa1 ) ( { 0, 1 } ) )", set()),
        ("fa2", 'load "example.dot"', ["aaa", "a", "aab", "aaabbb"]),
        (
            "fa2_1",
            "getStart ( fa2 )",
            {
                "17",
                "14",
                "16",
                "9",
                "6",
                "5",
                "1",
                "3",
                "2",
                "7",
                "11",
                "12",
                "0",
                "15",
                "4",
                "8",
                "13",
                "10",
            },
        ),
        (
            "fa2_2",
            "getFinal ( fa2 )",
            {
                "17",
                "14",
                "16",
                "9",
                "6",
                "5",
                "1",
                "3",
                "2",
                "7",
                "11",
                "12",
                "0",
                "15",
                "4",
                "8",
                "13",
                "10",
            },
        ),
        (
            "fa2_3",
            "getVertices ( fa2 )",
            {
                "17",
                "14",
                "16",
                "9",
                "6",
                "5",
                "1",
                "3",
                "2",
                "7",
                "11",
                "12",
                "0",
                "15",
                "4",
                "8",
                "13",
                "10",
            },
        ),
        (
            "fa2_4",
            "getEdges ( fa2 )",
            {
                ("17", "b", "0"),
                ("16", "b", "17"),
                ("0", "b", "11"),
                ("10", "a", "0"),
                ("6", "a", "7"),
                ("0", "a", "1"),
                ("4", "a", "5"),
                ("8", "a", "9"),
                ("2", "a", "3"),
                ("14", "b", "15"),
                ("12", "b", "13"),
                ("3", "a", "4"),
                ("7", "a", "8"),
                ("1", "a", "2"),
                ("9", "a", "10"),
                ("15", "b", "16"),
                ("11", "b", "12"),
                ("13", "b", "14"),
                ("5", "a", "6"),
            },
        ),
        ("fa2_5", "getLabels ( fa2 )", {"a", "b"}),
        ("q1_", '( smb "a" ++ smb "b" )', ["ab"]),
        ("q1__1", "q1_", ["ab"]),
        ("q1__2", "getStart ( q1_ )", {"0;4;5"}),
        ("q1__3", "getFinal ( q1_ )", {"1"}),
        ("q1", 'setFinal ( setStart ( q1_ ) ( { "0;4;5" } ) ) ( { "1" } )', ["ab"]),
        ("q1_1", "q1", ["ab"]),
        ("q1_2", "getStart ( q1 )", {"0;4;5"}),
        ("q1_3", "getFinal ( q1 )", {"1"}),
        ("q1_4", "getReachable ( ( q1 & fa2 ) )", {(("0;4;5", "10"), ("1", "11"))}),
        ("q1_5", "getReachable ( ( q1 & ( setStart ( fa2 ) ( {} ) ) ) )", set()),
        ("q1_6", "getReachable ( ( q1 & fa2 ) )", {(("0;4;5", "10"), ("1", "11"))}),
        (
            "q1_7",
            "getReachable ( ( q1 & ( setStart ( fa2 ) ( getVertices ( fa2 ) ) ) ) )",
            {(("0;4;5", "10"), ("1", "11"))},
        ),
        ("fa2_cleared", "setFinal ( setStart ( fa2 ) ( {} ) ) ( {} )", []),
        ("q2", '( *( smb "a" ) ++ *( smb "b" ) )', ["a", "b", "aaa", "bbb", "aabb"]),
        (
            "q2_3",
            "getReachable ( ( ( q1 & fa2 ) & fa2 ) )",
            {((("0;4;5", "10"), "10"), (("1", "11"), "11"))},
        ),
        (
            "q2_4",
            "getReachable ( ( ( fa2 & q1 ) & q1 ) )",
            {((("10", "0;4;5"), "0;4;5"), (("11", "1"), "1"))},
        ),
        (
            "q2_5",
            "getReachable ( ( fa2 & q1 ) ) ( q1 )",
            {(("10", "0;4;5"), ("11", "1"))},
        ),
        (
            "q2_6",
            'getReachable ( setStart ( fa2 ) ( { "0", "1" } ) ) ( q1 )',
            {
                ("1", "2"),
                ("0", "14"),
                ("1", "7"),
                ("1", "11"),
                ("1", "8"),
                ("1", "13"),
                ("0", "0"),
                ("1", "17"),
                ("1", "10"),
                ("1", "9"),
                ("0", "6"),
                ("0", "12"),
                ("0", "1"),
                ("0", "4"),
                ("1", "15"),
                ("1", "16"),
                ("0", "5"),
                ("0", "3"),
                ("1", "6"),
                ("0", "2"),
                ("0", "7"),
                ("0", "11"),
                ("0", "8"),
                ("1", "14"),
                ("0", "13"),
                ("1", "0"),
                ("0", "17"),
                ("0", "10"),
                ("0", "9"),
                ("1", "12"),
                ("0", "15"),
                ("1", "1"),
                ("0", "16"),
                ("1", "4"),
                ("1", "5"),
                ("1", "3"),
            },
        ),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_value in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        if isinstance(expr.type, FAType):
            for word in expected_value:
                assert expr.value.accepts(word)
        elif isinstance(expected_value, set):
            assert set(expr.value) == expected_value
        else:
            assert expr.value == expected_value


def test_rsm():
    variables = [
        ("a", '( smb "a" | a )', ["S", "a"]),
        ("b", '( smb "b" | b )', ["S", "b"]),
        ("fa", 'smb "c"', None),
        ("c", "( a | b )", ["S", "a", "b"]),
        ("e", "( a ++ b )", ["ab", "Sb", ["a", "S_2"]]),
        ("f", "( fa | b )", ["c", "b", "S"]),
        ("h", "( fa ++ b )", ["cS", "cb"]),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_value in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        if isinstance(expr.type, RSMType):
            for word in expected_value:
                assert expr.value.nfa.accepts(word)
