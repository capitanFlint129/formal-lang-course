from antlr4 import *

from project.query_language.grammar.QueryLanguageLexer import QueryLanguageLexer
from project.query_language.grammar.QueryLanguageParser import QueryLanguageParser
from project.query_language.interpreter.interpret_visitor import InterpretVisitor
from project.query_language.interpreter.types import *


def test_simple_types():
    int_type = IntType()
    str_type = StringType()
    bool_type = BoolType()
    variables = [
        ("a", "1", int_type),
        ("b", "2", int_type),
        ("c", "-2", int_type),
        ("d", "10000000000", int_type),
        ("e", "a", int_type),
        ("f", "e", int_type),
        ("s", '"aaaaa"', str_type),
        ("q", '""', str_type),
        ("r", '"One. Two three. /Four  "', str_type),
        ("___s__A_", "False", bool_type),
        ("A___s__A_", "True", bool_type),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_type in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        assert expr.type == expected_type


def test_containers():
    variables = [
        ("p", "[ 1, 2, 3 ]", ListType),
        ("p2", "( p ++ p )", ListType),
        ("s", "{ 1, 2, 3 }", SetType),
        ("s2", "{ 1, 2 }", SetType),
        ("a", "[ 1, 2, 3, 4, 5, 6 ]", ListType),
        ("a1", "[]", ListType),
        ("b", "[ -1, 2, -3, 4, -5, -6 ]", ListType),
        ("c", "[ 0..10 ]", ListType),
        ("d", "[ 2..10 ]", ListType),
        ("e", "[ -2..10 ]", ListType),
        ("f", "[ a, b, c, d, e ]", ListType),
        ("g", '[ [ 1, 2, 3, 4 ], [ "aa", 1 ], [ a, b, c ] ]', ListType),
        (
            "g1",
            '[ [ 1, [ 2 ], [ 3, [ False ] ], [ 4 ] ], [ "aa", 1 ], [ a, b, c ] ]',
            ListType,
        ),
        ("g1_el", "( ( ( ( g1 )[ 0 ] )[ 2 ] )[ 1 ] )[ 0 ]", BoolType),
        ("a_set", "{ 1, 2, 3, 4, 5, 6 }", SetType),
        ("a1_set", "{}", SetType),
        ("a_set_2", "{ 1, 1, 2, 3, 4, 5, 6 }", SetType),
        ("a_set_3", "{ [ 1, 2, 3 ], 2, 3, [ 1, 2 ], [ 1, 2, 3 ] }", SetType),
        ("b_set", "{ -1, 2, -3, 4, -5, -6 }", SetType),
        ("c_set", "{ 0..10 }", SetType),
        ("d_set", "{ 2..10 }", SetType),
        ("e_set", "{ -2..10 }", SetType),
        ("f_set", "{ a, b, c, d, e }", SetType),
        ("f_set_2", "{ a_set, b_set, c_set, d_set, e_set }", SetType),
        ("g_set", '{ { 1, 2, 3, 4 }, { "aa", 1 }, { a, b, c } }', SetType),
        ("q", "( 0 ) in a", BoolType),
        ("s_1", "( s | s )", SetType),
        ("s_2", "( s & s )", SetType),
        ("s_3", "( s & s2 )", SetType),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_type_class in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        assert expr.type.__class__ == expected_type_class


def test_lambdas():
    variables = [
        ("a", "[ 1, 2, 3, 4, 5, 6 ]", ListType),
        ("a_set", "{ 1..7 }", SetType),
        ("fff", "map ( \el -> el ) ( a )", ListType),
        ("fff_", "map ( \el -> el ) ( a_set )", ListType),
        ("fff_1", "map ( \el -> 1 ) ( a )", ListType),
        ("fff_2", "map ( \el -> 1 ) ( a_set )", ListType),
        ("eee", 'map ( \el -> "" ) ( a )', ListType),
        ("eee_", 'map ( \el -> "a" ) ( a_set )', ListType),
        ("aaa", "map ( \el -> [ a ] ) ( a )", ListType),
        ("aaa_", "map ( \el -> { a_set } ) ( a_set )", ListType),
        ("b", '[ a, 1, "a", { "", "a", "b" } ]', ListType),
        ("y", "map ( \el -> el ) ( b )", ListType),
        ("c", "map ( \el -> el ) ( b )", ListType),
        ("aa", "{ 1, 2, 3, [ 1, 2, 3 ] }", SetType),
        ("g", "filter ( \el -> ( el ) in aa ) ( a )", ListType),
        (
            "qq",
            "filter ( \el -> ( el ) in aa ) ( { [ 1, 2, 3 ], [ 1, 2, 3 ] } )",
            ListType,
        ),
        ("bb", '{ "" }', SetType),
        ("bb2", 'filter ( \el -> ( el ) in bb ) ( map ( \el -> "" ) ( a ) )', ListType),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_type_class in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        assert expr.type.__class__ == expected_type_class


def test_fa():
    variables = [
        ("fa1", 'smb "aaa"', FAType),
        ("fa1_1", "getStart ( fa1 )", SetType),
        ("fa1_2", "getFinal ( fa1 )", SetType),
        ("fa1_3", "getVertices ( fa1 )", SetType),
        ("fa1_4", "getEdges ( fa1 )", SetType),
        ("fa1_5", "getLabels ( fa1 )", SetType),
        ("fa1_6", "getReachable ( fa1 )", SetType),
        ("fa1_7", "getStart ( setStart ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_8", "getStart ( setFinal ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_9", "getFinal ( setStart ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_11", "getFinal ( setFinal ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_12", "getVertices ( setStart ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_13", "getVertices ( setFinal ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_14", "getEdges ( setStart ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_15", "getEdges ( setFinal ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_16", "getLabels ( setStart ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_17", "getLabels ( setFinal ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_18", "getReachable ( setStart ( fa1 ) ( { 0, 1 } ) )", SetType),
        ("fa1_19", "getReachable ( setFinal ( fa1 ) ( { 0, 1 } ) )", SetType),
        (
            "fa2",
            'load "tests/query_language/interpreter/data/example_graph.dot"',
            FAType,
        ),
        ("fa2_1", "getStart ( fa2 )", SetType),
        ("fa2_2", "getFinal ( fa2 )", SetType),
        ("fa2_3", "getVertices ( fa2 )", SetType),
        ("fa2_4", "getEdges ( fa2 )", SetType),
        ("fa2_5", "getLabels ( fa2 )", SetType),
        ("fa2_6", "getReachable ( fa2 )", SetType),
        ("q1_", '( smb "a" ++ smb "b" )', FAType),
        ("q1__1", "q1_", FAType),
        ("q1__2", "getStart ( q1_ )", SetType),
        ("q1__3", "getFinal ( q1_ )", SetType),
        ("q1", 'setFinal ( setStart ( q1_ ) ( { "0;4;5" } ) ) ( { "1" } )', FAType),
        ("q1_1", "q1", FAType),
        ("q1_2", "getStart ( q1 )", SetType),
        ("q1_3", "getFinal ( q1 )", SetType),
        ("q1_4", "getReachable ( ( q1 & fa2 ) )", SetType),
        ("q1_5", "getReachable ( ( q1 & ( setStart ( fa2 ) ( {} ) ) ) )", SetType),
        ("q1_6", "getReachable ( ( q1 & fa2 ) )", SetType),
        (
            "q1_7",
            "getReachable ( ( q1 & ( setStart ( fa2 ) ( getVertices ( fa2 ) ) ) ) )",
            SetType,
        ),
        ("fa2_cleared", "setFinal ( setStart ( fa2 ) ( {} ) ) ( {} )", FAType),
        ("q2", '( *( smb "a" ) ++ *( smb "b" ) )', FAType),
        ("q2_1", "getReachable ( ( q2 & fa2 ) )", SetType),
        (
            "q2_2",
            'getReachable ( ( q2 & ( addFinal ( addStart ( fa2_cleared ) ( "0" ) ) ( "5" ) ) ) )',
            SetType,
        ),
        ("q2_3", "getReachable ( ( ( q1 & fa2 ) & fa2 ) )", SetType),
        ("q2_4", "getReachable ( ( ( fa2 & q1 ) & q1 ) )", SetType),
        ("q2_5", "getReachable ( ( fa2 & q1 ) ) ( q1 )", SetType),
        ("q2_6", "getReachable ( fa2 ) ( q1 )", SetType),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_type_class in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        assert expr.type.__class__ == expected_type_class


def test_rsm():
    variables = [
        ("a", '( smb "a" | a )', RSMType),
        ("b", '( smb "b" | b )', RSMType),
        ("fa", 'smb "c"', FAType),
        ("c", "( a | b )", RSMType),
        ("e", "( a ++ b )", RSMType),
        ("f", "( fa | b )", RSMType),
        ("h", "( fa ++ b )", RSMType),
    ]

    script = "".join([f"{name} = {val}\n" for name, val, _ in variables])
    input_stream = InputStream(script)
    lexer = QueryLanguageLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = QueryLanguageParser(stream)
    tree = parser.prog()
    visitor = InterpretVisitor()
    visitor.visit(tree)

    for name, _, expected_type_class in variables:
        expr = visitor._get_value(name)
        assert expr is not None
        assert expr.type.__class__ == expected_type_class
