import os
import stat
import yaml

# File name to store the settings in
FILE_NAME='.pistachio'

# Load settings from a pistachio.yaml file
def load():
  settings = {}
  settings_files = []

  # Search bottom up from the current directory for a pistachio.yaml file
  path = os.getcwd()
  while True:
    settings_file = os.path.join(path, FILE_NAME)
    if os.path.isfile(settings_file): settings_files.append(settings_file)
    if path == '/': break
    path = os.path.abspath(os.path.join(path, os.pardir))

  # Check for a FILE_NAME file in the HOME directory
  if os.getenv('HOME'):
    settings_file = os.path.abspath(os.path.join(os.getenv('HOME'), FILE_NAME))
    if os.path.isfile(settings_file): settings_files.append(settings_file)

  # Load settings from files
  for settings_file in reversed(settings_files):
    settings.update(validate_file(settings_file))

  # Override settings from any environment variables
  for var, val in os.environ.iteritems():
    if var == 'PISTACHIO_PATH':
      # When path is set through environment variables, folders are ':' delimited
      settings['path'] = val.split(':')
    elif var.startswith('PISTACHIO_'):
      key = var.split('PISTACHIO_', 1)[1]
      settings[key.lower()] = val

  return settings


def validate_file(file):
  loaded = yaml.load(open(file,'r'))

  # Expand the fullpath of the cache, if set
  if 'cache' in loaded:
    loaded['cache'] = os.path.abspath(os.path.join(os.path.dirname(file), loaded['cache']))

  # Check file security for open keys
  if 'key' in loaded or 'secret' in loaded:
    mode = oct(stat.S_IMODE(os.stat(file).st_mode))
    if not mode == '0600':
      raise Exception('Pistachio settings file "%s" contains a key/secret. Mode must be set to "0600"' % file)

  return loaded


# Validate settings and set defaults
def validate(settings):
  # Required keys
  if 'cache' in settings and settings['cache'] and os.path.isfile(settings['cache']):
    pass # Only 'cache' key is required, if the cache already exists.
  else:
    for required_key in ['key', 'secret', 'bucket']:
      if required_key not in settings: raise Exception('The "%s" key is required.' % required_key)

  # Default settings
  if 'path' not in settings or settings['path'] is None: settings['path'] = ['']
  if 'cache' not in settings: settings['cache'] = None

  # Type conversions
  if not isinstance(settings['path'], list):
    settings['path'] = [settings['path']]

  return settings
