import os
import stat
import yaml

from . import cache
from . import util

# File name to store the settings in
FILE_NAME='.pistachio'
ALTERNATIVE_FILE_NAME='pistachio.yaml'

# Load settings from a pistachio.yaml file
def load():
  settings = {}
  settings_files = []

  # Search bottom up from the current directory for settings files
  path = os.getcwd()
  while True:
    # Check for ALTERNATIVE_FILE_NAME file
    alternative_settings_file = os.path.join(path, ALTERNATIVE_FILE_NAME)
    if os.path.isfile(alternative_settings_file): settings_files.append(alternative_settings_file)
    # Check for FILE_NAME file
    settings_file = os.path.join(path, FILE_NAME)
    if os.path.isfile(settings_file): settings_files.append(settings_file)
    # Break out if we're at the root directory
    if path == '/': break
    # Check the parent directory next
    path = os.path.abspath(os.path.join(path, os.pardir))

  # Check for a FILE_NAME file in the HOME directory
  if os.getenv('HOME'):
    settings_file = os.path.abspath(os.path.join(os.getenv('HOME'), FILE_NAME))
    if os.path.isfile(settings_file): settings_files.append(settings_file)

  # Load settings from files
  for settings_file in reversed(settings_files):
    settings.update(validate_file(settings_file))

  # Override settings from any environment variables
  for var, val in os.environ.items():
    if var == 'PISTACHIO_PATH':
      # When path is set through environment variables, folders are ':' delimited
      settings['path'] = val.split(':')
    elif var.startswith('PISTACHIO_'):
      key = var.split('PISTACHIO_', 1)[1]
      settings[key.lower()] = val

  return settings


def validate_file(file):
  loaded = yaml.load(open(file,'r'))

  # Check if it's a proper yaml file
  if not loaded: raise Exception('%s is not a proper yaml file.' % file)

  # Expand the fullpath of the cache, if set
  if 'cache' in loaded:
    loaded['cache']['path'] = os.path.abspath(os.path.join(os.path.dirname(file), loaded['cache']['path']))

  # Check file security for open keys
  if 'key' in loaded or 'secret' in loaded:
    mode = oct(stat.S_IMODE(os.stat(file).st_mode))
    if mode not in ['0o600', '0600']:
      raise Exception('Pistachio settings file "{0}" contains a key/secret. Mode must be set to "0600" or "0o600", not "{1}"'.format(file, mode))
    if os.path.basename(file) != FILE_NAME:
      raise Exception('"{0}" is not a "{1}" file. Only "{1}" files can contain key/secrets'.format(file, FILE_NAME))

  return loaded


# Validate settings and set defaults
def validate(settings):
  """
  For the settings to be valid it must fulfill any of the following:
  1. Have a valid cache file
  2. Have a key & secret & bucket defined
  3. Have skipauth set to true as well as a bucket defined
  """
  # Default settings
  if 'path' not in settings or settings['path'] is None: settings['path'] = ['']
  if 'cache' not in settings: settings['cache'] = {}
  settings['cache'].setdefault('enabled', True)
  if 'parallel' not in settings: settings['parallel'] = False
  if 'skipauth' not in settings: settings['skipauth'] = False

  # Check if There is a valid cache
  if ((settings.get('cache', {}).get('path', None) and os.path.isfile(settings['cache']['path'])) and
     # cache exists
     settings['cache'].get('enabled', True) and
     # cache is enabled
     (not settings['cache'].get('expires', None) or not cache.is_expired(settings['cache']))):
     # 'expires' doesn't exist or is not expired
    pass
  # Check if key & secret & bucket are defined
  elif 'key' in settings and 'secret' in settings and 'bucket' in settings:
    pass
  # Check if userole is set to true & bucket are defined
  elif settings.get('skipauth') and 'bucket' in settings:
    pass
  else:
    raise ValueError("""
      For the settings to be valid it must fulfill any of the following:
      1. Have a valid cache file
      2. Have a key & secret & bucket defined
      3. Have skipauth set to true as well as a bucket defined
      """)

  # Type conversions
  if not isinstance(settings['path'], list):
    settings['path'] = [settings['path']]
  settings['parallel'] = util.truthy(settings['parallel'])
  settings['skipauth'] = util.truthy(settings['skipauth'])

  return settings
