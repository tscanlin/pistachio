import boto
import os
import yaml


# Create an S3 connection
def connect(settings):
  # Use key and secret from pistachio.yaml if set
  if settings['key'] and settings['secret']:
    key = settings['key']
    secret = settings['secret']
  # Otherwise, get it from the environment
  else:
    key = os.getenv('AWS_ACCESS_KEY_ID')
    secret = os.getenv('AWS_SECRET_ACCESS_KEY')
  return boto.connect_s3(key,secret)


# Load settings from a pistachio.yaml file
def load_settings():
  path = os.getcwd()
  # Search bottom up from the current directory for a pistachio.yaml file
  while True:
    settings_file = os.path.join(path, 'pistachio.yaml')
    if os.path.isfile(settings_file):
      loaded = yaml.load(open(settings_file,'r'))
      # Expand the fullpath of the cache, if set
      if 'cache' in loaded: loaded['cache'] = os.path.abspath(os.path.join(path, loaded['cache']))
      return loaded
    if path == '/': raise Exception('No pistachio.yaml file found')
    path = os.path.abspath(os.path.join(path, os.pardir))


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
          config.update(config_partial)
        except boto.exception.S3ResponseError:
          pass # Access denied. Skip this one.

  # If settings['cache'] is set, we should cache the config locally to a file
  if settings['cache']:
    with open(settings['cache'], 'w') as pistachio_cache:
      pistachio_cache.write( yaml.dump(config, default_flow_style=False))

  return config


# Set the CONFIG constant
CONFIG = load_config(load_settings())
