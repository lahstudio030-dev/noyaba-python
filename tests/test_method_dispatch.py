import unittest
from noyaba.vm import VM

class MethodDispatchTests(unittest.TestCase):
 def runv(self,src):
  v=VM(); v.run(src); return v
 def test_str_method_is_used_by_view_and_str(self):
  v=self.runv('class demo:\n    func __init__(self, x, y):\n        self.x=x\n        self.y=y\n    func __str__(self): return str(self.x + self.y)\nd=demo(9,9)\nview(d)\nview(str(d))\nview(repr(d))\n')
  self.assertEqual(v.output,['18','18','18'])
 def test_repr_fallback_is_used_when_str_absent(self):
  v=self.runv('class demo:\n    func __init__(self, x): self.x=x\n    func __repr__(self): return str(self.x)\nview(demo(7))\nview(str(demo(8)))\n')
  self.assertEqual(v.output,['7','8'])
 def test_repr_prefers_explicit_repr_over_str(self):
  v=self.runv('class demo:\n    func __str__(self): return "str"\n    func __repr__(self): return "repr"\nd=demo()\nview(str(d))\nview(repr(d))\n')
  self.assertEqual(v.output,['str','repr'])
 def test_ordinary_method_returns_and_mutates(self):
  v=self.runv('class Counter:\n    value = 0\n    func add(self, n):\n        self.value=self.value+n\n        return self.value\nc=Counter()\nview(c.add(2))\nview(c.add(3))\nview(c.value)\n')
  self.assertEqual(v.output,['2','5','5'])
 def test_inherited_and_overridden_methods(self):
  v=self.runv('class Parent:\n    func speak(self): return "parent"\nclass Child(Parent):\n    func speak(self): return "child"\n    func parent_speak(self): return super.speak()\nc=Child()\nview(c.speak())\nview(c.parent_speak())\n')
  self.assertEqual(v.output,['child','parent'])
 def test_method_as_value_remains_bound(self):
  v=self.runv('class A:\n    func value(self): return 11\na=A()\nf=a.value\nview(f())\n')
  self.assertEqual(v.output,['11'])

if __name__=='__main__': unittest.main()
