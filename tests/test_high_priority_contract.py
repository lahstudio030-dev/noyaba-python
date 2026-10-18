import pathlib
import tempfile
import unittest

from noyaba.vm import VM
from noyaba.runtime import TypeError_


class HighPriorityContractTests(unittest.TestCase):
    def test_exception_binding_is_object(self):
        vm = VM()
        vm.run('''try:
    raise "boom"
except CenterError as e:
    view(typeof(e))
    view(isinstance(e, "exception"))
    view(e.message)
''')
        self.assertEqual(vm.output, ['EXCEPTION', 'true', 'boom'])

    def test_parent_fields_are_initialized_and_accessible(self):
        vm = VM()
        vm.run('''class Parent:
    x = 9
class Child(Parent):
    y = 2
c = Child()
view(c.x)
view(c.y)
''')
        self.assertEqual(vm.output, ['9', '2'])

    def test_imported_class_method_closes_over_module_environment(self):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            (root / 'mod.noy').write_text('''seed = 8
class A:
    func get(self):
        return seed
''')
            vm = VM(project_root=str(root))
            vm.run('''from mod import A
 a = A()
view(a.get())
'''.replace(' a =', 'a ='), str(root / 'main.noy'))
            self.assertEqual(vm.output, ['8'])

    def test_typed_dobject_copy_preserves_schema(self):
        vm = VM()
        vm.run('''d = {age as int: 45}
c = d.copy()
''')
        with self.assertRaises(TypeError_):
            vm.run('c.age = "bad"')

    def test_class_expression_defaults_are_evaluated(self):
        vm = VM()
        vm.run('''func seed():
    return 8
class A:
    x = seed()
    y = 1 + 2
a = A()
view(a.x)
view(a.y)
''')
        self.assertEqual(vm.output, ['8', '3'])

    def test_struct_expression_defaults_are_evaluated_and_typed(self):
        vm = VM()
        vm.run('''func seed():
    return 8
struct S:
    x: int = seed()
    y: int = 1 + 2
s = S({})
view(s.x)
view(s.y)
''')
        self.assertEqual(vm.output, ['8', '3'])


if __name__ == '__main__':
    unittest.main()
