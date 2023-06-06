import sys

from project.query_language.interpreter.interpreter import Interpreter

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You need to specify path to program", file=sys.stderr)
    else:
        interpreter = Interpreter()
        interpreter.execute_from_path(sys.argv[1])
