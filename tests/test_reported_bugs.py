import unittest
from noyaba.vm import VM
from noyaba.parser import parse
from noyaba.runtime import CenterError, CostError, InstanceObject, NameError_

class ReportedBugs(unittest.TestCase):
 def runv(self,src):
  v=VM(); v.run(src); return v
 def test_cost_inactive_member_report(self):
  with self.assertRaises(CostError): self.runv('cost Data = {i: 0, f: 0.0}\ndata = Data()\ndata.f = 10\nview(data.i)\n')
 def test_class_repr_report(self):
  v=self.runv('class demo:\n    func __init__(self, x, y):\n        self.x = x\n        self.y = y\n    func __repr__(self): return str(self.x + self.y)\nview(demo(9, 9))\n')
  self.assertEqual(v.output,['18'])
 def test_duplicate_except_rejected(self):
  with self.assertRaises(SyntaxError): parse('try:\n    9/0\nexcept except CenterError as e:\n    view(e)\n')
 def test_undefined_name_can_be_caught(self):
  v=self.runv('try:\n    view(value)\nexcept CenterError as e:\n    view(e)\nview("hello")\n')
  self.assertEqual(v.output,['value','hello'])
 def test_break_continue_report(self):
  v=self.runv('x=[1,2,3,4,5,6,7,8,9,10]\nfor i in x:\n    if i == 5:\n        view("Center")\n        continue\n    elif i == 10:\n        view("Complite")\n        break\n    else:\n        if i % 2 == 0:\n            view(i)\n        else:\n            view("-")\n')
  self.assertEqual(v.output,['-','2','-','4','Center','6','-','8','-','Complite'])
 def test_trigger_boolean_cases_report(self):
  v=self.runv('x=[1,2,3,4,5,6,7,8,9,10]\nfor i in x:\n    trigger i:\n        case i == 5:\n            view("center")\n        case i == 10:\n            view("complite")\n        default:\n            if i % 2 == 0:\n                view(i)\n            else:\n                view("-")\n')
  self.assertEqual(v.output,['-','2','-','4','center','6','-','8','-','complite'])

if __name__=='__main__': unittest.main()
