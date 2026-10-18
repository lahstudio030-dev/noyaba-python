import unittest

from noyaba.vm import VM
from noyaba.runtime import TypeError_


class ConditionFlowTests(unittest.TestCase):
    def test_not_comparison_precedence_and_elif_membership(self):
        vm = VM()
        vm.run('''x = [1, 2]
if not x[0] == 2:
    view("if")
elif 2 in x:
    view("elif")
''')
        self.assertEqual(vm.output, ['if'])

    def test_elif_membership_branch(self):
        vm = VM()
        vm.run('''x = [1, 2]
if x[0] == 2:
    view("wrong")
elif 2 in x:
    view("elif")
else:
    view("wrong2")
''')
        self.assertEqual(vm.output, ['elif'])

    def test_in_and_not_in_for_arrays(self):
        vm = VM()
        vm.run('''x = [1, 2]
view(2 in x)
view(3 in x)
view(2 not in x)
view(3 not in x)
''')
        self.assertEqual(vm.output, ['true', 'false', 'false', 'true'])

    def test_not_binds_below_comparison_but_above_logical(self):
        vm = VM()
        vm.run('''view(not 1 == 2)
view(not false and true)
view(not true or true)
''')
        self.assertEqual(vm.output, ['true', 'true', 'true'])

    def test_membership_rejects_non_collection_rhs(self):
        with self.assertRaises(TypeError_):
            VM().run('view(1 in 2)')

    def test_if_elif_else_is_exclusive(self):
        vm = VM()
        vm.run('''if false:
    view("wrong")
elif true:
    view("elif")
else:
    view("wrong2")
''')
        self.assertEqual(vm.output, ['elif'])


if __name__ == '__main__':
    unittest.main()
