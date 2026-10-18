# Noyaba v1.3 Built-in Function Inventory

The registry is `VM._builtins()` and every entry below is invoked through the ordinary source `CALL` path. Values crossing the VM boundary are Noyaba `Value` objects or runtime wrappers; host exceptions are translated to `CenterError` subclasses.

| Built-in | Registered | Implemented | Source-callable | Deterministic / tested status |
|---|---:|---:|---:|---|
| `int`, `float`, `str`, `bool` | Yes | Yes | Yes | 64-bit overflow and frozen cast rules covered |
| `len`, `list`, `array`, `dobject`, `struct` | Yes | Yes | Yes | Value collections, structs, binary and lazy sequences covered |
| `count` | Yes | Yes | Yes | `count(start, stop[, step])`, finite lazy sequence; zero-step rejected |
| `enumerate` | Yes | Yes | Yes | Lazy pair sequence, optional integer start |
| `zip` | Yes | Yes | Yes | Lazy shortest-sequence zip |
| `stepview` | Yes | Yes | Yes | Lazy indexed view; positive/negative nonzero step |
| `view`, `print` | Yes | Yes | Yes | VM output path covered |
| `binary` | Yes | Yes | Yes | UTF-8/string, byte-list, integer and binary construction |
| `hash` | Yes | Yes | Yes | SHA-256-derived signed 64-bit, platform-independent |
| `bitfix` | Yes | Yes | Yes | `bitfix(value, min, max)`; deterministic 64-bit hash folded into inclusive range |
| `pow`, `abs`, `round`, `max`, `min` | Yes | Yes | Yes | Numeric utility and CenterError mapping covered |
| `char`, `ord`, `hex`, `oct`, `ascii` | Yes | Yes | Yes | Noyaba conversion/error paths covered |
| `execute` | Yes | Yes | Yes | Re-enters parser/compiler/VM; no host `exec` |
| `eval` | Yes | Yes | Yes | Parser/compiler math-expression subset; no host evaluator |
| `open` | Yes | Yes | Yes | Wrapped read/write/seek/tell/close API |
| `input` | Yes | Yes | Yes | Host input isolated behind builtin wrapper |
| `typeof`, `isinstance`, `callable` | Yes | Yes | Yes | Noyaba kinds, classes and functions |
| `object` | Yes | Yes | Yes | Root runtime object wrapper |
| `freeze` | Yes | Yes | Yes | Binding freeze semantics enforced by runtime |
| `super` | Runtime proxy | Yes | Yes | Parent method dispatch |
| `__class__`, `__struct__`, `__fixed_struct__`, `__enum__`, `__cost__` | Yes | Yes | Internal | Compiler/runtime constructors |

## Determinism and error boundary

`hash` never delegates to Python's randomized `hash()`. `count`, `stepview`, and all indexing enforce deterministic bounds through `LazySequence`. `binary` values are represented as `Kind.BINARY`; they are not Python implementation objects. Builtin adapters translate `TypeError`, `ValueError`, indexing/key errors, and OS errors to Noyaba `CenterError` subclasses.

## Verification

The historical regression gate contains 141 tests. The added suite is `tests/builtins/test_v13_builtins.py` and covers source-callable lazy iteration, binary/hash/bitfix, dynamic pipeline restrictions, wrapped file I/O, and invalid-input error mapping.
