import unittest
from noyaba.vm import VM
from noyaba.parser import parse
from noyaba.compiler import Compiler

class TriggerAndMacroTests(unittest.TestCase):
    def test_trigger_first_match_default_and_no_fallthrough(self):
        v=VM(); v.run('x = 2\ntrigger x:\n    case 1:\n        view("one")\n    case 2, 3:\n        view("two")\n    case 4:\n        view("four")\n    default:\n        view("other")\n')
        self.assertEqual(v.output,['two'])
    def test_trigger_default(self):
        v=VM(); v.run('x = 9\ntrigger x:\n    case 1:\n        view("one")\n    default:\n        view("other")\n')
        self.assertEqual(v.output,['other'])
    def test_trigger_constant_duplicate_rejected(self):
        with self.assertRaises(SyntaxError): Compiler().compile(parse('x=1\ntrigger x:\n    case 1:\n        view("a")\n    case 1:\n        view("b")\n'))
    def test_macro_expression_expands_at_compile_time(self):
        v=VM(); v.run('macro twice(x): x + x\nview(twice(3))\n')
        self.assertEqual(v.output,['6'])
    def test_nested_trigger(self):
        v=VM(); v.run('x=1\ntrigger x:\n    case 1:\n        trigger x:\n            case 1:\n                view("nested")\n')
        self.assertEqual(v.output,['nested'])
    def test_recursive_macro_rejected(self):
        with self.assertRaises(SyntaxError): VM().run('macro loop(x): loop(x)\nview(loop(1))\n')

if __name__=='__main__': unittest.main()
