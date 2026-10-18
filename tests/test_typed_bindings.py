import unittest
from noyaba.vm import VM
from noyaba.runtime import TypeError_

class TypedBindingTests(unittest.TestCase):
 def test_typed_initializer_rejects_wrong_type(self):
  with self.assertRaises(TypeError_): VM().run('x: str = 7\n')
 def test_typed_reassignment_rejects_wrong_type(self):
  with self.assertRaises(TypeError_): VM().run('x: str = "h"\nx = 7\n')
 def test_typed_reassignment_accepts_same_type(self):
  v=VM(); v.run('x: str = "h"\nx = "ok"\nview(x)\n'); self.assertEqual(v.output,['ok'])
 def test_typed_reference_cannot_bypass_type(self):
  with self.assertRaises(TypeError_): VM().run('x: str = "h"\nref y = x\ny = 7\n')
 def test_function_local_typed_binding_is_fixed(self):
  with self.assertRaises(TypeError_): VM().run('func f():\n    x: str = "h"\n    x = 7\nf()\n')
 def test_class_typed_field_rejects_wrong_type(self):
  with self.assertRaises(TypeError_): VM().run('class C:\n    x: str\nc=C()\nc.x=7\n')
 def test_class_typed_field_accepts_correct_type(self):
  v=VM(); v.run('class C:\n    x: str\nc=C()\nc.x="ok"\nview(c.x)\n'); self.assertEqual(v.output,['ok'])
 def test_class_typed_default_is_validated(self):
  with self.assertRaises(TypeError_): VM().run('class C:\n    x: str = 7\nc=C()\n')

if __name__=='__main__': unittest.main()
