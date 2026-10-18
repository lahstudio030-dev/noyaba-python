import tempfile
from pathlib import Path
import unittest
from noyaba.vm import VM
from noyaba.runtime import ImportError_,ModuleLoadError,PrivacyError,CenterError,NameError_

class ModuleMatrix(unittest.TestCase):
 def file(self,root,rel,text):
  p=Path(root)/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text); return p
 def runmain(self,root,text):
  p=self.file(root,'main.noy',text); v=VM(project_root=root); v.run(p.read_text(),str(p)); return v
 def test_dotted_module_import(self):
  with tempfile.TemporaryDirectory() as d:
   self.file(d,'pkg/mod.ny','value=42\n')
   v=self.runmain(d,'from pkg.mod import value\nview(value)\n')
   self.assertEqual(v.output,['42'])
 def test_multiple_names_and_configured_path(self):
  with tempfile.TemporaryDirectory() as project, tempfile.TemporaryDirectory() as lib:
   self.file(lib,'shared.ny','a=2\nb=3\n')
   p=self.file(project,'main.noy','from shared import a, b\nview(a+b)\n')
   v=VM(project_root=project,module_paths=[lib]); v.run(p.read_text(),str(p)); self.assertEqual(v.output,['5'])
 def test_nested_module_import_and_relative_resolution(self):
  with tempfile.TemporaryDirectory() as d:
   self.file(d,'pkg/inner.ny','value=9\n')
   self.file(d,'pkg/outer.ny','from inner import value\nresult=value+1\n')
   v=self.runmain(d,'from pkg.outer import result\nview(result)\n')
   self.assertEqual(v.output,['10'])
 def test_cache_by_canonical_path(self):
  with tempfile.TemporaryDirectory() as d:
   self.file(d,'m.ny','view("init")\nvalue=1\n')
   v=self.runmain(d,'from m import value\nfrom m import value\nview(value)\n')
   self.assertEqual(v.output,['init','1'])
 def test_missing_name_and_module_errors(self):
  with tempfile.TemporaryDirectory() as d:
   self.file(d,'m.ny','value=1\n')
   with self.assertRaises(ImportError_): self.runmain(d,'from m import absent\n')
   with self.assertRaises(ImportError_): self.runmain(d,'from nope import value\n')
 def test_private_exports_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   self.file(d,'m.ny','_secret=1\n__secret=2\n')
   with self.assertRaises(PrivacyError): self.runmain(d,'from m import _secret\n')
   with self.assertRaises(PrivacyError): self.runmain(d,'from m import __secret\n')
 def test_module_initialization_failure_is_wrapped(self):
  with tempfile.TemporaryDirectory() as d:
   self.file(d,'bad.ny','x=1/0\n')
   with self.assertRaises(ModuleLoadError) as cm: self.runmain(d,'from bad import x\n')
   self.assertIn('bad.ny',str(cm.exception)); self.assertIsInstance(cm.exception.__cause__,CenterError)
 def test_circular_import(self):
  with tempfile.TemporaryDirectory() as d:
   self.file(d,'a.ny','from b import value\nvalue=1\n')
   self.file(d,'b.ny','from a import value\nvalue=2\n')
   with self.assertRaises(ModuleLoadError): self.runmain(d,'from a import value\n')
 def test_unsupported_import_forms_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   self.file(d,'m.ny','x=1\n')
   for src in ['import m\n']:
    with self.subTest(src=src), self.assertRaises((SyntaxError,ImportError_,NameError_)):
     self.runmain(d,src)

if __name__=='__main__':unittest.main()
