# Util Test Module
import copy
import mock
import unittest

import pistachio.cache as cache

# Tests the cache.load
class TestLoad(unittest.TestCase):

  def setUp(self):
    self.isfile_patch = mock.patch('os.path.isfile', mock.Mock(return_value = True))
    self.isfile_patch.start()
    self.timenow_patch = mock.patch('time.time', mock.Mock(return_value = 120)) # 2 minutes since modified
    self.timenow_patch.start()
    self.modifiedtime_patch = mock.patch('os.path.getmtime', mock.Mock(return_value = 0))
    self.modifiedtime_patch.start()
    self.open_patch = mock.patch('__builtin__.open', mock.Mock(return_value = 'foo: bar'))
    self.open_patch.start()

  def tearDown(self):
    self.isfile_patch.stop()
    self.timenow_patch.stop()
    self.modifiedtime_patch.stop()
    self.open_patch.stop()

  # Test that cache is ignored when it doesn't exist
  def test_cache_not_exist(self):
    test_cache = None
    self.assertEqual(cache.load(test_cache), None)

  # Test that cache is ignored when expired
  def test_cache_expired(self):
    test_cache = {'path': 'exists', 'expires': 1} # 1 minute
    self.assertEqual(cache.load(test_cache), None)

  # Test that cache is loaded when not expired
  def test_cache_not_expired(self):
    test_cache = {'path': 'exists', 'expires': 3} # 3 minute
    self.assertEqual(cache.load(test_cache), {'foo': 'bar'})

  # Test that cache is loaded when no expired is specified
  def test_cache_no_expires_setting(self):
    test_cache = {'path': 'exists'}
    self.assertEqual(cache.load(test_cache), {'foo': 'bar'})

  # Test that cache is ignored when no disabled
  def test_cache_disabled(self):
    test_cache = {'path': 'exists', 'enabled': False}
    self.assertEqual(cache.load(test_cache), None)

if __name__ == '__main__':
    unittest.main()
