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

## Copyright and usage restriction

**Copyright (C) by LAH Asif 2026. All Rights Reserved.**

This public repository is published for attribution and inspection only. No
permission is granted to copy, rebuild, modify, redistribute, or create
 derivative works without prior written permission. See [LICENSE](LICENSE) and
[COPYRIGHT.md](COPYRIGHT.md).
