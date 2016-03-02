import sys
import boto3
import botocore
import logging
import threading
import yaml

from . import util

# This is module level so it can be appended to by multiple threads
config_partials = None

# rate limit
maxconn = 100
pool = threading.BoundedSemaphore(value=maxconn)

def create_connection(settings):
  """ Creates an S3 connection using AWS credentials """
  # Temporary support for keys and secrets
  if settings.get('key') and settings.get('secret'):
    logging.debug('[Pistachio] Using your .pistachio keys and secrets.')
    session = boto3.session.Session(aws_access_key_id=settings['key'],
                                    aws_secret_access_key=settings['secret'])
  else:
    # Set up session with specified profile or 'default'
    if not settings.get('profile'):
      session = boto3.session.Session()
      logging.debug('[Pistachio] Did not specify AWS profile. Defaulting to boto3 credentials.')
    else:
      session = boto3.session.Session(profile_name=settings['profile'])
      logging.debug('[Pistachio] Specified AWS profile. Using profile: {}'.format(session.profile_name))
  return session


def download(session, settings):
  """ Downloads the configs from S3, merges them, and returns a dict """
  # Use Amazon S3
  conn = session.resource('s3')
  # Specify bucket being accessed
  Bucket = conn.Bucket(settings['bucket'])

  # Initialize the config with the pistachio keys
  config = {
    'pistachio': {
      'key': settings.get('key'),
      'secret': settings.get('secret'),
      'profile': session.profile_name,
      'bucket': Bucket.name,
    }
  }
  # For each folder

  # Reset the config_partials array
  global config_partials
  config_partials = {}
  # Must store partials by folder, so that we guarantee folder hierarchy when merging them
  for folder in settings['path']:
    config_partials[folder] = []

  # Create thread store if we're running in parallel
  if settings['parallel']:
    threads = []

  # Iterate through the folders in the path
  for folder in reversed(settings['path']):
    # Iterate through yaml files in the set folder
    for key in Bucket.objects.filter(Prefix=folder + '/', Delimiter='/'):
      if key.key.endswith('.yaml'):
        # Download and store
        if settings['parallel']:
          thread = threading.Thread(target=fetch_config_partial, args=(folder, key))
          thread.start()
          threads.append(thread)
        else:
          fetch_config_partial(folder, key)

  # Wait for the threads to finish if we're running in parallel
  if settings['parallel']:
    for thread in threads:
      # timeout in 5 seconds
      thread.join(5)

  # Merge them together
  for folder in reversed(settings['path']):
    for config_partial in config_partials[folder]:
      util.merge_dicts(config, config_partial)

  return config


def fetch_config_partial(folder, key):
  """ Downloads contents of an S3 file given an S3 key object """
  try:
    pool.acquire()
    contents = key.get()['Body'].read()

    # Append the config_partials with the downloaded content
    global config_partials
    config_partials[folder].append(yaml.load(contents))

  except botocore.exceptions.ClientError as e:
    logging.warning("[Pistachio] S3 exception on %s: %s" % (key, e))
  except:
    logging.warning("[Pistachio] Unexpected error: %s" % sys.exc_info()[0])
  finally:
    pool.release()

