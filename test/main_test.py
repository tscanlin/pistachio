# Util Test Module
import copy
import mock
import unittest

import pistachio.main

TEST_CONFIG = {
  'test': 'config',
}
TEST_SETTINGS = {
  'key': 'test',
  'secret': 'test',
  'bucket': 'test',
}

# Tests the settings.validate function
class TestMemoization(unittest.TestCase):

  def setUp(self):
    pass

  def tearDown(self):
    pass

  # Test the memo is returned when set
  def test_returns_memo(self):
    pistachio.main.memo = TEST_CONFIG
    self.assertEqual(pistachio.main.load(TEST_SETTINGS), TEST_CONFIG)

  # Test that memo is set when unset
  @mock.patch('pistachio.cache.load', mock.Mock(return_value = None))
  @mock.patch('pistachio.s3.download', mock.Mock(return_value = TEST_CONFIG))
  def test_memo_set_on_load(self):
    pistachio.main.load(TEST_SETTINGS)
    self.assertEqual(pistachio.main.memo, TEST_CONFIG)

  # Test that memo is set when on reload
  @mock.patch('pistachio.s3.download', mock.Mock(return_value = TEST_CONFIG))
  def test_returns_memo_on_reload(self):
    pistachio.main.attempt_reload(TEST_SETTINGS)
    self.assertEqual(pistachio.main.memo, TEST_CONFIG)

  # Test that memo is not loaded on a reload
  @mock.patch('pistachio.s3.download', mock.Mock(return_value = {'fraudulent': 'config'}))
  def test_reload_ignores_memo(self):
    pistachio.main.attempt_reload(TEST_SETTINGS)
    self.assertNotEqual(pistachio.main.memo, TEST_CONFIG)


if __name__ == '__main__':
    unittest.main()
