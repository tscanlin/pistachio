# Util Test Module
import copy
from mock import patch
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

  # Test for existence of the minimum required keys for valid settings
  def test_minimum_valid_settings(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    try:
      settings.validate(test_settings)
    except:
      self.fail("settings.validate raised an exception unexpectedly!")

  # Test that validate passes when the cache exists
  @patch('os.path.isfile')
  def test_cache_exists(self, test_patch):
    test_patch.return_value = True
    test_settings = { 'cache': 'exists' }
    try:
      settings.validate(test_settings)
    except:
      self.fail("settings.validate raised an exception unexpectedly!")

  # Test that validate fails when the cache doesn't exist, and we dont' have valid settings
  @patch('os.path.isfile')
  def test_cache_does_not_exist(self, test_patch):
    test_patch.return_value = False
    test_settings = { 'cache': 'does not exist' }
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
