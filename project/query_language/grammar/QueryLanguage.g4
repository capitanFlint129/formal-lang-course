grammar QueryLanguage;

prog: (stmt NEWLINE)+;

stmt: declaration | print;

declaration: name ' = ' expr;

print: 'print ' expr;

name: literal | literal name;

string: '/' | '.' | literal | string string;

literal: CHAR | DIGIT | '_';

integer: DIGIT | DIGIT integer | '-' integer;

bool: TRUE | FALSE;

val:
  stringVal
  | integer
  | bool
  | list
  | set;

stringVal: '"' string '"';

expr:
    name
  | val
  | setStart
  | setFinal
  | addStart
  | addFinal
  | getStart
  | getFinal
  | getReachable
  | getVertices
  | getEdges
  | map
  | filter
  | load
  | intersect
  | concat
  | union
  | star
  | smb
  | brakets
  | in
  | listElement;

setStart: 'setStart ( ' expr ' ) ( ' expr ' )';
setFinal: 'setFinal ( ' expr ' ) ( ' expr ' )';
addStart: 'addStart ( ' expr ' ) ( ' expr ' )';
addFinal: 'addFinal ( ' expr ' ) ( ' expr ' )';
getStart: 'getStart ( ' expr ' )';
getFinal: 'getFinal ( ' expr ' )';
getReachable: 'getReachable ( ' expr ' )';
getVertices: 'getVertices ( ' expr ' )';
getEdges: 'getEdges ( ' expr ' )';
map: 'map ( ' lambda ' ) ( ' expr ' )';
filter: 'filter ( ' lambda ' ) ( ' expr ' )';
load: 'load ' string;
intersect: '( 'expr ' & ' expr ' )';
concat: '( 'expr ' ++ ' expr ' )';
union: '( 'expr ' | ' expr ' )';
star: '*' expr;
smb: 'smb ' expr;
brakets: '( ' expr ' )';
in: '( ' expr ' ) in ' expr;
listElement: '( ' expr ' )[ ' integer ' ]';

list: '[ ' elements ' ]' | '[ ' range ' ]';

set: '{ ' elements ' }' | '[ ' range ' ]';


range: integer '..' integer;
elements: expr | expr ', ' elements;

lambdaArgs: name | name ', ' lambdaArgs;

lambda: '\\' lambdaArgs ' -> ' expr;


CHAR:  [a-zA-Z];
DIGIT: [0-9];
NEWLINE : [\r\n]+ ;
TRUE: 'True';
FALSE: 'False';
