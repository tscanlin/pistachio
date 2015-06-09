# Util Test Module
import unittest
import pistachio.util as util

# Tests the util.merge_dicts function
class TestMergeDicts(unittest.TestCase):

  def setUp(self):
    pass

  # Test the recursive case: both d1 and d2 have nested dicts
  def test_recursive_case(self):
    d1 = { 'test': { 'overlap': 'this will be overridden', 'd1': 'this should be unaffected' }}
    d2 = { 'test': { 'overlap': 'this will override', 'd2': 'this should be merged in' }}
    merged = {
      'test': {
        'overlap': 'this will override',
        'd1': 'this should be unaffected',
        'd2': 'this should be merged in' }}
    self.assertEqual(util.merge_dicts(d1, d2), merged)

  # Test the base case: d1 is a nested dict
  def test_base_case_d1(self):
    d1 = { 'test': { 'inner': 'dict' } }
    d2 = { 'test': 'string' }
    self.assertEqual(util.merge_dicts(d1, d2), d2)

  # Test the base case: d2 is a nested dict
  def test_base_case_d2(self):
    d1 = { 'test': 'string' }
    d2 = { 'test': { 'inner': 'dict' } }
    self.assertEqual(util.merge_dicts(d1, d2), d2)

  # Test the base case: neither d1 or d2 have nested dicts
  def test_base_case(self):
    d1 = { 'test': 'string' }
    d2 = { 'test': 'alsostring' }
    self.assertEqual(util.merge_dicts(d1, d2), d2)


# Tests the util.truthy function
class TestTruthy(unittest.TestCase):

  def setUp(self):
    self.truth_map = [
      ('True', True),
      ('true', True),
      (True, True),
      ('False', False),
      ('false', False),
      (False, False),
      ('', False),
      (None, False),
    ]

  def test_truth_map(self):
    for arg, output in self.truth_map:
      self.assertEqual(util.truthy(arg), output)


if __name__ == '__main__':
    unittest.main()
