from distutils.core import setup

setup(
  name='pistachio',
  version='0.1.0',
  author='Jon San Miguel',
  author_email='jon.sanmiguel@optimizely.com',
  packages=['pistachio'],
  url='https://github.com/optimizely/pistachio',
  license='Copyright Optimizely',
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
