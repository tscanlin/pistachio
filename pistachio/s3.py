import boto
import yaml

import util


def download(key, secret, bucket, path=[]):
  # Create the connection
  conn = boto.connect_s3(key, secret)
  bucket = conn.get_bucket(bucket, validate=False)

  # Initialize the config with the pistachio keys
  config = {
    'pistachio': {
      'key': conn.access_key,
      'secret': conn.secret_key,
    }
  }
  # For each folder
  for folder in reversed(path):
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

  return config
