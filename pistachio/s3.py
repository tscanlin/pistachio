import sys
import boto3
import botocore
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
    print('[Pistachio]: Using your .pistachio keys and secrets. This will be deprecated soon.')
    session = boto3.session.Session(aws_access_key_id=settings['key'],
                                    aws_secret_access_key=settings['secret'])
  else:
    # Set up session with specified profile or 'default'
    if not settings.get('profile'):
      print('[Pistachio]: Did not specify AWS profile - Using default profile')
      settings['profile'] = 'default'

    session = boto3.session.Session(profile_name=settings['profile'])
    print('[Pistachio]: Using {} profile'.format(session.profile_name))
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

  # Reset the config_partials array
  global config_partials
  config_partials = {}
  # Must store partials by path, so that we guarantee path hierarchy when merging them
  config_partials[settings['path']] = []

  # Create thread store if we're running in parallel
  if settings['parallel']:
    threads = []

  # Iterate through yaml files in the set path
  for key in Bucket.objects.filter(Prefix=settings['path'] + '/', delimiter='/'):
    if key.key.endswith('.yaml'):
      # Download and store
      if settings['parallel']:
        thread = threading.Thread(target=fetch_config_partial, args=(settings['path'], key))
        thread.start()
        threads.append(thread)
      else:
        fetch_config_partial(settings['path'], key)

  # Wait for the threads to finish if we're running in parallel
  if settings['parallel']:
    for thread in threads:
      # timeout in 5 seconds
      thread.join(5)

  # Merge them together
  for config_partial in config_partials[settings['path']]:
    util.merge_dicts(config, config_partial)

  return config


def fetch_config_partial(path, key):
  """ Downloads contents of an S3 file given an S3 key object """
  try:
    pool.acquire()
    contents = key.get()['Body'].read()

    # Append the config_partials with the downloaded content
    global config_partials
    config_partials[path].append(yaml.load(contents))

  except botocore.exceptions.ClientError as e:
    print("[Pistachio]: S3 exception on %s: %s" % (key, e))
  except:
    print("[Pistachio]: Unexpected error: %s" % sys.exc_info()[0])
  finally:
    pool.release()

