import unittest
from noyaba.vm import VM
from noyaba.runtime import CostError
class CostTests(unittest.TestCase):
 def test_switch_active_member(self):
  v=VM(); v.run('cost Data = {i: 0, f: 0.0}\nd = Data()\nd.i = 3\nview(d.i)\nd.f = 2.5\nview(d.f)\n')
  self.assertEqual(v.output,['3','2.5'])
 def test_inactive_member_fails(self):
  with self.assertRaises(CostError): VM().run('cost Data = {i: 0, f: 0.0}\nd = Data()\nd.i = 3\nview(d.f)\n')
if __name__=='__main__': unittest.main()
