import pytest

from project.query_language.interpreter.interpret_visitor import TypesException
from project.query_language.interpreter.interpreter import Interpreter


@pytest.mark.parametrize(
    "script",
    [
        "g = ( [ 1, 2 ] ++ { 1, 2, 3 } )\n",
        "g = ( 1 ++ 2 )\n",
        'g = ( 1 ++ "a" )\n',
        'g = ( "a" ++ 1 )\n',
        'g = ( "1" ++ "a" )\n',
        'g = ( "1" ++ "a" )\n',
    ],
)
def test_concat_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = ( [ 1, 2 ] | { 1, 2, 3 } )\n",
        "g = ( 1 | 2 )\n",
        'g = ( 1 | "a" )\n',
        'g = ( "a" | 1 )\n',
        'g = ( "1" | "a" )\n',
        'g = ( "1" | "a" )\n',
    ],
)
def test_union_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = *( [ 1, 2 ] )\n",
        "g = *( { 1, 2 } )\n",
        "g = *( 1 )\n",
        'g = *( "a" )\n',
    ],
)
def test_star_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = smb [ 1, 2 ]\n",
        "g = smb { 1, 2 }\n",
        "g = smb 1\n",
        'g = smb ( smb "a" )\n',
    ],
)
def test_star_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = setStart ( [ 1, 2 ] ) ( { 1 } )\n",
        "g = setStart ( { 1, 2 } ) ( { 1 } )\n",
        "g = setStart ( { 1, 2 } ) ( { 1 } )\n",
        'g = setStart ( smb "a" ) ( 1 )\n',
        "g = setStart ( 1 ) ( { 1 } )\n",
        'g = setStart ( "a" ) ( { 1 } )\n',
    ],
)
def test_set_start_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = setFinal ( [ 1, 2 ] ) ( { 1 } )\n",
        "g = setFinal ( { 1, 2 } ) ( { 1 } )\n",
        "g = setFinal ( { 1, 2 } ) ( { 1 } )\n",
        'g = setFinal ( smb "a" ) ( 1 )\n',
        "g = setFinal ( 1 ) ( { 1 } )\n",
        'g = setFinal ( "a" ) ( { 1 } )\n',
    ],
)
def test_set_final_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = addStart ( [ 1, 2 ] ) ( 1 )\n",
        "g = addStart ( { 1, 2 } ) ( 1 )\n",
        "g = addStart ( { 1, 2 } ) ( 1 )\n",
        "g = addStart ( 1 ) ( 1 )\n",
        'g = addStart ( "a" ) ( 1 )\n',
    ],
)
def test_add_start_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = addFinal ( [ 1, 2 ] ) ( 1 )\n",
        "g = addFinal ( { 1, 2 } ) ( 1 )\n",
        "g = addFinal ( { 1, 2 } ) ( 1 )\n",
        "g = addFinal ( 1 ) ( 1 )\n",
        'g = addFinal ( "a" ) ( 1 )\n',
    ],
)
def test_add_final_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = getStart ( [ 1, 2 ] )\n",
        "g = getStart ( { 1, 2 } )\n",
        "g = getStart ( { 1, 2 } )\n",
        "g = getStart ( 1 )\n",
        'g = getStart ( "a" )\n',
    ],
)
def test_get_start_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = getFinal ( [ 1, 2 ] )\n",
        "g = getFinal ( { 1, 2 } )\n",
        "g = getFinal ( { 1, 2 } )\n",
        "g = getFinal ( 1 )\n",
        'g = getFinal ( "a" )\n',
    ],
)
def test_get_final_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = getReachable ( [ 1, 2 ] )\n",
        "g = getReachable ( { 1, 2 } )\n",
        "g = getReachable ( { 1, 2 } )\n",
        "g = getReachable ( 1 )\n",
        'g = getReachable ( "a" )\n',
    ],
)
def test_get_reachable_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = getVertices ( [ 1, 2 ] )\n",
        "g = getVertices ( { 1, 2 } )\n",
        "g = getVertices ( { 1, 2 } )\n",
        "g = getVertices ( 1 )\n",
        'g = getVertices ( "a" )\n',
    ],
)
def test_get_vertices_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = getEdges ( [ 1, 2 ] )\n",
        "g = getEdges ( { 1, 2 } )\n",
        "g = getEdges ( { 1, 2 } )\n",
        "g = getEdges ( 1 )\n",
        'g = getEdges ( "a" )\n',
    ],
)
def test_get_edges_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = getLabels ( [ 1, 2 ] )\n",
        "g = getLabels ( { 1, 2 } )\n",
        "g = getLabels ( { 1, 2 } )\n",
        "g = getLabels ( 1 )\n",
        'g = getLabels ( "a" )\n',
    ],
)
def test_get_labels_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = map ( \el -> el ) ( 1 )\n",
        'g = map ( \el -> el ) ( "a" )\n',
        'g = map ( \el -> el ) ( smb "a" )\n',
        "\n".join(
            [
                'a = ( smb "a" ++ a )',
                "g = map ( \el -> el ) ( a )",
                "",
            ]
        ),
    ],
)
def test_map_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        "g = filter ( \el -> True ) ( 1 )\n",
        'g = filter ( \el -> True ) ( "a" )\n',
        'g = filter ( \el -> True ) ( smb "a" )\n',
        "\n".join(
            [
                'a = ( smb "a" ++ a )',
                "g = filter ( \el -> True ) ( a )",
                "",
            ]
        ),
    ],
)
def test_filter_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        'g = ( "a" ) in "aaa"\n',
        'g = ( "a" ) in 1\n',
        'g = ( "a" ) in ( smb "a" )\n',
        'g = ( 1 ) in "aa"\n',
        "\n".join(
            [
                'a = ( smb "a" ++ a )',
                'g = ( "a" ) in a\n',
                "",
            ]
        ),
    ],
)
def test_in_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        'g = ( [ 1, 2, 3 ] )[ "a" ]\n',
        'g = ( [ 1, 2, 3 ] )[ ( smb "a" ) ]\n',
        'g = ( smb "a" )[ [ 1, 2, 3 ] ]\n',
        'g = ( "shajhshja" )[ 0 ]\n',
        "\n".join(
            [
                'a = ( smb "a" ++ a )',
                "g = ( a )[ 1 ]",
                "",
            ]
        ),
    ],
)
def test_list_element_exception(script):
    interpreter = Interpreter()
    with pytest.raises(TypesException):
        interpreter.execute_script(script)
