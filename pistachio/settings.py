import os
import stat
import yaml

from . import cache
from . import util

""" Special Variables """
PISTACHIO_FILE_NAME = '.pistachio'
PISTACHIO_ALTERNATIVE_FILE_NAME = 'pistachio.yaml'

def load():
  """
  Configure pistachio settings.

  Settings are retrieved by walking backwards from the cwd, to the $HOME dir.
  Any file in that walk path named PISTACHIO_FILE_NAME or
  PISTACHIO_ALTERNATIVE_FILE_NAME is parsed for settings.
  """
  settings = {}  # Settings
  pistachio_files = []  # Pistachio specific files

  # Search bottom up from the current directory for settings files
  path = os.getcwd()

  while True:
    # Check for PISTACHIO_ALTERNATIVE_FILE_NAME and PISTACHIO_FILE_NAME
    for filename in (PISTACHIO_ALTERNATIVE_FILE_NAME, PISTACHIO_FILE_NAME):
      file_path = os.path.join(path, filename)
      if os.path.isfile(file_path):
        pistachio_files.append(file_path)

    # Break out if we're at the root directory
    if path == '/':
      break
    # Otherwise, iterate up to the parent directory
    path = os.path.abspath(os.path.join(path, os.pardir))

  # Check for a PISTACHIO_FILE_NAME file in the HOME directory
  if os.getenv('HOME'):
    pistachio_settings_path = os.path.abspath(
      os.path.join(os.getenv('HOME'), PISTACHIO_FILE_NAME)
    )
    if os.path.isfile(pistachio_settings_path):
      pistachio_files.append(pistachio_settings_path)

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
  with open(file, 'r') as _file:
    contents = _file.read().strip()
  loaded = yaml.load(contents)

  if not contents or not loaded or loaded == contents:
    # If it's still just a regular string, then it's not yaml
    raise Exception('%s is not a proper yaml file.' % file)

  # Expand the fullpath of the cache, if set
  if 'cache' in loaded:
    loaded['cache']['path'] = os.path.abspath(os.path.join(os.path.dirname(file), loaded['cache']['path']))

  # Warn about open pistachio keys or secrets
  if 'key' in loaded or 'secret' in loaded:
    mode = oct(stat.S_IMODE(os.stat(file).st_mode))
    if mode not in ['0o600', '0600']:
      raise Exception('Pistachio settings file "{0}" contains a key/secret. Mode must be set to "0600" or "0o600", not "{1}"'.format(file, mode))
    print('"{0}" contains key/secret. Please remove key/secret. Using AWS credentials instead...'.format(file))
    loaded.pop('key', None)
    loaded.pop('secret', None)

  return loaded


# Set the default values for missing fields
def set_defaults(settings):
  # Default settings
  if 'path' not in settings or settings['path'] is None:
    settings['path'] = ['']

  if 'cache' not in settings:
    settings['cache'] = {}
  else:
    settings['cache'].setdefault('enabled', True)

  if 'parallel' not in settings:
    settings['parallel'] = False

  return settings


# Validate settings and set defaults
def validate(settings):
  validation_message = """
  For the settings to be valid it must fulfill any of the following:
  1. Have a valid cache file
  2. Have a bucket defined
  """

  settings = set_defaults(settings)
  if 'bucket' not in settings and not (settings['cache'] and cache.is_valid(settings)):
    raise ValueError(validation_message)

  # Type conversions
  if not isinstance(settings.get('path', []), list):
    settings['path'] = [settings['path']]
  if not isinstance(settings.get('cache', {}).get('disable', []), list):
    settings['cache']['disable'] = [settings['cache']['disable']]
  if not isinstance(settings.get('parallel', False), bool):
    settings['parallel'] = util.truthy(settings['parallel'])

  return settings
