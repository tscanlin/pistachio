# S3 Test Module
import boto3
import botocore
import mock
import unittest

import pistachio.s3 as s3


class TestCreateConnection(unittest.TestCase):
  """ Tests the s3.create_connection function """

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

  def test_using_no_profile_uses_boto3_credentials(self):
    test_settings = self.new_valid_settings
    del test_settings['profile']
    with mock.patch('boto3.session.Session') as session:
      try:
        s3.create_connection(test_settings)
      except Exception as e:
        self.fail(e)
      session.assert_called_with()

  def test_using_unknown_profile_fails(self):
    test_settings = self.new_valid_settings
    test_settings['profile'] = 'anonymous123+_not_a_profile$$$$'
    with self.assertRaises(botocore.exceptions.ProfileNotFound):
      s3.create_connection(test_settings)

  def test_using_specified_profile_uses_specified_profile(self):
    test_settings = self.new_valid_settings
    test_settings['profile'] = 'not default'
    with mock.patch('boto3.session.Session') as session:
      try:
        s3.create_connection(test_settings)
      except Exception as e:
        self.fail(e)
      session.assert_called_with(profile_name='not default')

  def test_using_key_and_secret(self):
    test_settings = self.old_valid_settings
    with mock.patch('boto3.session.Session') as session:
      try:
        s3.create_connection(test_settings)
      except Exception as e:
        self.fail(e)
      session.assert_called_with(aws_access_key_id='exists', aws_secret_access_key='exists')

  def test_using_deprecated_key_only_uses_boto3_credentials(self):
    test_settings = self.old_valid_settings
    del test_settings['secret']
    with mock.patch('boto3.session.Session') as session:
      try:
        s3.create_connection(test_settings)
      except Exception as e:
        self.fail(e)
      session.assert_called_with()

  def test_using_deprecated_secret_only_uses_boto3_credentials(self):
    test_settings = self.old_valid_settings
    del test_settings['key']
    with mock.patch('boto3.session.Session') as session:
      try:
        s3.create_connection(test_settings)
      except Exception as e:
        self.fail(e)
      session.assert_called_with()

  def test_using_nothing_uses_boto3_credentials(self):
    with mock.patch('boto3.session.Session') as session:
      try:
        s3.create_connection({})
      except Exception as e:
        self.fail(e)
      session.assert_called_with()


class TestDownload(unittest.TestCase):
  """ Tests the s3.download function """
  pass  # TODO


if __name__ == '__main__':
    unittest.main()
