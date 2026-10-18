import unittest
from noyaba.vm import VM
from noyaba.runtime import TypeError_,KeyError_

class FixedStructTests(unittest.TestCase):
 def test_fixed_struct_valid(self):
  v=VM(); v.run('struct Person:\n    name: str\n    age: int\np = Person({"name": "LAH", "age": 20})\nview(p.name)\nview(p.age)\n')
  self.assertEqual(v.output,['LAH','20'])
 def test_fixed_struct_wrong_type(self):
  with self.assertRaises(TypeError_): VM().run('struct Person:\n    age: int\np = Person({"age": "bad"})\n')
 def test_fixed_struct_missing_unknown(self):
  with self.assertRaises(KeyError_): VM().run('struct Person:\n    age: int\np = Person({})\n')
  with self.assertRaises(KeyError_): VM().run('struct Person:\n    age: int\np = Person({"age": 1, "x": 2})\n')
 def test_fixed_struct_mutation_type(self):
  with self.assertRaises(TypeError_): VM().run('struct Person:\n    age: int\np = Person({"age": 1})\np.age = "bad"\n')

if __name__=='__main__':unittest.main()
