import unittest
from noyaba.bytecode import Chunk, Instruction, Op
from noyaba.compiler import Compiler
from noyaba.parser import parse
from noyaba.runtime import *
from noyaba.vm import VM

class RuntimeSemantics(unittest.TestCase):
    def test_value_model_is_explicit(self):
        self.assertEqual(wrap(7).kind, Kind.INT)
        self.assertEqual(wrap(2.5).kind, Kind.FLOAT)
        self.assertEqual(wrap(True).kind, Kind.BOOL)
        self.assertEqual(wrap("x").kind, Kind.STRING)
        self.assertEqual(wrap(None).kind, Kind.NULL)
        self.assertNotIsInstance(wrap(7), int)

    def test_signed_64_bit_bounds(self):
        vm = VM()
        self.assertEqual(vm.binary(Op.ADD, wrap(2), wrap(3)).payload, 5)
        with self.assertRaises(ValueError_):
            vm.binary(Op.ADD, wrap(2**63-1), wrap(1))
        with self.assertRaises(ValueError_):
            vm.binary(Op.SUB, wrap(-(2**63)), wrap(1))

    def test_binding_cell_type_and_freeze(self):
        c = BindingCell(wrap(1), 'int', False, False)
        c.set(wrap(2)); self.assertEqual(c.value.payload, 2)
        with self.assertRaises(TypeError_): c.set(wrap('bad'))
        f = BindingCell(wrap(1), 'int', False, True)
        with self.assertRaises(FreezeError): f.set(wrap(2))

    def test_reference_is_cell_alias(self):
        e = Environment(); x = e.define('x', wrap(4)); r = Reference(x)
        r.target.set(wrap(20)); self.assertEqual(e.get('x').payload, 20)

    def test_destroyed_cell_rejects_reference(self):
        e = Environment(temporary=True); r = Reference(e.define('x', wrap(1)))
        e.destroy()
        with self.assertRaises(RefError): r.target.set(wrap(2))

    def test_frame_local_assignment_does_not_mutate_global(self):
        v = VM(); v.run('x = 1\nfunc f():\n    x = 2\n    return x\nview(f())\nview(x)\n')
        self.assertEqual(v.output, ['2', '1'])

    def test_reference_program(self):
        v = VM(); v.run('x = 4\nref y = x\ny = 20\nview(x)\n')
        self.assertEqual(v.output, ['20'])

    def test_freeze_source_syntax(self):
        v = VM()
        with self.assertRaises(FreezeError): v.run('x: freeze = 12\nx = 13\n')

    def test_temporary_scope_is_not_global(self):
        v = VM(); v.run('with:\n    x = 10\n')
        self.assertNotIn('x', v.globals.cells)

    def test_functional_with_returns_value(self):
        v = VM(); v.run('with make:\n    x = 10\n    return x\nview(make())\n')
        self.assertEqual(v.output, ['10'])

    def test_recursion_has_independent_frames(self):
        v = VM(); v.run('func f(n):\n    if n <= 0:\n        return 1\n    return n * f(n - 1)\nview(f(5))\n')
        self.assertEqual(v.output, ['120'])

    def test_struct_both_access_forms(self):
        v = VM(); v.run('s = struct()\ns["name"] = "LAH"\nview(s.name)\nview(s["name"])\n')
        self.assertEqual(v.output, ['LAH', 'LAH'])

    def test_cost_members_share_storage(self):
        v = VM(); v.run('cost Data = {i: 0, f: 0.0}\ndata = Data()\ndata.i = 10\n')
        with self.assertRaises(CostError): v.run('view(data.f)\n')

    def test_enum_member_lookup(self):
        e = EnumObject({'RED': 0, 'GREEN': 1})
        self.assertEqual(attr_get(e, 'GREEN').payload, 1)

    def test_heap_has_explicit_lifetime(self):
        h = Heap(); ident = h.allocate(StructObject())
        self.assertIn(ident, h.objects); h.release(ident); self.assertNotIn(ident, h.objects)

    def test_error_hierarchy(self):
        for cls in (FreezeError, RefError, TypeError_, NameError_, ValueError_, IndexError_, KeyError_, ZeroDivisionError_, ImportError_, CostError, ScopeError):
            self.assertTrue(issubclass(cls, CenterError))

class BytecodeConformance(unittest.TestCase):
    def test_versioned_instruction_objects(self):
        c = Chunk(); i = c.emit(Op.CONST, c.const(1)); self.assertIsInstance(c.code[i], Instruction)
        self.assertEqual(c.code[i].op, Op.CONST)

    def test_arithmetic_stack_effect(self):
        v = VM(); c = Chunk(); c.emit(Op.CONST, c.const(2)); c.emit(Op.CONST, c.const(3)); c.emit(Op.ADD); c.emit(Op.RETURN)
        self.assertEqual(v._exec(c, v.globals).payload, 5)

    def test_jump_targets_instruction_boundaries(self):
        c = Compiler().compile(parse('x = false\nif x:\n    view("bad")\nelse:\n    view("ok")\n'))
        targets = [i.arg for i in c.code if i.op in (Op.JUMP, Op.JUMP_IF_FALSE, Op.JUMP_IF_TRUE) and isinstance(i.arg, int)]
        self.assertTrue(all(0 <= t <= len(c.code) for t in targets))

    def test_call_and_return_stack_effect(self):
        v = VM(); v.run('func add(a, b):\n    return a + b\nview(add(2, 3))\n'); self.assertEqual(v.output, ['5'])

    def test_create_ref_opcode(self):
        c = Chunk(); c.emit(Op.CONST, c.const(4)); c.emit(Op.STORE, ('x', None, False, False)); c.emit(Op.CREATE_REF, 'x'); c.emit(Op.RETURN)
        r = VM()._exec(c, VM().globals)
        self.assertIsInstance(r, Reference)

    def test_load_and_store_ref_opcodes(self):
        vm = VM(); cell = vm.globals.define('x', wrap(1)); ref = Reference(cell)
        c = Chunk(); c.emit(Op.CONST, c.const(ref)); c.emit(Op.LOAD_REF); c.emit(Op.RETURN)
        self.assertEqual(vm._exec(c, vm.globals).payload, 1)
        c = Chunk(); c.emit(Op.CONST, c.const(ref)); c.emit(Op.CONST, c.const(9)); c.emit(Op.STORE_REF); c.emit(Op.HALT)
        vm._exec(c, vm.globals); self.assertEqual(cell.value.payload, 9)

    def test_array_opcode(self):
        c = Chunk(); c.emit(Op.CONST, c.const(1)); c.emit(Op.CONST, c.const(2)); c.emit(Op.CREATE_ARRAY, 2); c.emit(Op.RETURN)
        result = VM()._exec(c, VM().globals)
        self.assertEqual(result.kind, Kind.ARRAY); self.assertEqual([x.payload for x in result.payload], [1, 2])

    def test_zero_division_is_noyaba_error(self):
        vm = VM()
        with self.assertRaises(ZeroDivisionError_): vm.binary(Op.DIV, wrap(1), wrap(0))

    def test_uncaught_exception_propagates(self):
        with self.assertRaises(CenterError): VM().run('raise "boom"\n')

    def test_exception_handler_transfers_control(self):
        v = VM(); v.run('try:\n    raise "boom"\nexcept CenterError:\n    view("caught")\n')
        self.assertEqual(v.output, ['caught'])

    def test_create_destroy_env_opcodes(self):
        c = Chunk(); c.emit(Op.CREATE_ENV); c.emit(Op.CONST, c.const(1)); c.emit(Op.STORE, ('x', None, False, False)); c.emit(Op.DESTROY_ENV); c.emit(Op.HALT)
        vm = VM(); vm._exec(c, vm.globals); self.assertNotIn('x', vm.globals.cells)

    def test_no_python_eval_in_execution_path(self):
        import inspect, noyaba.vm as vm_mod
        self.assertNotIn('eval(', inspect.getsource(vm_mod))

class VersionConformance(unittest.TestCase):
    def test_version_identifiers(self):
        import noyaba
        self.assertEqual(noyaba.LANGUAGE_VERSION, '1.3')
        self.assertEqual(noyaba.VM_VERSION, '1.0')
        self.assertEqual(noyaba.BYTECODE_VERSION, 1)

if __name__ == '__main__': unittest.main()
