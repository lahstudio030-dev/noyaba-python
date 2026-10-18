# Noyaba v1.3 Final Semantic Contract

This is the authoritative runtime contract from the human Step 5 decisions. The current implementation status is documented in `IMPLEMENTATION_GAP_REPORT.md`.

## Trigger/case

Evaluate the trigger expression exactly once. Evaluate case expressions in source order. Compare using Noyaba value equality. Execute the first matching case, then exit. No implicit fall-through. Execute `default` only when no case matches. A trigger has no special scope. Return, raise, goto, and loop control retain ordinary semantics. A statically identical constant duplicate case is a compiler error; otherwise duplicate cases are legal.

## Modules

A module is a source file identified by canonical normalized absolute path. Search importer directory, project root, configured Noyaba module paths, then available standard-library path. First import resolves, loads, parses, compiles, executes, and caches. Re-import uses the cache; top-level code executes once. A loading-state cycle raises a dedicated module/import error. There is no implicit reload. Each module has an independent global environment. Public names export; names beginning `_` do not; explicit private import is rejected.

## Classes

Classes have declared fields and methods and support single inheritance. Construction allocates an instance, initializes declared fields, follows inherited/new initialization path as specified, calls `__init__`, and returns the instance. v1.3 does not introduce `__new__`. Instance method access creates a bound callable supplying `self`. Lookup is instance, class, parent, then parent chain; first definition wins. Child definitions override. `super` supplies parent-class lookup while preserving the current instance. Default classes are fixed-field oriented; dynamic behavior uses existing dynamic objects. Only explicitly registered special methods are dispatched specially.

## Macros

Macros transform syntax/AST at compile time before bytecode generation. Arguments are syntax, not runtime values. Macros cannot access runtime variables, cannot recurse, and compile-time expansion errors are language errors. Expansion must preserve source locations and use hygienic internal names. A macro is not a runtime function.

## Fixed structs

Fixed structs have declaration-ordered typed fields. Required fields must be supplied unless defaults exist. Unknown fields are errors. Mutation must satisfy field type. Deletion is prohibited. Metadata remains available at runtime. Field references use ordinary BindingCell behavior. Fixed structs never silently become dynamic structs.

## Privacy

`_name` is module-private/non-public: internal access is allowed, public/wildcard export is excluded, and restricted external access raises a privacy error. `__name` is strong private/internal and is not publicly importable or externally accessible through normal lookup. No Python name mangling is used. Privacy is language visibility, not memory security.

## Cost

`cost` is a shared-storage tagged union. Exactly one member is active. Assigning a member changes active member and shared storage. Reading an inactive member is an error unless an explicit conversion exists. Storage capacity is the maximum member representation plus required metadata; references point to shared storage, not copied values. Raw offsets are not language syntax. Exact C ABI bytes are defined in the future native implementation phase.

## Exceptions

Errors derive from the Noyaba hierarchy. A handler matches the raised error type or any parent type. Handlers are checked top-to-bottom; first compatible handler executes. `except` without a type is a final catch-all. Optional `as e` binds the exception object. If no handler matches, unwind caller frames. If no frame handles it, report an unhandled exception with source location. Raising within a handler begins a new unwind. Module initialization failures propagate as module-load errors while preserving the original cause.

## Native boundary

Native adapters receive explicit Noyaba values and return a Noyaba value or Noyaba error. Ownership is explicit: borrowed values cannot outlive their VM scope; native-created values register with runtime memory management. Calls include ABI version information and use an explicit registry. Native code cannot manipulate Python VM internals. Matching major ABI versions are required. Platform calling convention and exact C struct layout are backend details.

## Casting

Casting is explicit through `int`, `float`, `str`, and `bool`. Allowed numeric conversions are `int→float`, `float→int` with truncation toward zero, `bool→int`, and `int→bool`. Signed 64-bit overflow raises a Noyaba numeric/value error. `str` creates a string representation, not memory reinterpretation. `bool` uses finalized Noyaba truthiness. Invalid conversions raise a runtime conversion/type error. Fixed assignment does not implicitly narrow; references are not copied by casting and cannot bypass BindingCell type enforcement.
