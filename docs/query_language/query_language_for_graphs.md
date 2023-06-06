# Язык запросов к графам

## Описание абстрактного синтаксиса языка

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    String of string
  | Int of int
  | Bool of bool
  | Set of set
  | List of list

expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход

lambda = List<var> * expr
```

## Описание конкретного синтаксиса языка

```
prog -> '' | stmt | stmt '\r\n' prog

stmt -> name ' = ' expr | 'print ' expr

name -> literal | literal name

string -> '/' | '.' | ' ' | ';' | literal | string string;

literal -> char | digit | '_'

char -> 'a' | 'b' | ... | 'Z' // включает латинские буквы в нижнем и верхнем регистре

digit -> '0' | '1' | ... | '9' // включает цифры

integer -> digit | digit integer | '-' integer

bool -> 'True' | 'False'

val ->
  stringVal
  | integer
  | bool
  | list
  | set

stringVal -> '"' string '"' | '""'

expr ->
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
  | 'load ' stringVal
  | '( ' expr ' & ' expr ' )'
  | '( ' expr ' ++ ' expr ' )'
  | '( ' expr ' | ' expr ' )'
  | '*( ' expr ' )'
  | 'smb ' expr
  | '( ' expr ' )'
  | '( ' expr ' ) in ' expr
  | '( ' expr ' )' '[ ' integer ' ]'

elements -> expr | expr ', ' elements |  integer '..' integer

list -> '[]' | '[ ' elements ' ]' | '[ ' range ' ]'

set -> '{}' | '{ ' elements ' }' | '{ ' range ' }'

range -> integer '..' integer

elements -> expr | expr ', ' elements

lambdaArgs -> name | name ', ' lambdaArgs

lambda -> '\' lambdaArgs ' -> ' expr

```

## Пример запроса в данном синтаксисе

Исполнение следующих команд подразумевается в рамках одного скрипта.

Загрузка графа из файла.

```
g_ = load "/home/user/wine.dot"
```

Создаем новый граф. Из `g_` берутся все вершины и устанавливаются в качестве финальных,
в полученном графе, в качестве стартовых устанавливаются вершины от 0 до 100.
Имя `g` связывается с полученным графом.
```
g = setStart ( setFinal ( g_ ) ( getVertices ( g_ ) ) ) ( { 0..100 } )
```

Создаем запросы с помощью операций объединения, замыкания и конкатенации.

```
l1 = ( "l1" | "l2" )

q1 = *( ( "type" | l1 ) )
q2 = ( "sub_class_of" ++ l1 )
```

Строим пересечение языков запросов и графа, а затем печатаем результат первого пересечения.
```
res1 = ( g & q1 )
res2 = ( g & q2 )

print res1
```

Получаем стартовые состояния графа.
```
s = getStart ( g )
```

Для каждого из языков-результатов получаем список ребер, с помощью map и лямбды
получаем для каждого ребра вершину источник в композиции, а из нее извлекаем вершину
соответсвующую графу. После чего с помощью filter оставляем только те вершины,
которые являются стартовыми вершинами графа.
```
vertices1 = filter ( \v -> ( v ) in s ) ( map ( \edge -> ( ( edge )[ 0 ] )[ 0 ] ) ( getEdges ( res1 ) ) )
vertices2 = filter ( \v -> ( v ) in s ) ( map ( \edge -> ( ( edge )[ 0 ] )[ 0 ] ) ( getEdges ( res2 ) ) )
```

Строим пересечение полученных множеств вершин и печатаем их.
```
vertices = ( vertices1 & vertices2 )

print vertices
```
