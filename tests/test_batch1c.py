import unittest

from noyaba.vm import VM


class Batch1CShortCircuitTests(unittest.TestCase):
    def test_and_skips_rhs_when_left_is_false(self):
        vm = VM()
        vm.run('x=false\nview(x and missing_name)')
        self.assertEqual(vm.output, ['false'])

    def test_or_skips_rhs_when_left_is_true(self):
        vm = VM()
        vm.run('x=true\nview(x or missing_name)')
        self.assertEqual(vm.output, ['true'])

    def test_array_double_or_is_not_short_circuited(self):
        vm = VM()
        vm.run('view([1,2] || [4,5])')
        self.assertEqual(vm.output, ['[5, 7]'])

    def test_scalar_logical_results_remain_boolean(self):
        vm = VM()
        vm.run('view(0 and 4)\nview(2 or 0)')
        self.assertEqual(vm.output, ['false', 'true'])


class Batch1CExceptionInsideExceptTests(unittest.TestCase):
    def test_raise_inside_handler_reaches_outer_handler(self):
        vm = VM()
        vm.run('''try:
    try:
        raise "inner"
    except CenterError:
        raise "handler"
except CenterError as e:
    view(e)
''')
        self.assertEqual(vm.output, ['handler'])

    def test_runtime_error_inside_handler_reaches_outer_handler(self):
        vm = VM()
        vm.run('''try:
    try:
        raise "inner"
    except CenterError:
        1 / 0
except ZeroDivisionError as e:
    view(e)
''')
        self.assertEqual(vm.output, ['division by zero'])

    def test_nested_handler_success_is_unchanged(self):
        vm = VM()
        vm.run('''try:
    try:
        raise "inner"
    except CenterError:
        view("recovered")
except CenterError:
    view("wrong")
''')
        self.assertEqual(vm.output, ['recovered'])


if __name__ == '__main__':
    unittest.main()
