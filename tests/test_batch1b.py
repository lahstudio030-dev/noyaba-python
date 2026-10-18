import pathlib
import tempfile
import unittest

from noyaba.vm import VM
from noyaba.runtime import TypeError_


class Batch1BEnumTests(unittest.TestCase):
    def test_bracket_enum_declaration_and_member_lookup(self):
        vm = VM()
        vm.run('enum Color = [RED: 255, GREEN: 128]\nview(Color.RED)\nview(typeof(Color))\nview(isinstance(Color, "enum"))')
        self.assertEqual(vm.output, ['255', 'ENUM', 'true'])

    def test_enum_inside_array_and_dobject(self):
        vm = VM()
        vm.run('enum Color = [RED: 255]\na=[Color.RED]\nd={color: Color.RED}\nview(a[0])\nview(d.color)')
        self.assertEqual(vm.output, ['255', '255'])


class Batch1BTypedDObjectTests(unittest.TestCase):
    def test_typed_dobject_keeps_dobject_identity(self):
        vm = VM()
        vm.run('d={age as int: 45, name as str: "N"}\nview(typeof(d))\nview(isinstance(d, "dobject"))\nd.age=46\nd.set("name", "M")\nview(d.age)\nview(d.name)')
        self.assertEqual(vm.output, ['DOBJECT', 'true', '46', 'M'])

    def test_typed_dobject_rejects_wrong_assignment(self):
        with self.assertRaises(TypeError_):
            VM().run('d={age as int: 45}\nd.age="bad"')
        with self.assertRaises(TypeError_):
            VM().run('d={age as int: 45}\nd.set("age", "bad")')


class Batch1BInsertTests(unittest.TestCase):
    def test_insert_uses_object_then_index(self):
        vm = VM()
        vm.run('a=[1,2,3]\na.insert(99,1)\nview(a)')
        self.assertEqual(vm.output, ['[1, 99, 2, 3]'])

    def test_insert_requires_integer_index(self):
        with self.assertRaises(TypeError_):
            VM().run('a=[1,2]\na.insert(9, "bad")')


class Batch1BModuleTests(unittest.TestCase):
    def test_noy_module_resolution_and_ny_compatibility(self):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            (root / 'modern.noy').write_text('value=42\n')
            (root / 'legacy.ny').write_text('value=7\n')
            modern = root / 'modern_main.noy'
            legacy = root / 'legacy_main.noy'
            vm = VM(project_root=str(root))
            vm.run('from modern import value\nview(value)\n', str(modern))
            self.assertEqual(vm.output, ['42'])
            vm = VM(project_root=str(root))
            vm.run('from legacy import value\nview(value)\n', str(legacy))
            self.assertEqual(vm.output, ['7'])


if __name__ == '__main__':
    unittest.main()
