import sys,unittest
sys.path.insert(0,'.')
from noyaba.vm import VM
from noyaba.runtime import FreezeError,RefError,CostError
class Conformance(unittest.TestCase):
 def runv(self,s):
  v=VM();v.run(s);return v
 def test_reference(self):
  v=self.runv('x = 4\nref y = x\ny = 20\nview(x)\n');self.assertEqual(v.output,['20'])
 def test_recursion(self):
  v=self.runv('func factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\nview(factorial(5))\n');self.assertEqual(v.output,['120'])
 def test_with_is_temporary(self):
  v=self.runv('with:\n    x = 10\n');self.assertNotIn('x',v.globals.cells)
 def test_functional_with(self):
  v=self.runv('with make:\n    x = 10\n    return x\nview(make())\n');self.assertEqual(v.output,['10'])
 def test_fixed_type(self):
  with self.assertRaises(Exception):self.runv('x: int = 12\nx = "bad"\n')
 def test_goto(self):
  v=self.runv('flag = false\nif flag:\n    goto start\nview("OK")\nstart:\n    view("DONE")\n');self.assertEqual(v.output,['OK','DONE'])
 def test_struct(self):
  v=self.runv('s = struct()\ns["id"] = 7\nview(s["id"])\n');self.assertEqual(v.output,['7'])
 def test_cost_shared_storage(self):
  v=self.runv('cost Data = {i: 0, f: 0.0}\ndata = Data()\ndata.i = 10\n')
  with self.assertRaises(CostError): v.run('view(data.f)\n')
if __name__=='__main__':unittest.main()
