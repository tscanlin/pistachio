from distutils.core import setup

version = open('VERSION').read().strip()

setup(
  name='pistachio',
  version=version,
  author='Jon San Miguel',
  author_email='jon.sanmiguel@optimizely.com',
  packages=['pistachio'],
  url='https://github.com/optimizely/pistachio',
  download_url='https://github.com/optimizely/pistachio/tarball/%s' % version,
  license=open('LICENSE').read(),
  description='Credential Loader for S3 Stored Credentials',
  long_description=open('README.md').read(),
  install_requires=[
    "PyYAML >= 3.11",
    "boto >= 2.32.1",
  ],
  test_requires=[
    "mock >= 1.0.1",
  ],
)
