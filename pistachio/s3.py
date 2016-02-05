import boto3
import botocore
import threading
import yaml

from . import util

# This is module level so it can be appended to by multiple threads
config_partials = None

def create_connection(settings):
  """ Creates an S3 connection using AWS credentials """
  # Set up session with specified profile or 'default'
  if not settings.get('profile'):
    print('[Pistachio]: Did not specify AWS profile - Using default profile')
    settings['profile'] = 'default'

  session = boto3.session.Session(profile_name=settings['profile'])
  print('[Pistachio]: Using {} profile'.format(session.profile_name))

  return session


def download(session, bucket, path=[], parallel=False):
  """ Downloads the configs from S3, merges them, and returns a dict """
  # Use Amazon S3
  conn = session.resource('s3')
  # Specify bucket being accessed
  bucket = conn.Bucket(bucket)

  # Initialize the config with the pistachio keys
  config = {
    'pistachio': {
      'profile': session.profile_name,
      'bucket': bucket.name,
    }
  }
  # For each folder

  # Reset the config_partials array
  global config_partials
  config_partials = {}
  # Must store partials by folder, so that we guarantee folder hierarchy when merging them
  for folder in path:
    config_partials[folder] = []

  # Create thread store if we're running in parallel
  if parallel:
    threads = []

  # Iterate through the folders in the path
  for folder in reversed(path):
    # Iterate through yaml files in the set folder
    for key in bucket.objects.filter(Prefix=folder + '/', Delimiter='/'):
      if key.key.endswith('.yaml'):
        # Download and store
        if parallel:
          thread = threading.Thread(target=fetch_config_partial, args=(folder, key))
          thread.start()
          threads.append(thread)
        else:
          fetch_config_partial(folder, key)

  # Wait for the threads to finish if we're running in parallel
  if parallel:
    for thread in threads:
      thread.join()

  # Merge them together
  for folder in reversed(path):
    for config_partial in config_partials[folder]:
      util.merge_dicts(config, config_partial)

  return config


def fetch_config_partial(folder, key):
  """ Downloads contents of an S3 file given an S3 key object """
  try:
    contents = key.get()['Body'].read()

    # Append the config_partials with the downloaded content
    global config_partials
    config_partials[folder].append(yaml.load(contents))

  except botocore.exceptions.ClientError:
    pass # Access denied. Skip this one.
