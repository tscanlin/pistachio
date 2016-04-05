# Util Test Module
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
    self.default_settings = {'path': '', 'cache': {'enabled': True, 'path': 'exists'}}
    self.default_cache = {
      'foo': 'bar',
      'pistachio': {
        'path': ''
      }
    }

    # Mock isfile to return True
    self.isfile_patch = mock.patch('os.path.isfile', mock.Mock(return_value = True))
    self.isfile_patch.start()

    # Freeze the time to two minutes
    self.timenow_patch = mock.patch('time.time', mock.Mock(return_value = 120)) # 2 minutes since modified
    self.timenow_patch.start()

    # Set modified time to zero
    self.modifiedtime_patch = mock.patch('os.path.getmtime', mock.Mock(return_value = 0))
    self.modifiedtime_patch.start()

    # Mock read method to return without reading an actual file
    self.read_patch = mock.patch('pistachio.cache.read', mock.Mock(return_value = self.default_cache))
    self.read_patch.start()

  def tearDown(self):
    self.isfile_patch.stop()
    self.timenow_patch.stop()
    self.modifiedtime_patch.stop()
    self.read_patch.stop()

  # Test that cache is ignored when empty
  def test_cache_no_settings(self):
    test_settings = {'cache': {}}
    self.assertEqual(cache.load(test_settings), None)

  # Test that cache is ignored when expired
  def test_cache_expired(self):
    test_settings = self.default_settings
    test_settings['cache']['expires'] = 1 # 1 minute
    self.assertEqual(cache.load(test_settings), None)

  # Test that cache is loaded when not expired
  def test_cache_not_expired(self):
    test_settings = self.default_settings
    test_settings['cache']['expires'] = 3 # 3 minute
    self.assertEqual(cache.load(test_settings), self.default_cache)

  # Test that cache is loaded when no expired is specified
  def test_cache_no_expires_setting(self):
    test_settings = self.default_settings
    self.assertEqual(cache.load(test_settings), self.default_cache)

  # Test that cache is ignored when no disabled
  def test_cache_not_enabled(self):
    test_settings = self.default_settings
    test_settings['cache']['enabled'] = False # 1 minute
    self.assertEqual(cache.load(test_settings), None)


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
    test_settings = {'cache': {}}
    cache.write(test_settings, self.test_config)
    self.assertFalse(open_mock.called)

  # Test that cache is written when path is set and enabled is set to true
  @mock.patch.object(builtins_module, 'open')
  def test_cache_enabled_true(self, open_mock):
    test_settings = {'cache': {'path': 'exists', 'enabled': True}}
    cache.write(test_settings, self.test_config)
    self.assertTrue(open_mock.called)

  # Test that cache is not written when path is set and enabled is set to false
  @mock.patch.object(builtins_module, 'open')
  def test_cache_enabled_false(self, open_mock):
    test_settings = {'cache': {'path': 'exists', 'enabled': False}}
    cache.write(test_settings, self.test_config)
    self.assertFalse(open_mock.called)

  # Test that cache is not written when pistacho loads a path that is disabled in cache
  @mock.patch.object(builtins_module, 'open')
  def test_cache_disable(self, open_mock):
    test_settings = {'cache': {'path': 'exists', 'enabled': True, 'disable': ['prod']}, 'path': ['prod', 'dev']}
    cache.write(test_settings, self.test_config)
    self.assertFalse(open_mock.called)

  # Test that cache is written when no disabled paths are included within settings
  @mock.patch.object(builtins_module, 'open')
  def test_cache_not_disable(self, open_mock):
    test_settings = {'cache': {'path': 'exists', 'enabled': True, 'disable': ['athena']}, 'path': ['prod', 'dev']}
    cache.write(test_settings, self.test_config)
    self.assertTrue(open_mock.called)

if __name__ == '__main__':
    unittest.main()
