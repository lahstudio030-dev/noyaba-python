import os
import tempfile
import unittest

from noyaba.vm import VM
from noyaba.runtime import CenterError, ValueError_


class BuiltinV13E2E(unittest.TestCase):
    def runv(self, source):
        vm = VM()
        vm.run(source)
        return vm

    def test_lazy_iteration_protocol(self):
        vm = self.runv(
            'view(count(0, 5)[4])\n'
            'view(enumerate([8, 9])[1][0])\n'
            'view(enumerate([8, 9])[1][1])\n'
            'view(zip([1, 2], [3, 4])[1][0])\n'
            'view(zip([1, 2], [3, 4])[1][1])\n'
            'view(stepview([1, 2, 3, 4, 5], 2)[2])\n'
        )
        self.assertEqual(vm.output, ['4', '1', '9', '2', '4', '5'])

    def test_binary_and_deterministic_hash(self):
        vm = self.runv(
            'view(len(binary("ab", [99])))\n'
            'view(binary("ab")[1])\n'
            'view(hash("noyaba"))\n'
            'view(hash("noyaba"))\n'
            'view(bitfix("hello", 0, 100))\n'
            'view(bitfix("hello", 1, 6))\n'
        )
        self.assertEqual(vm.output[:2], ['3', '98'])
        self.assertEqual(vm.output[2], vm.output[3])
        self.assertTrue(0 <= int(vm.output[4]) <= 100)
        self.assertTrue(1 <= int(vm.output[5]) <= 6)

    def test_dynamic_pipeline_and_math_restriction(self):
        vm = self.runv('execute("answer = 40")\nview(answer + 2)\nview(eval("2 + 3 * 4"))\n')
        self.assertEqual(vm.output, ['42', '14'])
        with self.assertRaises(CenterError):
            VM().run('eval("view(1)")')

    def test_wrapped_open_api(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        try:
            vm = self.runv(
                f'f = open({path!r}, "w")\n'
                'f.write("hello")\n'
                'f.close()\n'
                f'f = open({path!r}, "r")\n'
                'view(f.read())\n'
                'view(f.tell())\n'
                'f.close()\n'
            )
            self.assertEqual(vm.output, ['hello', '5'])
        finally:
            os.unlink(path)

    def test_invalid_new_builtin_inputs_are_center_errors(self):
        for source in ('count(1, 2, 0)', 'binary([256])', 'bitfix(1, 9, 2)', 'open(1)'):
            with self.subTest(source=source):
                with self.assertRaises(CenterError):
                    VM().run(source)


if __name__ == '__main__':
    unittest.main()
