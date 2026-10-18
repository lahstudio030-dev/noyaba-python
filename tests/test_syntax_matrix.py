import unittest
from noyaba.vm import VM
from noyaba.parser import parse
from noyaba.runtime import CenterError,TypeError_,NameError_

class StatementSyntaxMatrix(unittest.TestCase):
 def runv(self,src):
  v=VM(); v.run(src); return v
 def test_assignments_and_annotations(self):
  v=self.runv('a=1\nb: int = 2\nc: float = 2.5\nfrozen: freeze = 3\nview(a+b)\nview(c)\n')
  self.assertEqual(v.output,['3','2.5'])
 def test_empty_and_nested_collections(self):
  v=self.runv('a=[]\nb={}\nc=[{}, [], (1)]\nview(a)\nview(b)\nview(c)\n')
  self.assertEqual(v.output,['[]','{}','[{}, [], 1]'])
 def test_expression_precedence_and_unary(self):
  v=self.runv('view(-2 + 3 * 4)\nview(not false and true)\nview(2 ** 3 ** 2)\n')
  self.assertEqual(v.output,['10','true','512'])
 def test_attribute_index_and_assignment(self):
  v=self.runv('s=struct()\ns["x"]=1\ns.x=2\nview(s.x)\nview(s["x"])\n')
  self.assertEqual(v.output,['2','2'])
 def test_comments_blank_lines_and_tabs(self):
  v=self.runv('# top\n\nif true:\n\t# inner\n\tview("ok")\n\nview("done")\n')
  self.assertEqual(v.output,['ok','done'])
 def test_all_loop_forms_and_for(self):
  v=self.runv('x=0\nwhile x < 2: x=x+1\ntotal=0\nfor item in [1,2,3]:\n    total=total+item\nview(x)\nview(total)\n')
  self.assertEqual(v.output,['2','6'])
 def test_function_forms_and_returns(self):
  v=self.runv('func zero():\n    return\nfunc one(a): return a\nview(zero())\nview(one(4))\n')
  self.assertEqual(v.output,['null','4'])
 def test_control_and_exception_forms(self):
  v=self.runv('try: view("safe")\nexcept CenterError: view("bad")\nif false: view("bad")\nelse: view("else")\n')
  self.assertEqual(v.output,['safe','else'])
 def test_struct_enum_cost_class_forms(self):
  v=self.runv('enum Color = {RED: 1}\nview(Color.RED)\ncost Data = {i: 0, f: 0.0}\nd=Data()\nd.i=5\nview(d.i)\nclass A:\n    x\na=A()\na.x=7\nview(a.x)\n')
  self.assertEqual(v.output,['1','5','7'])
 def test_class_optional_field_type_and_default(self):
  v=self.runv('class A:\n    typed: int\n    default = 7\na=A()\nview(a.default)\na.typed=3\nview(a.typed)\n')
  self.assertEqual(v.output,['7','3'])
 def test_goto_label_and_ref_forms(self):
  v=self.runv('x=1\nref y=x\ny=2\nif false: goto done\nview(x)\ndone:\nview(y)\n')
  self.assertEqual(v.output,['2','2'])
 def test_invalid_syntax_is_rejected(self):
  bad=['if true','if true:\nview(1)','func f(\n','x=[1,2','x={"a":1','try:\n    view(1)']
  for src in bad[:-1]:
   with self.subTest(src=src), self.assertRaises((SyntaxError,IndexError)): parse(src)
 def test_invalid_statement_and_expression(self):
  for src in ['else: view(1)\n','view(,)\n','[1,,2]\n','x = 1 2\n']:
   with self.subTest(src=src), self.assertRaises((SyntaxError,NameError_,TypeError_)): self.runv(src)

if __name__=='__main__': unittest.main()
