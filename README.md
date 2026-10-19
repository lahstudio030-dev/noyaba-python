# Noyaba v1.3 Python Reference VM

A self-contained prototype implementation of the supplied VM architecture. Python is used only as the host language; Noyaba values, bindings, environments, bytecode, frames, references, heap objects, and errors are explicit runtime abstractions.

## Run

```bash
python3 -m noyaba examples/conformance.ny
python3 -m unittest discover -s tests -v
```

The prototype freezes the following implementation choices: signed 64-bit integers raise `OverflowError` on overflow; fixed bindings enforce runtime types without implicit casts; `freeze` makes a binding immutable; temporary `with` bindings are frame-local; references to destroyed environments raise `RefError`; `cost` uses one fixed-size storage slot and member views; `_` names are private to modules; bytecode is represented by versioned instruction objects.

This is a reference VM, not a complete final language implementation. Unsupported syntax fails with a Noyaba `SyntaxError` rather than being executed as Python.

## Layout

- `noyaba/lexer.py` — tokenizer
- `noyaba/parser.py` — recursive-descent/Pratt parser and AST
- `noyaba/compiler.py` — AST to bytecode compiler
- `noyaba/runtime.py` — values, cells, environments, heap, objects, errors
- `noyaba/vm.py` — instruction dispatch and execution
- `noyaba/__main__.py` — CLI
- `tests/` — conformance and unit tests
- `examples/conformance.ny` — runnable examples from the architecture document

Version identifiers: language 1.3, VM 1.0, bytecode 1.

## Supported prototype surface

Expressions, arithmetic/comparison/logical/bitwise operators, assignment and annotations, `if`/`elif`/`else`, `while`, `for`, labels/`goto`, `func`/`return`/recursion, `ref`, `with` automatic and functional branches, `struct`, classes with methods and inheritance, `enum`, `cost`, `try`/`do`/`except`, imports, and the listed core built-ins are represented through explicit runtime APIs.

The opcode table and stack effects are documented in `noyaba/bytecode.py`.

## Noyaba usage and syntax guide

### Running a program

Run a `.noy` or `.ny` source file from the project root:

```bash
python3 -m noyaba path/to/program.noy
```

Run the full conformance suite with:

```bash
python3 -m unittest discover -s tests -v
```

### Values and variables

Noyaba supports integers, floating-point values, booleans, strings, `null`, arrays, lists, objects, structs, classes, functions, and references.

```noyaba
name = "Noyaba"
count = 3
ready = true
items = [1, 2, 3]
view(name)
view(items[0])
```

Use annotations for fixed runtime types:

```noyaba
age: int = 20
message: str = "hello"
```

A fixed binding rejects later values of another type. `freeze` can be used for immutable bindings where supported by the runtime contract.

### Operators and conditions

Arithmetic, comparison, logical, bitwise, membership, and augmented assignment operators are available:

```noyaba
x = 10
y = 3
view(x + y)
view(x > y and y > 0)
view(2 in [1, 2, 3])

if x > y:
    view("x is larger")
elif x == y:
    view("equal")
else:
    view("y is larger")
```

`and` and `or` short-circuit. `not` negates truthiness. Chained comparisons and `in`/`not in` are supported by the current reference VM.

### Functions

Functions use `func`, may have typed or default parameters, and return with `return`:

```noyaba
func add(a: int, b: int = 1):
    return a + b

view(add(4))
view(add(4, 6))
```

### Loops

```noyaba
for item in [1, 2, 3]:
    view(item)

x = 0
while x < 3:
    view(x)
    x += 1
```

`break` and `continue` are available inside loops.

### Structs, classes, and inheritance

```noyaba
struct Point:
    x: int = 0
    y: int = 0

p = Point({x: 2, y: 3})

class Person:
    name = "unknown"
    func greet(self):
        return "Hello " + self.name

class Student(Person):
    grade = 1

s = Student()
view(s.greet())
```

Class methods, inherited fields, fixed field types, `__init__`, `__str__`, and `__repr__` use the explicit Noyaba runtime model.

### Exceptions and modules

```noyaba
try:
    raise "something went wrong"
except CenterError as e:
    view(typeof(e))
    view(e.message)
```

Modules are imported from `.noy` files in the project/module path:

```noyaba
from helpers import add
view(add(2, 3))
```

Private module names beginning with `_` are not exported through ordinary imports.

### Common built-ins

The current VM includes built-ins such as `view`, `print`, `int`, `float`, `str`, `repr`, `bool`, `len`, `typeof`, `isinstance`, `count`, `enumerate`, `zip`, `stepview`, `binary`, `hash`, `bitfix`, `execute`, `eval`, `open`, `list`, `array`, and `dobject`.

The authoritative details are documented in [BUILTIN_INVENTORY.md](BUILTIN_INVENTORY.md), [FINAL_GRAMMAR_REFERENCE.md](FINAL_GRAMMAR_REFERENCE.md), and [FINAL_SEMANTIC_CONTRACT.md](FINAL_SEMANTIC_CONTRACT.md).

For questions or permission requests, see [CONTACT.md](CONTACT.md).

## Copyright and usage restriction

**Copyright (C) by LAH Asif 2026. All Rights Reserved.**

This public repository is published for attribution and inspection only. No permission is granted to copy, rebuild, modify, redistribute, or create derivative works without prior written permission. See [LICENSE](LICENSE) and [COPYRIGHT.md](COPYRIGHT.md).
