import boto
import os
import stat
import yaml

import settings
import util

# Create an S3 connection
def connect(s):
  key = s['key']
  secret = s['secret']
  return boto.connect_s3(key,secret)


# Load and merge the yaml files from S3
def load(s=settings.load()):
  s = settings.validate(s)

  # Load the file from a cache if one exists
  if s['cache'] and os.path.isfile(s['cache']):
    mode = oct(stat.S_IMODE(os.stat(s['cache']).st_mode))
    if not mode == '0600':
      raise Exception('Cache file "%s" mode must be set to "0600"' % s['cache'])
    return yaml.load(open(s['cache'],'r'))

  conn = connect(s)
  bucket = conn.get_bucket(s['bucket'], validate=False)

  # Initialize the config with the pistachio keys
  config = {
    'pistachio': {
      'key': conn.access_key,
      'secret': conn.secret_key,
    }
  }
  # For each folder
  for folder in reversed(s['path']):
    # Iterate through yaml files in the set folder
    for key in bucket.list(folder+'/', delimiter='/'):
      if key.name.endswith('.yaml'):
        try:
          contents = key.get_contents_as_string()
          # Update the config with the config partial
          config_partial = yaml.load(contents)
          util.merge_dicts(config, config_partial)
        except boto.exception.S3ResponseError:
          pass # Access denied. Skip this one.

  # If s['cache'] is set, we should cache the config locally to a file
  if s['cache']:
    with open(s['cache'], 'w') as pistachio_cache:
      pistachio_cache.write( yaml.dump(config, default_flow_style=False))
    os.chmod(s['cache'], 0600)

  return config
