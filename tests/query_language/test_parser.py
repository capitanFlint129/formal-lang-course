import pytest
from networkx.drawing.nx_pydot import read_dot
from networkx.utils.misc import graphs_equal

from project.query_language.grammar.parser import *


@pytest.mark.parametrize(
    "script",
    [
        "g = test_script\n",
        "g = 0\n",
        'g = "aaa"\n',
        'g = "a/a"\n',
        "g = load ./a/a\n",
        'print "aaa"\n',
        "g_1 = 0\n",
        "g_112 = 0\n",
        "g_112 = True\n",
        "g_112 = False\n",
        "g_112 = [ 0, test_script, 2 ]\n",
        "g_112 = [ 0..100 ]\n",
        "g_112 = [ -100..100 ]\n",
        "g_112 = { 0, test_script, 2 }\n",
        "g_112 = { 0..100 }\n",
        "g_112 = ( { 0, test_script, 2 } )\n",
        "g_112 = ( { { 0, test_script, 2 }, test_script, 2 } )\n",
        '_a = { { 0, test_script, 2 }, [ test_script, "aa", 555 ], 2 }\n',
        "g = setStart ( setFinal ( g_ ) ( getVertices ( g_ ) ) ) ( { 0..100 } )\n",
        "g_ = load /home/user/wine.dot\n",
        'l1 = "l1" | "l2"\n',
        'q1 = *( "type" | l1 )\n',
        'q2 = "sub_class_of" ++ l1\n',
        "res1 = g & q1\n",
        "res2 = g & q2\n",
        "print res1\n",
        "s = getStart ( g )\n",
        "vertices1 = filter ( \\v -> v in s ) ( map ( \\edge -> edge[ 0 ][ 0 ] ) ( getEdges ( res1 ) ) )\n",
        "vertices2 = filter ( \\v -> v in s ) ( map ( \\edge -> edge[ 0 ][ 0 ] ) ( getEdges ( res2 ) ) )\n",
        "vertices = vertices1 & vertices2\n",
        "print vertices\n",
    ],
)
def test_check_script_positive(script):
    assert check_script_correct(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = 0",  # no newline
        "g = +test_script\n",
        "g = =0\n",
        "g = /aaa\n",
        'g = load "a/a"\n',
        "print ~~~\n",
        "g_1 += 0\n",
        "-g_112 = 0\n",
        "g_112 = { 0, test_script, 2 ]\n",
        "g_112 = { 0, -aaaa, 2 }\n",
        "g_112 = ( {0, test_script, 2}]\n",
        "g = setstart  ( setFinal ( g_ )  ( getVertices g_ )  )  ( { 0..100 } )\n",
        "g = setStart  ( setFina ( g_ )  ( getVertices g_ )  )  ( { 0..100 } )\n",
        "g = setStart  ( setFinal ( g_ )  ( getVertices g_ )  )  ( { 0.100 } )\n",
        'l1 = "l1" "l2"\n',
        'q1 = ( "type" | l1*\n',
        'q2 = "sub_class_of" + l1\n',
        "res1 = g && q1\n",
        "res2 = g || q2\n",
        "print( res1 )\n",
        "vertices1 = filter ( 100 )  ( map ( \\edge -> edge[ 0 ][ 0 ] )  ( getEdges ( res1 ) )  )\n",
        "vertices2 = filter ( \\v -> v in s )  ( map ( 100 )  ( getEdges ( res2 ) )  )\n",
    ],
)
def test_check_script_negative(script):
    assert not check_script_correct(script)


def test_check_script_from_file_positive():
    script_path = "tests/data/query_language/test_script"
    with open(script_path, "r") as script_file:
        script = script_file.read()
    assert check_script_correct(script)


def test_export_tree_to_dot():
    script_path = "tests/data/query_language/test_script"
    result_path = "tests/data/query_language/result.dot"
    expected_path = "tests/data/query_language/expected.dot"
    with open(script_path, "r", newline="") as script_file:
        export_script_to_dot(script_file.read(), result_path)
    assert graphs_equal(read_dot(expected_path), read_dot(result_path))


def test_export_tree_from_file_to_dot():
    script_path = "tests/data/query_language/test_script"
    result_path = "tests/data/query_language/result.dot"
    expected_path = "tests/data/query_language/expected.dot"
    export_script_file_to_dot(script_path, result_path)
    assert graphs_equal(read_dot(expected_path), read_dot(result_path))
