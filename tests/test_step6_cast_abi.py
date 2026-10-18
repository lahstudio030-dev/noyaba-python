import unittest
from noyaba.vm import VM
from noyaba.runtime import NativeAdapter,TypeError_,ValueError_,SystemError_

class CastAbiTests(unittest.TestCase):
 def test_explicit_casts(self):
  v=VM(); v.run('view(int(3.9))\nview(float(2))\nview(bool(0))\nview(str(7))\n')
  self.assertEqual(v.output,['3','2.0','false','7'])
 def test_invalid_cast_and_overflow(self):
  with self.assertRaises(TypeError_): VM().run('int("bad")\n')
  with self.assertRaises(ValueError_): VM().run('int(9223372036854775808)\n')
 def test_native_adapter_registry_and_version(self):
  v=VM(); a=NativeAdapter('inc',lambda x: x+1,1,'borrowed'); v.register_native(a)
  self.assertIs(v.globals.get('inc'),a)
  self.assertEqual(a.call([2],v).payload,3)
  with self.assertRaises(SystemError_): a.call([2],v,2)

if __name__=='__main__':unittest.main()
