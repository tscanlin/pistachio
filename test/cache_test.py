# Util Test Module
import copy
import mock
import io
import sys
import unittest

import pistachio.cache as cache

# Get builtins based on python version
if sys.version_info.major == 2:
  builtins = '__builtin__'
  import __builtin__ as builtins_module
else:
  builtins = 'builtins'
  import builtins as builtins_module


# Tests the cache.load
class TestLoad(unittest.TestCase):

  def setUp(self):
    # Mock isfile to return True
    self.isfile_patch = mock.patch('os.path.isfile', mock.Mock(return_value = True))
    self.isfile_patch.start()

    # Freeze the time to two minutes
    self.timenow_patch = mock.patch('time.time', mock.Mock(return_value = 120)) # 2 minutes since modified
    self.timenow_patch.start()

    # Set modified time to zero
    self.modifiedtime_patch = mock.patch('os.path.getmtime', mock.Mock(return_value = 0))
    self.modifiedtime_patch.start()

    # Mock open method to return without reading an actual file
    self.open_patch = mock.patch('%s.open' % builtins, mock.Mock(return_value = 'foo: bar'))
    self.open_patch.start()

  def tearDown(self):
    self.isfile_patch.stop()
    self.timenow_patch.stop()
    self.modifiedtime_patch.stop()
    self.open_patch.stop()

  # Test that cache is ignored when empty
  def test_cache_not_exist(self):
    test_cache = {}
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


# Tests the cache.load
class TestWrite(unittest.TestCase):

  def setUp(self):
    # Test loaded config
    self.test_config = {'test': 'config'}

    # Mock chmod to return True
    self.chmod_patch = mock.patch('os.chmod', mock.Mock(return_value = True))
    self.chmod_patch.start()

  def tearDown(self):
    self.chmod_patch.stop()

  # Test that cache is not written when no path is set
  @mock.patch.object(builtins_module, 'open')
  def test_cache_not_set(self, open_mock):
    test_cache = {}
    cache.write(test_cache, self.test_config)
    self.assertFalse(open_mock.called)

  # Test that cache is written when path is set and enabled is set to true
  @mock.patch.object(builtins_module, 'open')
  def test_cache_enabled_true(self, open_mock):
    test_cache = {'path': 'exists', 'enabled': True}
    cache.write(test_cache, self.test_config)
    self.assertTrue(open_mock.called)

  # Test that cache is not written when path is set and enabled is set to false
  @mock.patch.object(builtins_module, 'open')
  def test_cache_enabled_true(self, open_mock):
    test_cache = {'path': 'exists', 'enabled': False}
    cache.write(test_cache, self.test_config)
    self.assertFalse(open_mock.called)


if __name__ == '__main__':
    unittest.main()
