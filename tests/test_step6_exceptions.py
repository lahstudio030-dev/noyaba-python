import unittest
from noyaba.vm import VM
from noyaba.runtime import CenterError

class ExceptionTests(unittest.TestCase):
 def test_exact_and_as_binding(self):
  v=VM(); v.run('try:\n    raise "boom"\nexcept CenterError as e:\n    view(e)\n')
  self.assertEqual(v.output,['boom'])
 def test_order_and_catch_all(self):
  v=VM(); v.run('try:\n    raise "boom"\nexcept ValueError_:\n    view("wrong")\nexcept:\n    view("fallback")\n')
  self.assertEqual(v.output,['fallback'])
 def test_unmatched_propagates(self):
  with self.assertRaises(CenterError): VM().run('try:\n    raise "boom"\nexcept ValueError_:\n    view("wrong")\n')
 def test_caller_frame_propagation(self):
  v=VM(); v.run('func f():\n    raise "boom"\ntry:\n    f()\nexcept CenterError:\n    view("caught")\n')
  self.assertEqual(v.output,['caught'])

if __name__=='__main__':unittest.main()
