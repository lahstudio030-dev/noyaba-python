import unittest
from noyaba.vm import VM
from noyaba.runtime import CenterError,TypeError_,ValueError_

class BuiltinConformance(unittest.TestCase):
 def runv(self,src):
  v=VM(); v.run(src); return v
 def test_type_conversion_and_type_queries(self):
  v=self.runv('view(int(10))\nview(float(10))\nview(str(123))\nview(bool(0))\nview(typeof(123))\nview(typeof("abc"))\nview(isinstance(123, int))\nview(isinstance("abc", str))\n')
  self.assertEqual(v.output,['10','10.0','123','false','INT','STRING','true','true'])
 def test_collections_len_index_and_mutation(self):
  v=self.runv('a=array(1,2,3)\nl=list(a)\nd=dobject({"x": 7})\nview(len(a))\nview(len(l))\nview(d.x)\nl[1]=9\nview(l[1])\n')
  self.assertEqual(v.output,['3','3','7','9'])
 def test_numeric_and_string_utilities(self):
  v=self.runv('view(pow(2,3))\nview(abs(-4))\nview(round(2.6))\nview(max(1,5,3))\nview(min(1,5,3))\nview(ord("A"))\nview(char(65))\nview(hex(15))\nview(oct(8))\nview(ascii("A"))\n')
  self.assertEqual(v.output,['8','4','3','5','1','65','A','0xf','0o10',"'A'"])
 def test_callable_and_class_integration(self):
  v=self.runv('class Demo:\n    func get(self): return 10\nd=Demo()\nview(callable(d.get))\nview(typeof(d))\nview(d.get())\n')
  self.assertEqual(v.output,['true','CLASS','10'])
 def test_invalid_builtin_arguments_are_noyaba_errors(self):
  cases=['int("bad")','char("A")','ord("AB")','len(1)','list(1)','struct(1)','max()']
  for src in cases:
   with self.subTest(src=src):
    with self.assertRaises(CenterError): VM().run(src)
 def test_overflow_remains_noyaba_error(self):
  with self.assertRaises(ValueError_): VM().run('int(9223372036854775808)')
 def test_string_to_int_is_rejected_by_frozen_cast_contract(self):
  with self.assertRaises(TypeError_): VM().run('int("10")')

if __name__=='__main__': unittest.main()
