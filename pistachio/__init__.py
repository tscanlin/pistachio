import boto
import os
import yaml


# Recursively update a dict
# Merges d2 into d1
# Any conflicts override d1
def merge_dicts(d1, d2):
  for key in d2:
    if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
      merge_dicts(d1[key], d2[key])
    else:
      d1[key] = d2[key]
  return d1


# Create an S3 connection
def connect(settings):
  key = settings['key']
  secret = settings['secret']
  return boto.connect_s3(key,secret)


# Load settings from a pistachio.yaml file
def load_settings():
  settings = {}
  settings_files = []

  # Search bottom up from the current directory for a pistachio.yaml file
  path = os.getcwd()
  while True:
    settings_file = os.path.join(path, 'pistachio.yaml')
    if os.path.isfile(settings_file): settings_files.append(settings_file)
    if path == '/': break
    path = os.path.abspath(os.path.join(path, os.pardir))

  # Check for a 'pistachio.yaml' file in the HOME directory
  if os.getenv('HOME'):
    settings_file = os.path.abspath(os.path.join(os.getenv('HOME'), 'pistachio.yaml'))
    if os.path.isfile(settings_file): settings_files.append(settings_file)

  # Load settings from files
  for settings_file in reversed(settings_files):
    loaded = yaml.load(open(settings_file,'r'))
    # Expand the fullpath of the cache, if set
    if 'cache' in loaded: loaded['cache'] = os.path.abspath(os.path.join(os.path.dirname(settings_file), loaded['cache']))
    settings.update(loaded)

  # Override settings from any environment variables
  for var, val in os.environ.iteritems():
    if var.startswith('PISTACHIO_'):
      key = var.split('PISTACHIO_', 1)[1]
      settings[key.lower()] = val

  return settings


# Validate settings and set defaults
def validate_settings(settings):
  # Required keys
  for required_key in ['key', 'secret', 'bucket']:
    if required_key not in settings: raise Exception('The "%s" key is required.' % required_key)

  # Default settings
  if 'path' not in settings or settings['path'] is None: settings['path'] = ['']
  if 'cache' not in settings: settings['cache'] = None

  # Type conversions
  if not isinstance(settings['path'], list):
    settings['path'] = [settings['path']]

  return settings


# Load the config from S3
def load_config(settings):
  settings = validate_settings(settings)

  # Load the file from a cache if one exists
  if settings['cache'] and os.path.isfile(settings['cache']):
    return yaml.load(open(settings['cache'],'r'))

  conn = connect(settings)
  bucket = conn.get_bucket(settings['bucket'], validate=False)

  # Initialize the config with the pistachio keys
  config = {
    'pistachio': {
      'key': conn.access_key,
      'secret': conn.secret_key,
    }
  }
  # For each folder
  for folder in reversed(settings['path']):
    # Iterate through yaml files in the set folder
    for key in bucket.list(folder+'/', delimiter='/'):
      if key.name.endswith('.yaml'):
        try:
          contents = key.get_contents_as_string()
          # Update the config with the config partial
          config_partial = yaml.load(contents)
          merge_dicts(config, config_partial)
        except boto.exception.S3ResponseError:
          pass # Access denied. Skip this one.

  # If settings['cache'] is set, we should cache the config locally to a file
  if settings['cache']:
    with open(settings['cache'], 'w') as pistachio_cache:
      pistachio_cache.write( yaml.dump(config, default_flow_style=False))

  return config


# Set the CONFIG constant
CONFIG = load_config(load_settings())
