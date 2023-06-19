import pytest

from project.query_language.interpreter.interpret_visitor import InterpretException
from project.query_language.interpreter.interpreter import Interpreter


@pytest.mark.parametrize(
    "script",
    [
        "g = [ 1, 2, 3, 4, g ]\n",
        "g = { 1, 2, 3, 4, g }\n",
    ],
)
def test_recursion_exception(script):
    interpreter = Interpreter()
    with pytest.raises(InterpretException):
        interpreter.execute_script(script)


@pytest.mark.parametrize(
    "script",
    [
        'a = ( smb "a" ++ g )\n',
        "a = [ 1, 2, 3, g ]\n",
        "a = { 1, 2, 3, g }\n",
    ],
)
def test_unknown_variable_exception(script):
    interpreter = Interpreter()
    with pytest.raises(InterpretException):
        interpreter.execute_script(script)
