from setuptools import setup

VERSION = open('VERSION').read().strip()
with open('requirements/core.txt') as f:
  INSTALL_REQUIRES = f.read().splitlines()
with open('requirements/test.txt') as f:
  TEST_REQUIRES = f.read().splitlines()

setup(
  name='pistachio',
  version=VERSION,
  author='Jon San Miguel',
  author_email='jon.sanmiguel@optimizely.com',
  packages=['pistachio'],
  url='https://github.com/optimizely/pistachio',
  download_url='https://github.com/optimizely/pistachio/tarball/%s' % VERSION,
  license=open('LICENSE').read(),
  description='Credential Loader for S3 Stored Credentials',
  long_description=open('README.rst').read(),
  install_requires=INSTALL_REQUIRES,
  tests_require=TEST_REQUIRES,
  test_suite='test',
)
