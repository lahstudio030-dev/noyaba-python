import tempfile
from pathlib import Path
import unittest
from noyaba.vm import VM
from noyaba.parser import parse
from noyaba.runtime import CenterError

class MultilineCollectionTests(unittest.TestCase):
 def test_multiline_list(self):
  v=VM(); v.run('x = [\n    1,\n    2,\n    3\n]\nview(x)\n'); self.assertEqual(v.output,['[1, 2, 3]'])
 def test_nested_multiline_list(self):
  v=VM(); v.run('x = [\n    1,\n    [\n        2,\n        3,\n    ],\n    4,\n]\nview(x)\n'); self.assertEqual(v.output,['[1, [2, 3], 4]'])
 def test_multiline_call_and_dobject(self):
  v=VM(); v.run('x = array(\n    1,\n    2,\n    3,\n)\nd = {\n    "a": 1,\n    "b": [2, 3],\n}\nview(x)\nview(d["b"])\n'); self.assertEqual(v.output,['[1, 2, 3]','[2, 3]'])
 def test_unclosed_collection_is_rejected(self):
  with self.assertRaises(SyntaxError): parse('x = [\n  1\n')

class SingleLineBlockTests(unittest.TestCase):
 def test_if_single_line_and_following_statement(self):
  v=VM(); v.run('if true: view("A")\nx = 4\nview(x)\n'); self.assertEqual(v.output,['A','4'])
 def test_else_elif_single_line(self):
  v=VM(); v.run('if false: view("bad")\nelif true: view("elif")\nelse: view("else")\n'); self.assertEqual(v.output,['elif'])
 def test_while_single_line(self):
  v=VM(); v.run('x = 3\nwhile x: x = x - 1\nview(x)\n'); self.assertEqual(v.output,['0'])
 def test_indented_and_compact_are_equivalent(self):
  a=VM(); a.run('x = 1\nif x: view("yes")\n')
  b=VM(); b.run('x = 1\nif x:\n    view("yes")\n')
  self.assertEqual(a.output,b.output)

class ExceptionContinuationTests(unittest.TestCase):
 def test_arithmetic_catch_continues(self):
  v=VM(); v.run('try:\n    9 / 0\nexcept CenterError as e:\n    view("caught")\nview("continued")\n'); self.assertEqual(v.output,['caught','continued'])
 def test_no_exception_skips_handler(self):
  v=VM(); v.run('try:\n    x = 10\nexcept CenterError:\n    view("wrong")\nview(x)\n'); self.assertEqual(v.output,['10'])
 def test_function_try_catch_continues(self):
  v=VM(); v.run('func test():\n    try:\n        9 / 0\n    except CenterError:\n        view("caught")\n    return 7\nx = test()\nview(x)\n'); self.assertEqual(v.output,['caught','7'])
 def test_unmatched_still_propagates(self):
  with self.assertRaises(CenterError): VM().run('try:\n    9 / 0\nexcept ValueError_:\n    view("wrong")\n')

class RealFileIntegrationTests(unittest.TestCase):
 def test_combined_real_noy_file(self):
  source='''x = [\n    1,\n    2,\n    3\n]\nif x: view("list exists")\ntry:\n    9 / 0\nexcept CenterError as e:\n    view("error caught")\nx = 4\nview(x)\n'''
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'integration.noy'; p.write_text(source)
   v=VM(project_root=d); v.run(p.read_text(),str(p)); self.assertEqual(v.output,['list exists','error caught','4'])

if __name__=='__main__': unittest.main()
