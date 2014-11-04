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
    config = os.path.join(path, 'pistachio.yaml')
    if os.path.isfile(config): return yaml.load(open(config,'r'))
    if path == '/': raise Exception('No pistachio.yaml file found')
    path = os.path.abspath(os.path.join(path, os.pardir))

# Load the config from S3
def load_config(settings):
  conn = connect(settings)
  bucket = conn.get_bucket(settings['bucket'])

  # Create an empty config
  config = {}
  # Iterate through yaml files in the set folder
  for key in bucket.list(settings['folder']):
    if key.name.endswith('.yaml'):
      contents = key.get_contents_as_string()
      config_partial = yaml.load(contents)
      # Update the config with the config partial
      config.update(config_partial)
  return config

CONFIG = load_config(load_settings())
