# Util Test Module
import copy
import mock
import unittest

import pistachio.settings as settings

# Tests the settings.validate function
class TestValidate(unittest.TestCase):

  def setUp(self):
    self.minimum_valid_settings = {
      'key': 'exists',
      'secret': 'exists',
      'bucket': 'exists',
    }
    self.timenow_patch = mock.patch('time.time', mock.Mock(return_value = 120)) # 2 minutes since modified
    self.timenow_patch.start()
    self.modifiedtime_patch = mock.patch('os.path.getmtime', mock.Mock(return_value = 0))
    self.modifiedtime_patch.start()

  def tearDown(self):
    self.timenow_patch.stop()
    self.modifiedtime_patch.stop()

  # Test for existence of the minimum required keys for valid settings
  def test_minimum_valid_settings(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    try:
      settings.validate(test_settings)
    except:
      self.fail("settings.validate raised an exception unexpectedly!")

  # Test that validate passes when the cache exists
  @mock.patch('os.path.isfile', mock.Mock(return_value = True))
  def test_cache_exists(self):
    test_settings = {'cache': {'path': 'exists'}}
    try:
      settings.validate(test_settings)
    except:
      self.fail("settings.validate raised an exception unexpectedly!")

  # Test that validate passes when the cache exists and expires is valid
  @mock.patch('os.path.isfile', mock.Mock(return_value = True))
  def test_cache_not_expired(self):
    test_settings = {'cache': {'path': 'exists', 'expires': 3}}
    try:
      settings.validate(test_settings)
    except:
      self.fail("settings.validate raised an exception unexpectedly!")

  # Test validate fails when the cache is expired and we don't have valid settings
  @mock.patch('os.path.isfile', mock.Mock(return_value = True))
  def test_cache_expired(self):
    test_settings = {'cache': {'path': 'exists', 'expires': 1}}
    with self.assertRaises(ValueError):
      settings.validate(test_settings)

  # Test that validate fails when the cache doesn't exist, and we dont' have valid settings
  @mock.patch('os.path.isfile', mock.Mock(return_value = False))
  def test_cache_does_not_exist(self):
    test_settings = {'cache': {'path': 'does not exist'}}
    with self.assertRaises(ValueError):
      settings.validate(test_settings)

  # Test that validate fails when the cache is disabled, and we dont' have valid settings
  @mock.patch('os.path.isfile', mock.Mock(return_value = False))
  def test_cache_disabled(self):
    test_settings = {'cache': {'path': 'does not exist', 'enabled': False}}
    with self.assertRaises(ValueError):
      settings.validate(test_settings)

  # Test that validate() properly sets the default path value
  def test_path_default(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    settings.validate(test_settings)
    self.assertEqual(test_settings['path'], [''])

  # Test that validate() converts the path to an array
  def test_path_type_conversion(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    test_settings['path'] = 'filepath'
    settings.validate(test_settings)
    self.assertEqual(test_settings['path'], ['filepath'])

  # Test that validate() properly sets the default path value
  def test_cache_default(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    settings.validate(test_settings)
    self.assertEqual(test_settings['cache'], None)

  # Test that it requires the 'key' key
  def test_key_required(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    del test_settings['key']
    with self.assertRaises(ValueError):
      settings.validate(test_settings)

  # Test that it requires the 'secret' key
  def test_secret_required(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    del test_settings['secret']
    with self.assertRaises(ValueError):
      settings.validate(test_settings)

  # Test that it requires the 'bucket' key
  def test_bucket_required(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    del test_settings['bucket']
    with self.assertRaises(ValueError):
      settings.validate(test_settings)

if __name__ == '__main__':
    unittest.main()
