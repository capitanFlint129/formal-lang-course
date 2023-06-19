import pytest

from project.query_language.interpreter.interpreter import Interpreter


@pytest.mark.parametrize(
    "script",
    [
        "g = 0\n",
        'g = "aaa"\n',
        'g = "a/a"\n',
        "g_1 = 0\n",
        "g_112 = 0\n",
        "g_112 = True\n",
        "g_112 = False\n",
        "g_112 = [ 0, [ 1 ], 2 ]\n",
        "g_112 = [ 0..100 ]\n",
        "g_112 = [ -100..100 ]\n",
        "g_112 = { 0, 1, 2 }\n",
        "g_112 = { 0..100 }\n",
        'g_112 = ( { 0, "a", 2 } )\n',
        'g_112 = ( { { 0, "a", 2 }, "a", 2 } )\n',
        '_a = { { 0, "a", 2 }, [ "a", "aa", 555 ], 2 }\n',
        'l1 = ( smb "l1" | smb "l2" )\n',
        'q1 = *( ( smb "type" | q1 ) )\n',
        'q2 = ( smb "sub_class_of" ++ q2 )\n',
        'res1 = ( ( smb "a" ) & ( smb "b" ) )\n',
        'res2 = ( ( ( smb "a" ) & ( smb "b" ) ) ++ ( smb "c" ) )\n',
        'vertices1 = filter ( \\v -> ( v ) in { 1 } ) ( map ( \\edge -> ( ( edge )[ 0 ] )[ 0 ] ) ( getEdges ( smb "a" ) ) )\n',
        'vertices2 = filter ( \\v -> ( v ) in { 1 } ) ( map ( \\edge -> ( ( edge )[ 0 ] )[ 0 ] ) ( getEdges ( smb "a" ) ) )\n',
        "vertices = ( { 1 } & { 1, 2 } )\n",
    ],
)
def test_no_output(script, capsys):
    interpreter = Interpreter()
    interpreter.execute_script(script)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize(
    "script, expected",
    [
        (
            "\n".join(
                [
                    "a = 1",
                    "b = 2",
                    "c = -2",
                    "d = 10000000000",
                    "e = a",
                    "f = e",
                    "print a",
                    "print ( ( a ) )",
                    "print b",
                    "print c",
                    "print d",
                    "print e",
                    "print f",
                    "",
                ]
            ),
            "\n".join(["1", "1", "2", "-2", "10000000000", "1", "1", ""]),
        ),
        (
            "\n".join(
                [
                    's = "aaaaa"',
                    'q = ""',
                    'r = "One. Two three. /Four  "',
                    "print s",
                    "print q",
                    "print r",
                    "___s__A_ = False",
                    "A___s__A_ = True",
                    "print ___s__A_",
                    "print A___s__A_",
                    "",
                ]
            ),
            "\n".join(["aaaaa", "", "One. Two three. /Four  ", "False", "True", ""]),
        ),
    ],
)
def test_output_simple_types(script, expected, capsys):
    interpreter = Interpreter()
    interpreter.execute_script(script)
    captured = capsys.readouterr()
    assert captured.out == expected
    assert captured.err == ""


@pytest.mark.parametrize(
    "script, expected",
    [
        (
            "\n".join(
                [
                    "p = [ 1, 2, 3 ]",
                    "print ( p ++ p )",
                    "s = { 1, 2, 3 }",
                    "s2 = { 1, 2 }",
                    "print ( s | s )",
                    "print ( s & s )",
                    "print ( s & s2 )",
                    "",
                    "",
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "a1 = []",
                    'print "__a"',
                    "print a",
                    "print ( ( a ) )",
                    "",
                    "print ( a )[ 0 ]",
                    "print ( a )[ 1 ]",
                    "print ( a )[ 2 ]",
                    "print ( a )[ 3 ]",
                    "print ( a )[ 4 ]",
                    "print ( a )[ 5 ]",
                    "",
                    "print ( 0 ) in a",
                    "print ( 1 ) in a",
                    "print ( 2 ) in a",
                    "print ( 3 ) in a",
                    "print ( 4 ) in a",
                    "print ( 5 ) in a",
                    "print ( 6 ) in a",
                    "print ( 7 ) in a",
                    'print ( "" ) in a',
                    "print ( [] ) in a",
                    "print ( a ) in a",
                    "print ( 0 ) in a1",
                    "",
                ]
            ),
            "\n".join(
                [
                    "(1, 2, 3, 1, 2, 3)",
                    "(1, 2, 3)",
                    "(1, 2, 3)",
                    "(1, 2)",
                    "__a",
                    "(1, 2, 3, 4, 5, 6)",
                    "(1, 2, 3, 4, 5, 6)",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "False",
                    "True",
                    "True",
                    "True",
                    "True",
                    "True",
                    "True",
                    "False",
                    "False",
                    "False",
                    "False",
                    "False",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "b = [ -1, 2, -3, 4, -5, -6 ]",
                    'print "__b"',
                    "print b",
                    "",
                ]
            ),
            "\n".join(
                [
                    "__b",
                    "(-1, 2, -3, 4, -5, -6)",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "c = [ 0..10 ]",
                    'print "__c"',
                    "print c",
                    "",
                ]
            ),
            "\n".join(
                [
                    "__c",
                    "(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "d = [ 2..10 ]",
                    'print "__d"',
                    "print d",
                    "",
                ]
            ),
            "\n".join(
                [
                    "__d",
                    "(2, 3, 4, 5, 6, 7, 8, 9)",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "e = [ -2..10 ]",
                    'print "__e"',
                    "print e",
                    "",
                ]
            ),
            "\n".join(
                [
                    "__e",
                    "(-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "b = [ -1, 2, -3, 4, -5, -6 ]",
                    "c = [ 0..10 ]",
                    "d = [ 2..10 ]",
                    "e = [ -2..10 ]",
                    "f = [ a, b, c, d, e ]",
                    'print "__f"',
                    "print f",
                    "",
                ]
            ),
            "\n".join(
                [
                    "__f",
                    "((1, 2, 3, 4, 5, 6), (-1, 2, -3, 4, -5, -6), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (2, 3, 4, 5, 6, 7, 8, 9), (-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9))",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "b = [ -1, 2, -3, 4, -5, -6 ]",
                    "c = [ 0..10 ]",
                    'g = [ [ 1, 2, 3, 4 ], [ "aa", 1 ], [ a, b, c ] ]',
                    'print "__g"',
                    "print g",
                    "",
                ]
            ),
            "\n".join(
                [
                    "__g",
                    "((1, 2, 3, 4), ('aa', 1), ((1, 2, 3, 4, 5, 6), (-1, 2, -3, 4, -5, -6), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)))",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "b = [ -1, 2, -3, 4, -5, -6 ]",
                    "c = [ 0..10 ]",
                    'g1 = [ [ 1, [ 2 ], [ 3, [ False ] ], [ 4 ] ], [ "aa", 1 ], [ a, b, c ] ]',
                    'print "__g1"',
                    "print g1",
                    "print ( ( ( ( g1 )[ 0 ] )[ 2 ] )[ 1 ] )[ 0 ]",
                    "",
                ]
            ),
            "\n".join(
                [
                    "__g1",
                    "((1, (2,), (3, (False,)), (4,)), ('aa', 1), ((1, 2, 3, 4, 5, 6), (-1, 2, -3, 4, -5, -6), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)))",
                    "False",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "a_set = { 1, 2, 3, 4, 5, 6 }",
                    "a1_set = {}",
                    'print "__a_set"',
                    "",
                    "print ( 0 ) in a_set",
                    "print ( 1 ) in a_set",
                    "print ( 2 ) in a_set",
                    "print ( 3 ) in a_set",
                    "print ( 4 ) in a_set",
                    "print ( 5 ) in a_set",
                    "print ( 6 ) in a_set",
                    "print ( 7 ) in a_set",
                    'print ( "" ) in a_set',
                    "print ( [] ) in a_set",
                    "print ( a ) in a_set",
                    "print ( 0 ) in a1_set",
                    "",
                ]
            ),
            "\n".join(
                [
                    "__a_set",
                    "False",
                    "True",
                    "True",
                    "True",
                    "True",
                    "True",
                    "True",
                    "False",
                    "False",
                    "False",
                    "False",
                    "False",
                    "",
                ]
            ),
        ),
    ],
)
def test_output_containers(script, expected, capsys):
    interpreter = Interpreter()
    interpreter.execute_script(script)
    captured = capsys.readouterr()
    assert captured.out == expected
    assert captured.err == ""


@pytest.mark.parametrize(
    "script, expected",
    [
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "a_2 = [ 1..7 ]",
                    "",
                    "print map ( \el -> el ) ( a )",
                    "print map ( \el -> el ) ( a_2 )",
                    "",
                ]
            ),
            "\n".join(
                [
                    "(1, 2, 3, 4, 5, 6)",
                    "(1, 2, 3, 4, 5, 6)",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "a_2 = [ 1..7 ]",
                    "",
                    "print map ( \el -> 1 ) ( a )",
                    "print map ( \el -> 1 ) ( a_2 )",
                    "",
                ]
            ),
            "\n".join(
                [
                    "(1, 1, 1, 1, 1, 1)",
                    "(1, 1, 1, 1, 1, 1)",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "a_2 = [ 1..7 ]",
                    "",
                    'print map ( \el -> "" ) ( a )',
                    'print map ( \el -> "a" ) ( a_2 )',
                    "",
                ]
            ),
            "\n".join(
                [
                    "('', '', '', '', '', '')",
                    "('a', 'a', 'a', 'a', 'a', 'a')",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "a_2 = [ 1..7 ]",
                    "",
                    "print map ( \el -> [ a ] ) ( a )",
                    "print map ( \el -> [ a_2 ] ) ( a_2 )",
                    "",
                ]
            ),
            "\n".join(
                [
                    "(((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),))",
                    "(((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),))",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    'b = [ a, 1, "a", [ "", "a", "b" ] ]',
                    "print map ( \el -> el ) ( b )",
                    "c = map ( \el -> el ) ( b )",
                    "print c",
                    "",
                ]
            ),
            "\n".join(
                [
                    "((1, 2, 3, 4, 5, 6), 1, 'a', ('', 'a', 'b'))",
                    "((1, 2, 3, 4, 5, 6), 1, 'a', ('', 'a', 'b'))",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "aa = [ 1, 2, 3, [ 1, 2, 3 ] ]",
                    "g = filter ( \el -> ( el ) in aa ) ( a )",
                    "print g",
                    "",
                    "print filter ( \el -> ( el ) in aa ) ( [ [ 1, 2, 3 ], [ 1, 2, 3 ] ] )",
                    "",
                    'bb = [ "" ]',
                    'print filter ( \el -> ( el ) in bb ) ( map ( \el -> "" ) ( a ) )',
                    "",
                ]
            ),
            "\n".join(
                [
                    "(1, 2, 3)",
                    "((1, 2, 3), (1, 2, 3))",
                    "('', '', '', '', '', '')",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    "a = [ 1, 2, 3, 4, 5, 6 ]",
                    "a_2 = [ 1..7 ]",
                    "",
                    "print map ( \el -> el ) ( a )",
                    "print map ( \el -> el ) ( a_2 )",
                    "",
                    "print map ( \el -> 1 ) ( a )",
                    "print map ( \el -> 1 ) ( a_2 )",
                    "",
                    'print map ( \el -> "" ) ( a )',
                    'print map ( \el -> "a" ) ( a_2 )',
                    "",
                    "print map ( \el -> [ a ] ) ( a )",
                    "print map ( \el -> [ a_2 ] ) ( a_2 )",
                    "",
                    'b = [ a, 1, "a", [ "", "a", "b" ] ]',
                    "print map ( \el -> el ) ( b )",
                    "c = map ( \el -> el ) ( b )",
                    "print c",
                    "",
                    "aa = [ 1, 2, 3, [ 1, 2, 3 ] ]",
                    "g = filter ( \el -> ( el ) in aa ) ( a )",
                    "print g",
                    "",
                    "print filter ( \el -> ( el ) in aa ) ( [ [ 1, 2, 3 ], [ 1, 2, 3 ] ] )",
                    "",
                    'bb = [ "" ]',
                    'print filter ( \el -> ( el ) in bb ) ( map ( \el -> "" ) ( a ) )',
                    "",
                ]
            ),
            "\n".join(
                [
                    "(1, 2, 3, 4, 5, 6)",
                    "(1, 2, 3, 4, 5, 6)",
                    "(1, 1, 1, 1, 1, 1)",
                    "(1, 1, 1, 1, 1, 1)",
                    "('', '', '', '', '', '')",
                    "('a', 'a', 'a', 'a', 'a', 'a')",
                    "(((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),))",
                    "(((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),), ((1, 2, 3, 4, 5, 6),))",
                    "((1, 2, 3, 4, 5, 6), 1, 'a', ('', 'a', 'b'))",
                    "((1, 2, 3, 4, 5, 6), 1, 'a', ('', 'a', 'b'))",
                    "(1, 2, 3)",
                    "((1, 2, 3), (1, 2, 3))",
                    "('', '', '', '', '', '')",
                    "",
                ]
            ),
        ),
    ],
)
def test_output_lambdas_map_filter(script, expected, capsys):
    interpreter = Interpreter()
    interpreter.execute_script(script)
    captured = capsys.readouterr()
    assert captured.out == expected
    assert captured.err == ""


@pytest.mark.parametrize(
    "script, expected",
    [
        (
            "\n".join(
                [
                    'fa1 = smb "aaa"',
                    "print getStart ( fa1 )",
                    "print getFinal ( fa1 )",
                    "print getEdges ( fa1 )",
                    "print getLabels ( fa1 )",
                    "",
                    "",
                    "print getStart ( setFinal ( fa1 ) ( { 0, 1 } ) )",
                    "",
                    "print getFinal ( setStart ( fa1 ) ( { 0, 1 } ) )",
                    "print getFinal ( setFinal ( fa1 ) ( { 0, 1 } ) )",
                    "",
                    "print getEdges ( setStart ( fa1 ) ( { 0, 1 } ) )",
                    "print getEdges ( setFinal ( fa1 ) ( { 0, 1 } ) )",
                    "print getLabels ( setStart ( fa1 ) ( { 0, 1 } ) )",
                    "print getLabels ( setFinal ( fa1 ) ( { 0, 1 } ) )",
                    "print getReachable ( setStart ( fa1 ) ( { 0, 1 } ) )",
                    "print getReachable ( setFinal ( fa1 ) ( { 0, 1 } ) )",
                    "",
                ]
            ),
            "\n".join(
                [
                    "('0',)",
                    "('1',)",
                    "(('0', 'aaa', '1'),)",
                    "('aaa',)",
                    "('0',)",
                    "('1',)",
                    "(0, 1)",
                    "(('0', 'aaa', '1'),)",
                    "(('0', 'aaa', '1'),)",
                    "('aaa',)",
                    "('aaa',)",
                    "()",
                    "()",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    'q1_ = ( smb "a" ++ smb "b" )',
                    "print q1_",
                    "print getStart ( q1_ )",
                    "print getFinal ( q1_ )",
                    "",
                    'q1 = setFinal ( setStart ( q1_ ) ( { "0;4;5" } ) ) ( { "1" } )',
                    "print q1",
                    "print getStart ( q1 )",
                    "print getFinal ( q1 )",
                    "",
                ]
            ),
            "\n".join(
                [
                    "FAType",
                    "('0;4;5',)",
                    "('1',)",
                    "FAType",
                    "('0;4;5',)",
                    "('1',)",
                    "",
                ]
            ),
        ),
        (
            "\n".join(
                [
                    'q1_ = ( smb "a" ++ smb "b" )',
                    'q1 = setFinal ( setStart ( q1_ ) ( { "0;4;5" } ) ) ( { "1" } )',
                    'fa2 = load "tests/query_language/interpreter/data/example_graph.dot"',
                    "",
                    "print getReachable ( ( q1 & fa2 ) )",
                    "print getReachable ( ( q1 & ( setStart ( fa2 ) ( {} ) ) ) )",
                    "print getReachable ( ( q1 & fa2 ) )",
                    "print getReachable ( ( q1 & ( setStart ( fa2 ) ( getVertices ( fa2 ) ) ) ) )",
                    "",
                    "fa2_cleared = setFinal ( setStart ( fa2 ) ( {} ) ) ( {} )",
                    'q2 = ( *( smb "a" ) ++ *( smb "b" ) )',
                    "",
                    "print getReachable ( ( ( q1 & fa2 ) & fa2 ) )",
                    "print getReachable ( ( ( fa2 & q1 ) & q1 ) )",
                    "",
                ]
            ),
            "\n".join(
                [
                    "((('0;4;5', '10'), ('1', '11')),)",
                    "()",
                    "((('0;4;5', '10'), ('1', '11')),)",
                    "((('0;4;5', '10'), ('1', '11')),)",
                    "(((('0;4;5', '10'), '10'), (('1', '11'), '11')),)",
                    "(((('10', '0;4;5'), '0;4;5'), (('11', '1'), '1')),)",
                    "",
                ]
            ),
        ),
    ],
)
def test_output_fa(script, expected, capsys):
    interpreter = Interpreter()
    interpreter.execute_script(script)
    captured = capsys.readouterr()
    assert captured.out == expected
    assert captured.err == ""
