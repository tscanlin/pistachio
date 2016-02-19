import os
import stat
import yaml

from . import cache
from . import util

""" Special Variables """
# Pistachio
PISTACHIO_FILE_NAME='.pistachio'
PISTACHIO_ALTERNATIVE_FILE_NAME='pistachio.yaml'

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
    # Otherwise, iterate up to the parent directory
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
    mode = oct(stat.S_IMODE(os.stat(file).st_mode))
    if mode not in ['0o600', '0600']:
      raise Exception('Pistachio settings file "{0}" contains a key/secret. Mode must be set to "0600" or "0o600", not "{1}"'.format(file, mode))
    if os.path.basename(file) != PISTACHIO_FILE_NAME:
      raise Exception('"{0}" is not a "{1}" file. Only "{1}" files can contain key/secrets'.format(file, PISTACHIO_FILE_NAME))

  return loaded


# Set the default values for missing fields
def set_defaults(settings):
  # Default settings
  if 'path' not in settings or settings['path'] is None: settings['path'] = ['']
  if 'cache' not in settings: settings['cache'] = {}
  settings['cache'].setdefault('enabled', True)
  if 'parallel' not in settings: settings['parallel'] = False
  if 'skipauth' not in settings: settings['skipauth'] = False

  return settings


# Validate settings and set defaults
def validate(settings):
  validation_message = """
  For the settings to be valid it must fulfill any of the following:
  1. Have a valid cache file
  2. Have a bucket defined
  """

  # Cache is valid
  has_valid_cache = os.path.isfile(settings.get('cache', {}).get('path', ''))
  # Cache is enabled
  cache_enabled = settings.get('cache', {}).get('enabled', True)
  # Cache is expired
  cache_has_expired = settings.get('cache', {}).get('expires')
  cache_expired = cache_has_expired and cache.is_expired(settings['cache'])

  if has_valid_cache and cache_enabled and not cache_expired:
    pass
  # Check if bucket is defined
  elif 'bucket' in settings:
    pass
  else:
    raise ValueError(validation_message)

  # Type conversions
  if not isinstance(settings.get('path', []), list):
    settings['path'] = [settings['path']]
  if not isinstance(settings.get('parallel', False), bool):
    settings['parallel'] = util.truthy(settings['parallel'])
  if not isinstance(settings.get('skipauth', False), bool):
    settings['skipauth'] = util.truthy(settings['skipauth'])

  return settings
