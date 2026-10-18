import unittest

from noyaba.vm import VM
from noyaba.runtime import IndexError_


class EmptyArrayOperationTests(unittest.TestCase):
    def runv(self, source):
        vm = VM()
        vm.run(source)
        return vm

    def test_empty_array_scalar_elementwise_operations_return_empty_array(self):
        vm = self.runv('''view([] + 5)
view([] - 5)
view([] * 5)
view([] / 5)
view([] % 5)
view([] ** 2)
view([] & 1)
view([] | 1)
view([] ^ 1)
view([] << 1)
view([] >> 1)
view([] == 0)
view([] != 0)
view([] < 0)
view([] || 5)
''')
        self.assertEqual(vm.output, ['[]'] * 15)

    def test_empty_array_array_operations_remain_empty(self):
        vm = self.runv('''view([] + [])
view([] - [])
view([] | [])
view([] || [])
view([] == [])
view([] != [])
a=[]
a += []
view(a)
''')
        self.assertEqual(vm.output, ['[]'] * 7)

    def test_empty_pop_is_noyaba_index_error(self):
        with self.assertRaises(IndexError_):
            self.runv('a=[]\na.pop()')

    def test_nonempty_pop_and_existing_array_validation_are_unchanged(self):
        vm = self.runv('a=[1,2]\nview(a.pop())\nview(a)')
        self.assertEqual(vm.output, ['2', '[1]'])
        with self.assertRaises(Exception):
            self.runv('a=[]\na += 1')


if __name__ == '__main__':
    unittest.main()
