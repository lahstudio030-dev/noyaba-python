import unittest
from noyaba.vm import VM

class ObjectTests(unittest.TestCase):
 def test_class_constructor_and_bound_method(self):
  v=VM(); v.run('class Person:\n    name\n    func __init__(self, name):\n        self.name = name\n    func greet(self):\n        return self.name\np = Person("LAH")\nview(p.greet())\n')
  self.assertEqual(v.output,['LAH'])
 def test_single_inheritance_and_override(self):
  v=VM(); v.run('class Parent:\n    func greet(self):\n        return "parent"\nclass Child(Parent):\n    func greet(self):\n        return "child"\np = Child()\nview(p.greet())\n')
  self.assertEqual(v.output,['child'])
 def test_super_preserves_instance(self):
  v=VM(); v.run('class Parent:\n    func greet(self):\n        return self.name\nclass Child(Parent):\n    name\n    func __init__(self, name):\n        self.name = name\n    func greet(self):\n        return super.greet()\np = Child("LAH")\nview(p.greet())\n')
  self.assertEqual(v.output,['LAH'])
 def test_invalid_field_access(self):
  with self.assertRaises(Exception): VM().run('class Person:\n    name\np = Person()\nview(p.missing)\n')
 def test_unknown_class_field_write_rejected(self):
  with self.assertRaises(Exception): VM().run('class Person:\n    name\np = Person()\np.missing = 1\n')

if __name__=='__main__':unittest.main()
