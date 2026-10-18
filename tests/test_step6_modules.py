import tempfile, pathlib, unittest
from noyaba.vm import VM
from noyaba.runtime import PrivacyError,ModuleLoadError,ImportError_

class ModuleTests(unittest.TestCase):
 def make(self, root, name, text):
  p=pathlib.Path(root)/name; p.write_text(text); return str(p)
 def test_module_executes_once_and_exports_public(self):
  with tempfile.TemporaryDirectory() as d:
   self.make(d,'mod.ny','counter = 1\n_public = 9\nview("init")\n')
   main=self.make(d,'main.ny','from mod import counter\nfrom mod import counter\nview(counter)\n')
   v=VM(project_root=d); v.run(pathlib.Path(main).read_text(),main)
   self.assertEqual(v.output,['init','1'])
 def test_private_import_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   self.make(d,'mod.ny','_secret = 1\n__secret = 2\n')
   main=self.make(d,'main.ny','from mod import _secret\n')
   with self.assertRaises(PrivacyError): VM(project_root=d).run(pathlib.Path(main).read_text(),main)
 def test_circular_import_fails(self):
  with tempfile.TemporaryDirectory() as d:
   self.make(d,'a.ny','from b import x\nx = 1\n')
   self.make(d,'b.ny','from a import x\nx = 2\n')
   main=self.make(d,'main.ny','from a import x\n')
   with self.assertRaises(ModuleLoadError): VM(project_root=d).run(pathlib.Path(main).read_text(),main)
 def test_missing_module_error(self):
  with tempfile.TemporaryDirectory() as d:
   main=self.make(d,'main.ny','from nope import x\n')
   with self.assertRaises(ImportError_): VM(project_root=d).run(pathlib.Path(main).read_text(),main)

if __name__=='__main__':unittest.main()
