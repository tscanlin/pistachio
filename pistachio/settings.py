import os
import stat
import yaml
import ConfigParser

from . import cache
from . import util

""" Special Variables """
# Pistachio
PISTACHIO_FILE_NAME='.pistachio'
PISTACHIO_ALTERNATIVE_FILE_NAME='pistachio.yaml'
# AWS
AWS_DIR='.aws'
AWS_FILE_NAME='credentials'
AWS_ENV_VARIABLES=['aws_access_key_id', 'aws_secret_access_key', 'aws_session_token']

def load():
  """
  Configure pistachio settings
  """
  settings = {}  # Settings
  pistachio_files = []  # Pistachio specific files

  # Search bottom up from the current directory for settings files
  path = os.getcwd()
  while True:
    # Check for PISTACHIO_ALTERNATIVE_FILE_NAME file
    alternative_settings_file = os.path.join(path, PISTACHIO_ALTERNATIVE_FILE_NAME)
    if os.path.isfile(alternative_settings_file): pistachio_files.append(alternative_settings_file)
    # Check for PISTACHIO_FILE_NAME file
    settings_file = os.path.join(path, PISTACHIO_FILE_NAME)
    if os.path.isfile(settings_file): pistachio_files.append(settings_file)
    # Break out if we're at the root directory
    if path == '/': break
    # Check the parent directory next
    path = os.path.abspath(os.path.join(path, os.pardir))

  # Check for a PISTACHIO_FILE_NAME file in the HOME directory
  if os.getenv('HOME'):
    pistachio_settings_path = os.path.abspath(os.path.join(os.getenv('HOME'), PISTACHIO_FILE_NAME))
    if os.path.isfile(pistachio_settings_path): pistachio_files.append(pistachio_settings_path)

  # Load settings from files
  for pistachio_file in reversed(pistachio_files):
    settings.update(validate_pistachio_file(pistachio_file))

  # Override settings from any PISTACHIO environment variables
  for var, val in os.environ.items():
    if var == 'PISTACHIO_PATH':
      # When pistachio path is set through environment variables, folders are ':' delimited
      settings['path'] = val.split(':')
    elif var.startswith('PISTACHIO_'):
      key = var.split('PISTACHIO_', 1)[1]
      settings[key.lower()] = val

  return settings


def validate_pistachio_file(file):
  loaded = yaml.load(open(file,'r'))

  # Check if it's a proper yaml file
  if not loaded: raise Exception('%s is not a proper yaml file.' % file)

  # Expand the fullpath of the cache, if set
  if 'cache' in loaded:
    loaded['cache']['path'] = os.path.abspath(os.path.join(os.path.dirname(file), loaded['cache']['path']))

  # Warn about open pistachio keys or secrets
  if 'key' in loaded or 'secret' in loaded:
    print('Warning: Found "key" and/or "secret" in {0}. This is deprecated - Using boto (aws) credentials instead'.format(file))

  return loaded


# Validate settings and set defaults
def validate(settings):
  validation_message = """
  For the settings to be valid it must fulfill any of the following:
  1. Have a valid cache file
  2. Have a bucket defined
  """
  # Default settings
  if 'path' not in settings or settings['path'] is None: settings['path'] = ['']
  if 'cache' not in settings: settings['cache'] = {}
  settings['cache'].setdefault('enabled', True)
  if 'parallel' not in settings: settings['parallel'] = False

  # Check if There is a valid cache
  if ((settings.get('cache', {}).get('path', None) and os.path.isfile(settings['cache']['path'])) and
     # cache exists
     settings['cache'].get('enabled', True) and
     # cache is enabled
     (not settings['cache'].get('expires', None) or not cache.is_expired(settings['cache']))):
     # 'expires' doesn't exist or is not expired
    pass
  # Check if bucket is defined
  elif 'bucket' in settings:
    pass
  else:
    raise ValueError(validation_message)

  # Type conversions
  if not isinstance(settings['path'], list):
    settings['path'] = [settings['path']]
  settings['parallel'] = util.truthy(settings['parallel'])

  return settings
