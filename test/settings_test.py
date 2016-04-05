# Settings Test Module
import mock
import unittest

import pistachio.settings as settings

# Tests the settings.validate function
class TestValidate(unittest.TestCase):

  def setUp(self):
    self.new_valid_settings = {  # Pistaciho VERSION 2.0 > pistachio settings
      'profile': 'exists',
      'bucket': 'exists',
    }
    self.old_valid_settings = {  # Pistachio VERSION 1.0 > pistachio settings
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

  # Test for the new valid settings
  def test_new_valid_settings(self):
    test_settings = self.new_valid_settings
    try:
      settings.validate(test_settings)
    except:
      self.fail("settings.validate raised an exception unexpectedly!")

  # Test for the old valid settings
  def test_old_valid_settings(self):
    test_settings = self.old_valid_settings
    try:
      settings.validate(test_settings)
    except:
      self.fail("settings.validate raised an exception unexpectedly!")

  # Test that validate passes when the cache exists
  @mock.patch('pistachio.cache.read', mock.Mock(return_value = {'pistachio': {'path': ''}}))
  @mock.patch('os.path.isfile', mock.Mock(return_value = True))
  def test_cache_exists(self):
    test_settings = {'cache': {'path': 'exists'}}
    try:
      settings.validate(test_settings)
    except:
      self.fail("settings.validate raised an exception unexpectedly!")

  # Test that validate passes when the cache exists and expires is valid
  @mock.patch('pistachio.cache.read', mock.Mock(return_value = {'pistachio': {'path': ''}}))
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
    # Validate
    test_settings = self.old_valid_settings
    settings.validate(test_settings)
    self.assertEqual(test_settings.get('path'), [''])

  # Test that validate() converts the path to an array
  def test_path_type_conversion(self):
    test_settings = self.old_valid_settings
    test_settings['path'] = 'filepath'
    # Validate
    settings.validate(test_settings)
    self.assertEqual(test_settings.get('path'), ['filepath'])

  # Test that a defined path settings is not overwritten by set_defaults
  def test_path_defined(self):
    test_settings = self.old_valid_settings
    test_settings['path'] = ['filepath']
    # Validate
    settings.validate(test_settings)
    self.assertEqual(test_settings.get('path'), ['filepath'])
    # Default should not affect
    settings.set_defaults(test_settings)
    self.assertEqual(test_settings.get('path'), ['filepath'])

  # Test that validate() properly sets the default cache value
  def test_cache_default(self):
    # Validate
    test_settings = self.old_valid_settings
    settings.validate(test_settings)
    self.assertEqual(test_settings.get('cache'), {})

  # Test that a defined cache settings is not overwritten by set_defaults
  def test_cache_defined(self):
    test_settings = self.old_valid_settings
    test_settings['cache'] = {'a': 'b'}
    # Validate
    settings.validate(test_settings)
    self.assertEqual(test_settings.get('cache'), {'a': 'b', 'enabled': True})

  # Test that validate() converts cache disabled to an array
  def test_cache_disabled_type_conversion(self):
    test_settings = self.old_valid_settings
    test_settings['cache'] = {'disable':'proddin'}
    # Validate
    settings.validate(test_settings)
    self.assertEqual(test_settings['cache']['disable'], ['proddin'])
  
  # Test that it does not require the 'key' key
  def test_no_key(self):
    test_settings = self.old_valid_settings
    del test_settings['key']
    try:
      settings.validate(test_settings)
    except Exception as e:
      self.fail(e)

  # Test that it does not require the 'secret' key
  def test_no_secret(self):
    test_settings = self.old_valid_settings
    del test_settings['secret']
    try:
      settings.validate(test_settings)
    except Exception as e:
      self.fail(e)

  # Test that it requires the 'bucket' key
  def test_bucket_required(self):
    test_settings = self.old_valid_settings
    del test_settings['bucket']
    with self.assertRaises(ValueError):
      settings.validate(test_settings)

  # Test that validate passes when no key/secret is given
  def test_no_key_or_secret(self):
    test_settings = self.old_valid_settings
    del test_settings['key']
    del test_settings['secret']
    try:
      settings.validate(test_settings)
    except Exception as e:
      self.fail(e)

  # Test that validate() properly sets the default parallel value
  def test_parallel_default(self):
    test_settings = self.old_valid_settings
    # Validate
    settings.validate(test_settings)
    self.assertEqual(test_settings.get('parallel'), False)

  # Test that a defined parallel settings is not overwritten by set_defaults
  def test_parallel_defined(self):
    # Validate
    test_settings = self.old_valid_settings
    test_settings['parallel'] = True
    settings.validate(test_settings)
    self.assertEqual(test_settings.get('parallel'), True)

  # Test that validate() properly sets parllel to True when 'true' is passed in as a string
  def test_parallel_true_string(self):
    test_settings = self.old_valid_settings
    test_settings['parallel'] = 'true'
    settings.validate(test_settings)
    self.assertTrue(test_settings.get('parallel'))

if __name__ == '__main__':
    unittest.main()
