from pathlib import Path
import unittest
from noyaba.vm import VM

ROOT=Path(__file__).parents[1]/'examples'/'builtins'

class BuiltinFileE2E(unittest.TestCase):
 def test_core_builtin_fixture_through_file_pipeline(self):
  source=(ROOT/'core.noy').read_text(encoding='utf8')
  v=VM(project_root=str(ROOT)); v.run(source, filename=str(ROOT/'core.noy'))
  self.assertEqual(v.output,['10','10.0','123','false','INT','true','3','[1, 2, 3]','7','8','4','3','5','1','65','A','0xf','0o10',"'A'"])

if __name__=='__main__': unittest.main()
