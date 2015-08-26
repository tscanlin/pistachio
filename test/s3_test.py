# S3 Test Module
import boto
import copy
import mock
import unittest

import pistachio.s3 as s3

class TestCreateConnection(unittest.TestCase):
  """ Tests the s3.create_connection function """

  def setUp(self):
    self.minimum_valid_settings = {
      'key': 'exists',
      'secret': 'exists',
      'bucket': 'exists',
    }

  def test_using_key_and_secret_succeeds(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    with mock.patch('boto.connect_s3') as connect_s3:
      try:
        s3.create_connection(test_settings)
      except:
        self.fail("settings.validate raised an exception unexpectedly!")
      connect_s3.assert_called_with('exists', 'exists')

  def test_using_key_and_secret_fails_when_no_key(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    del test_settings['key']
    with mock.patch('boto.connect_s3') as connect_s3:
      with self.assertRaises(KeyError):
        s3.create_connection(test_settings)

  def test_using_key_and_secret_fails_when_no_secret(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    del test_settings['key']
    with mock.patch('boto.connect_s3') as connect_s3:
      with self.assertRaises(KeyError):
        s3.create_connection(test_settings)

  def test_skip_auth_does_not_use_key_and_secret(self):
    test_settings = copy.deepcopy(self.minimum_valid_settings)
    test_settings['skipauth'] = True
    with mock.patch('boto.connect_s3') as connect_s3:
      try:
        s3.create_connection(test_settings)
      except:
        self.fail("settings.validate raised an exception unexpectedly!")
      connect_s3.assert_called_with()  # Called with no arguments


class TestDownload(unittest.TestCase):
  """ Tests the s3.download function """
  pass  # TODO


if __name__ == '__main__':
    unittest.main()
