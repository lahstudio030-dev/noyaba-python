# Noyaba v1.3 Final Grammar Reference

This grammar is the authoritative Step 5 language-design contract. Implemented status is tracked separately in `IMPLEMENTATION_GAP_REPORT.md`.

## Core grammar

```ebnf
program ::= { statement } ;
block ::= INDENT { statement } DEDENT ;
assignment ::= target "=" expression ;
reference_assignment ::= "ref" identifier "=" expression ;
freeze_assignment ::= "freeze" identifier "=" expression
                    | identifier ":" "freeze" "=" expression ;
typed_assignment ::= identifier ":" type_name "=" expression ;
if_statement ::= "if" expression ":" block { "elif" expression ":" block } [ "else" ":" block ] ;
while_statement ::= "while" expression ":" block ;
for_statement ::= "for" identifier "in" expression ":" block ;
trigger_statement ::= "trigger" expression ":" trigger_block ;
trigger_block ::= { case_clause } [ default_clause ] ;
case_clause ::= "case" expression { "," expression } ":" block ;
default_clause ::= "default" ":" block ;
function_definition ::= "func" identifier "(" [ parameter { "," parameter } ] ")" ":" block ;
return_statement ::= "return" [ expression ] ;
with_statement ::= "with" ":" block | "with" identifier ":" block ;
goto_statement ::= "goto" identifier ;
label ::= identifier ":" ;
try_statement ::= "try" ":" block { except_clause } ;
except_clause ::= "except" [ type_name ] [ "as" identifier ] ":" block ;
raise_statement ::= "raise" expression ;
import_statement ::= "from" module_name "import" identifier { "," identifier } ;
class_definition ::= "class" identifier [ "(" identifier ")" ] ":" class_block ;
class_block ::= { field_declaration | function_definition } ;
field_declaration ::= identifier [ ":" type_name ] [ "=" expression ] ;
macro_definition ::= "macro" identifier "(" [ identifier { "," identifier } ] ")" ":" expression ;
fixed_struct_definition ::= "struct" identifier ":" struct_block ;
struct_block ::= { identifier ":" type_name [ "=" expression ] } ;
cost_definition ::= "cost" identifier "=" cost_members ;
```

## Trigger rules

The trigger expression is evaluated once. Case expressions are evaluated top-to-bottom and compared using Noyaba equality. The first matching case executes and exits the trigger. There is no fall-through. `default` is optional and may occur once. Duplicate statically identical constant cases are compiler errors. A trigger creates no scope.

## Module grammar rules

`from module import name[, name]*` is the v1.3 import form. Module names resolve through importer directory, project root, configured Noyaba paths, and available standard-library path in that order. Python system paths are not searched.

## Class rules

`self` is an automatically supplied bound method parameter. `__init__` is called after allocation and declared-field initialization. Single inheritance uses `class Child(Parent):`; multiple inheritance and `__new__` are deferred.

## Macro rules

Macro arguments are syntax/AST inputs. Expansion happens before bytecode generation; macros cannot access runtime values, cannot recurse, and must retain meaningful source locations.

## Fixed struct rules

Fields are declaration-ordered, typed, required unless defaults exist, reject unknown names, reject deletion, and remain distinct from dynamic structs.

## Privacy lexical rules

`_name` is module-private/non-public. `__name` is strong private/internal. Privacy is language-level visibility, not Python mangling or memory security.
