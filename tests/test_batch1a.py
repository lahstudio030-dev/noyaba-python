import unittest

from noyaba.vm import VM
from noyaba.runtime import CenterError, TypeError_, LengthError


class Batch1AArrayOrTests(unittest.TestCase):
    def runv(self, source):
        vm = VM()
        vm.run(source)
        return vm

    def test_array_double_or_uses_bitwise_array_mode(self):
        vm = self.runv('view([1, 2] || [4, 5])')
        self.assertEqual(vm.output, ['[5, 7]'])

    def test_scalar_double_or_remains_logical(self):
        vm = self.runv('view(false || true)\nview(0 || 3)')
        self.assertEqual(vm.output, ['true', 'true'])

    def test_array_double_or_validates_lengths_and_integer_elements(self):
        with self.assertRaises(LengthError):
            self.runv('view([1] || [2, 3])')
        with self.assertRaises(TypeError_):
            self.runv('view([1, "x"] || [2, 3])')


class Batch1AUnaryTests(unittest.TestCase):
    def runv(self, source):
        vm = VM()
        vm.run(source)
        return vm

    def test_integer_bitwise_not(self):
        vm = self.runv('view(~0)\nview(~1)\nview(~5)\nview(~(-1))')
        self.assertEqual(vm.output, ['-1', '-2', '-6', '0'])

    def test_bitwise_not_rejects_non_integer(self):
        with self.assertRaises(TypeError_):
            self.runv('view(~true)')


class Batch1APublicExceptionTests(unittest.TestCase):
    def test_zero_division_public_name(self):
        vm = VM()
        vm.run('try:\n    1 / 0\nexcept ZeroDivisionError:\n    view("caught")')
        self.assertEqual(vm.output, ['caught'])

    def test_existing_trailing_underscore_errors_match_public_names(self):
        cases = [
            ('view(missing_name)', 'NameError'),
            ('view([1][3])', 'IndexError'),
            ('view({"x": 1}["y"])', 'KeyError'),
            ('view(1 + "x")', 'TypeError'),
        ]
        for body, public_name in cases:
            with self.subTest(public_name=public_name):
                vm = VM()
                vm.run(f'try:\n    {body}\nexcept {public_name}:\n    view("caught")')
                self.assertEqual(vm.output, ['caught'])

    def test_center_error_catch_remains_compatible(self):
        vm = VM()
        vm.run('try:\n    1 / 0\nexcept CenterError:\n    view("caught")')
        self.assertEqual(vm.output, ['caught'])


if __name__ == '__main__':
    unittest.main()
