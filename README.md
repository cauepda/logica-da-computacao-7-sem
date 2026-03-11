# logica-da-computacao-7-sem

[![Compilation Status](https://compiler-tester.insper-comp.com.br/svg/cauepda/logica-da-computacao-7-sem)](https://compiler-tester.insper-comp.com.br/svg/cauepda/logica-da-computacao-7-sem)

This repository is monitored by Compiler Tester for automatic compilation status.

# Diagrama Sintático
![](diagrama_sintatico.png)


```ebnf

EXPRESSION = TERM, { ("+" | "-"), TERM } ;
TERM = FACTOR, { ("*" | "/"), FACTOR } ;
FACTOR = ("+" | "-"), FACTOR | "(", EXPRESSION, ")" | NUMBER ;
NUMBER = DIGIT, {DIGIT} ;
DIGIT = 0 | 1 | ... | 9 ;

```