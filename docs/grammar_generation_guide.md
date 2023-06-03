# Генерация грамматики языка запросов

Для генерации файлов парсера по грамматике нужно выполнить следующие команды из корня проекта:

```
cd project/query_language/grammar
antlr4 QueryLanguage.g4 -visitor -Dlanguage=Python3
```

Подробнее: https://github.com/antlr/antlr4/blob/master/doc/python-target.md
