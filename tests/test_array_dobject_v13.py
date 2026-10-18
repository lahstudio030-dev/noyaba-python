import unittest
from noyaba.vm import VM
from noyaba.runtime import CenterError, LengthError, TypeError_


class ArrayDObjectV13Tests(unittest.TestCase):
    def runv(self, source):
        vm = VM(); vm.run(source); return vm

    def test_array_is_indexed_and_sliceable(self):
        vm = self.runv('a=[1,2,3,4,5]\nview(a[-1])\nview(a[1:4])\nview(a[::2])\n')
        self.assertEqual(vm.output, ['5', '[2, 3, 4]', '[1, 3, 5]'])

    def test_array_numeric_and_bitwise_modes(self):
        vm = self.runv('view([1,2,3]+5)\nview([1,2]+[4,5])\nview([1,2]|[4,5])\nview([1,2]<<5)\n')
        self.assertEqual(vm.output, ['[6, 7, 8]', '[5, 7]', '[5, 7]', '[32, 64]'])

    def test_array_length_and_non_numeric_errors(self):
        with self.assertRaises(LengthError): VM().run('view([1,2]+[3])')
        with self.assertRaises(TypeError_): VM().run('view([1,2]+"x")')
        with self.assertRaises(TypeError_): VM().run('a=[1,2]\na += 3')

    def test_array_plus_equals_is_join(self):
        vm = self.runv('a=[1,2]\na += [3,"x"]\nview(a)\n')
        self.assertEqual(vm.output, ['[1, 2, 3, x]'])
        with self.assertRaises(TypeError_):
            VM().run('view([1,"x"] + [2,"y"])')

    def test_only_array_plus_equals_is_augmented_assignment(self):
        for op in ('-=', '*=', '/=', '^='):
            with self.subTest(op=op):
                with self.assertRaises(Exception):
                    VM().run(f'a=[1,2]\na {op} [3,4]')

    def test_nested_dobject_array_composition_and_mutation(self):
        vm = self.runv('data={user:{name:"Bob", age:20}, scores:[10,20]}\nview(data.user.age)\ndata.user.age=21\nview(data.user.age)\nview(data.scores[1])\n')
        self.assertEqual(vm.output, ['20', '21', '20'])

    def test_dobject_methods(self):
        vm = self.runv('d=dobject({x:1})\nd.set("y", 2)\nview(d.has("x"))\nview(d.get("y"))\nd.remove("x")\nview(d.has("x"))\n')
        self.assertEqual(vm.output, ['true', '2', 'false'])

    def test_parentheses_do_not_create_tuple(self):
        with self.assertRaises(Exception): VM().run('x=(1,2,3)')


if __name__ == '__main__':
    unittest.main()
