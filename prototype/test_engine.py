import unittest
from engine import analyze,read_csv
from pathlib import Path

def row(**kw):
 r=dict(id='A',buyer='B',supplier='S',category='C',published='2026-10-01',deadline='2026-10-15',initial_price='100',contract_price='90',bidders='2');r.update(kw);return r
class Tests(unittest.TestCase):
 def test_no_flags(self): self.assertEqual(analyze([row()])['rows'][0]['score'],0)
 def test_one_bidder(self): self.assertEqual(analyze([row(bidders='1')])['rows'][0]['score'],30)
 def test_one_percent_boundary(self): self.assertEqual(analyze([row(contract_price='99')])['rows'][0]['score'],0)
 def test_below_one_percent(self): self.assertEqual(analyze([row(contract_price='99.01')])['rows'][0]['score'],20)
 def test_three_days_boundary(self): self.assertEqual(analyze([row(deadline='2026-10-04')])['rows'][0]['score'],20)
 def test_four_days(self): self.assertEqual(analyze([row(deadline='2026-10-05')])['rows'][0]['score'],0)
 def test_threshold_50(self): self.assertTrue(analyze([row(bidders='1',contract_price='100')])['rows'][0]['review'])
 def test_below_threshold(self): self.assertFalse(analyze([row(contract_price='100',deadline='2026-10-03')])['rows'][0]['review'])
 def test_concentration_boundary(self):
  rs=[row(id=str(i),supplier='S' if i<3 else str(i)) for i in range(5)]
  self.assertEqual([r for r in analyze(rs)['rows'] if r['id']=='0'][0]['score'],30)
 def test_minimum_size(self): self.assertEqual(analyze([row(id=str(i)) for i in range(4)])['rows'][0]['score'],0)
 def test_concentration_below(self):
  rs=[row(id=str(i),supplier='S' if i<2 else str(i)) for i in range(5)]
  self.assertEqual(analyze(rs)['rows'][0]['score'],0)
 def test_repeat(self):
  rs=[row(id='Z'),row(id='A')];self.assertEqual(analyze(rs),analyze(rs))
 def test_reorder(self):
  rs=[row(id='Z'),row(id='A')];self.assertEqual(analyze(rs),analyze(rs[::-1]))
 def test_empty(self):
  with self.assertRaises(ValueError): analyze([])
 def test_missing(self):
  with self.assertRaises(ValueError): analyze([row(buyer='')])
 def test_duplicate(self):
  with self.assertRaises(ValueError): analyze([row(),row()])
 def test_invalid_price(self):
  with self.assertRaises(ValueError): analyze([row(initial_price='0')])
 def test_nan(self):
  with self.assertRaises(ValueError): analyze([row(initial_price='NaN')])
 def test_negative_days(self):
  with self.assertRaises(ValueError): analyze([row(deadline='2026-09-30')])
 def test_invalid_bidders(self):
  with self.assertRaises(ValueError): analyze([row(bidders='0')])
 def test_demo(self):
  r=analyze(read_csv(Path(__file__).with_name('demo.csv').read_text(encoding='utf-8-sig')))
  self.assertEqual((r['total'],r['review']),(40,24));self.assertEqual(r['rows'][0]['score'],100)
if __name__=='__main__': unittest.main(verbosity=2)
