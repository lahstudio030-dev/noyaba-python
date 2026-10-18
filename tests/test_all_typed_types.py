import unittest
from noyaba.vm import VM
from noyaba.runtime import TypeError_,Kind

class AllTypedTypes(unittest.TestCase):
 def assert_rejects(self,source):
  with self.assertRaises(TypeError_): VM().run(source)
 def test_primitive_initializer_and_reassignment_matrix(self):
  cases=[
   ('int','1','2','"bad"'),
   ('float','1.5','2.5','"bad"'),
   ('str','"a"','"b"','2'),
   ('bool','true','false','1'),
   ('char','char(65)','char(66)','"bad"'),
   ('list','list(array(1,2))','list(array(3,4))','1'),
   ('array','array(1,2)','array(3,4)','1'),
  ]
  for typ,initial,same,bad in cases:
   with self.subTest(typ=typ):
    v=VM(); v.run(f'x: {typ} = {initial}\nx = {same}\n'); self.assertIn('x',v.globals.cells)
    self.assert_rejects(f'x: {typ} = {initial}\nx = {bad}\n')
    self.assert_rejects(f'x: {typ} = {bad}\n')
 def test_primitive_function_local_and_reference_matrix(self):
  cases=[('int','1','"bad"'),('float','1.5','"bad"'),('str','"a"','1'),('bool','true','1'),('char','char(65)','"bad"'),('list','list(1)','1'),('array','array(1)','1')]
  for typ,initial,bad in cases:
   with self.subTest(typ=typ):
    self.assert_rejects(f'func f():\n    x: {typ} = {initial}\n    x = {bad}\nf()\n')
    self.assert_rejects(f'x: {typ} = {initial}\nref y = x\ny = {bad}\n')
 def test_object_backed_types(self):
  v=VM(); v.run('x: struct = struct({"n": 1})\ny: dobject = dobject({"n": 1})\n'); self.assertIn('x',v.globals.cells); self.assertIn('y',v.globals.cells)
  self.assert_rejects('x: struct = 1\n')
  self.assert_rejects('y: dobject = 1\n')
  self.assert_rejects('struct S:\n    n: int\nx: S = S({"n": 1})\nx = 3\n')
  self.assert_rejects('class C:\n    n: int\nx: C = C()\nx = 3\n')
  self.assert_rejects('class C:\n    n: int\nc=C()\nx: C = c\nx = C\n')
 def test_char_is_distinct_runtime_kind(self):
  v=VM(); v.run('x: char = char(65)\nview(x)\n'); self.assertEqual(v.globals.cells['x'].value.kind,Kind.CHAR); self.assertEqual(v.output,['A'])

if __name__=='__main__': unittest.main()
