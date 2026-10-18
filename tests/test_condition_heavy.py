import unittest

from noyaba.vm import VM


class HeavyConditionFlowTests(unittest.TestCase):
    def runv(self, source):
        vm = VM()
        vm.run(source)
        return vm

    def test_chained_comparisons(self):
        vm = self.runv('view(1 < 2 < 3)\nview(3 < 2 < 3)\nview(1 <= 1 <= 2)\nview(1 == 1 == 1)')
        self.assertEqual(vm.output, ['true', 'false', 'true', 'true'])

    def test_chained_comparison_short_circuits_later_terms(self):
        vm = self.runv('view(3 < 2 < (1 / 0))')
        self.assertEqual(vm.output, ['false'])

    def test_chained_membership_and_comparison(self):
        vm = self.runv('x=[1,2,3]\nview(1 in x and true)\nview(1 not in x or false)')
        self.assertEqual(vm.output, ['true', 'false'])

    def test_parenthesized_mixed_logical_precedence(self):
        vm = self.runv('''view(true or false and false)
view((true or false) and false)
view(false and true or true)
view(false or true and false)
''')
        self.assertEqual(vm.output, ['true', 'false', 'true', 'false'])

    def test_nested_not_membership_and_comparison(self):
        vm = self.runv('''x=[1,2,3]
view(not (2 in x))
view(not (4 in x))
view(not 1 < 2)
view(not 2 < 1)
''')
        self.assertEqual(vm.output, ['false', 'true', 'false', 'true'])

    def test_string_and_dobject_membership(self):
        vm = self.runv('''d={name: "Noyaba", version: 13}
view("name" in d)
view("missing" not in d)
view("oya" in d.name)
''')
        self.assertEqual(vm.output, ['true', 'true', 'true'])

    def test_short_circuit_does_not_evaluate_rhs(self):
        vm = self.runv('''view(false and (1 / 0))
view(true or (1 / 0))
''')
        self.assertEqual(vm.output, ['false', 'true'])

    def test_nested_if_elif_with_complex_condition(self):
        vm = self.runv('''x=[2,4,6]
if not (1 in x) and 2 < 3 < 4:
    if 4 in x and 9 not in x:
        view("nested")
elif true:
    view("wrong")
else:
    view("wrong2")
''')
        self.assertEqual(vm.output, ['nested'])

    def test_condition_values_are_boolean(self):
        vm = self.runv('''view(typeof(1 < 2 < 3))
view(typeof(2 in [1,2]))
view(typeof(not false))
''')
        self.assertEqual(vm.output, ['BOOL', 'BOOL', 'BOOL'])


if __name__ == '__main__':
    unittest.main()
