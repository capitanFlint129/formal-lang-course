grammar QueryLanguage;

prog: (stmt NEWLINE)+;

NEWLINE : [\r\n]+ ;

stmt: name ' = ' expr | 'print ' expr;

name: literal | literal name;

string: '/' | '.' | literal | string string;

literal: CHAR | DIGIT | '_';

CHAR:  [a-zA-Z];
DIGIT: [0-9];

integer: DIGIT | DIGIT integer | '-' integer;

bool: 'True' | 'False';

val:
    '"' string '"'
  | integer
  | bool
  | list
  | set;

expr:
    name
  | val
  | set
  | list
  | 'setStart ( ' expr ' ) ( ' expr ' )'
  | 'setFinal ( ' expr ' ) ( ' expr ' )'
  | 'addStart ( ' expr ' ) ( ' expr ' )'
  | 'addFinal ( ' expr ' ) ( ' expr ' )'
  | 'getStart ( ' expr ' )'
  | 'getFinal ( ' expr ' )'
  | 'getReachable ( ' expr ' )'
  | 'getVertices ( ' expr ' )'
  | 'getEdges ( ' expr ' )'
  | 'getEdges ( ' expr ' )'
  | 'map ( ' lambda ' ) ( ' expr ' )'
  | 'filter ( ' lambda ' ) ( ' expr ' )'
  | 'load ' string
  | expr ' & ' expr
  | expr ' ++ ' expr
  | expr ' | ' expr
  | '*' expr
  | 'smb ' expr
  | '( ' expr ' )'
  | expr ' in ' expr
  | expr '[ ' integer ' ]';

list: '[ ' elements ' ]';

set: '{ ' elements ' }';


elements: expr | expr ', ' elements |  integer '..' integer;

lambdaArgs: name | name ', ' lambdaArgs;

lambda: '\\' lambdaArgs ' -> ' expr;
