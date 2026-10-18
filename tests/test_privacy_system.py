import pathlib
import tempfile
import unittest

from noyaba.vm import VM
from noyaba.runtime import PrivacyError


class PrivacySystemTests(unittest.TestCase):
    def test_single_underscore_cannot_be_imported_but_public_wrapper_works(self):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            (root / 'export_file.noy').write_text('''func _fact(n: int):
    if n == 1 or n == 2:
        return n
    return n * _fact(n - 1)
func export_fact(n: int = 5): return _fact(n)
''')
            source = '''try:
    from export_file import _fact as fact
except CenterError:
    from export_file import export_fact as fact
view(fact(8))
'''
            with self.assertRaises(PrivacyError):
                VM(project_root=str(root)).run('from export_file import _fact as fact\n', str(root / 'main.noy'))
            vm = VM(project_root=str(root))
            vm.run(source, str(root / 'main.noy'))
            self.assertEqual(vm.output, ['40320'])

    def test_double_underscore_global_is_not_directly_readable(self):
        with self.assertRaises(PrivacyError):
            VM().run('__TRUE_OR_FALSE = true\nview(__TRUE_OR_FALSE)')

    def test_double_underscore_global_is_visible_inside_function(self):
        vm = VM()
        vm.run('''__TRUE_OR_FALSE = true
func demo():
    if __TRUE_OR_FALSE:
        view("is True")
        __TRUE_OR_FALSE = false
    else:
        view("is False")
        __TRUE_OR_FALSE = true
demo()
demo()
''')
        self.assertEqual(vm.output, ['is True', 'is False'])

    def test_double_underscore_global_is_visible_inside_class_method(self):
        vm = VM()
        vm.run('''__FLAG = true
class A:
    func check(self):
        if __FLAG:
            return "yes"
        return "no"
a = A()
view(a.check())
''')
        self.assertEqual(vm.output, ['yes'])

    def test_public_import_alias_is_supported(self):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            (root / 'm.noy').write_text('value = 17\n')
            vm = VM(project_root=str(root))
            vm.run('from m import value as answer\nview(answer)\n', str(root / 'main.noy'))
            self.assertEqual(vm.output, ['17'])

    def test_single_underscore_local_name_remains_local_to_module(self):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            (root / 'm.noy').write_text('_hidden = 9\npublic = 3\n')
            with self.assertRaises(PrivacyError):
                VM(project_root=str(root)).run('from m import _hidden\n', str(root / 'main.noy'))
            vm = VM(project_root=str(root))
            vm.run('from m import public\nview(public)\n', str(root / 'main.noy'))
            self.assertEqual(vm.output, ['3'])


if __name__ == '__main__':
    unittest.main()
