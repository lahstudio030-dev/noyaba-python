from pathlib import Path
import unittest
from noyaba.vm import VM
ROOT=Path(__file__).parents[1]/'examples'/'step6'
class Step6FileE2E(unittest.TestCase):
 def run_file(self,name):
  p=ROOT/name; v=VM(project_root=str(ROOT)); v.run(p.read_text(),str(p)); return v.output
 def test_trigger_file(self): self.assertEqual(self.run_file('trigger.noy'),['two'])
 def test_class_file(self): self.assertEqual(self.run_file('classes.noy'),['parent'])
 def test_fixed_struct_file(self): self.assertEqual(self.run_file('fixed_struct.noy'),['LAH','20'])
 def test_macro_cast_file(self): self.assertEqual(self.run_file('macro_cast.noy'),['6','3','2.0'])
 def test_exception_file(self): self.assertEqual(self.run_file('exceptions.noy'),['boom'])
if __name__=='__main__':unittest.main()
