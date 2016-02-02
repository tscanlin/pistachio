import boto3
import botocore
<<<<<<< 3de298f34d2d1d19eeed4adf5088968fbe5a790d
import sys
=======
>>>>>>> Support boto3 and wipe out changes regarding my AWS credential fetching.
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
<<<<<<< 3de298f34d2d1d19eeed4adf5088968fbe5a790d
  # Temporary support for keys and secrets
  if settings.get('key') and settings.get('secret'):
    print('[Pistachio]: Using your .pistachio keys and secrets')
    session = boto3.session.Session(aws_access_key_id=settings['key'],
                                    aws_secret_access_key=settings['secret'])
  else:
    # Set up session with specified profile or 'default'
    if not settings.get('profile'):
      print('[Pistachio]: Did not specify AWS profile - Using default profile')
      settings['profile'] = 'default'

    session = boto3.session.Session(profile_name=settings['profile'])
    print('[Pistachio]: Using {} profile'.format(session.profile_name))
=======
  # Set up session with specified profile or 'default'
  if not settings.get('profile'):
    print('Warning: Did not specify AWS profile - Using default profile')
    settings['profile'] = 'default'

  session = boto3.session.Session(profile_name=settings['profile'])
  print('Profile: {}'.format(session.profile_name))
>>>>>>> Support boto3 and wipe out changes regarding my AWS credential fetching.

  return session


<<<<<<< 3de298f34d2d1d19eeed4adf5088968fbe5a790d
def download(session, settings):
=======
def download(session, bucket, path=[], parallel=False):
>>>>>>> Support boto3 and wipe out changes regarding my AWS credential fetching.
  """ Downloads the configs from S3, merges them, and returns a dict """
  # Use Amazon S3
  conn = session.resource('s3')
  # Specify bucket being accessed
<<<<<<< 3de298f34d2d1d19eeed4adf5088968fbe5a790d
  Bucket = conn.Bucket(settings['bucket'])
=======
  bucket = conn.Bucket(bucket)
>>>>>>> Support boto3 and wipe out changes regarding my AWS credential fetching.

  # Initialize the config with the pistachio keys
  config = {
    'pistachio': {
<<<<<<< 3de298f34d2d1d19eeed4adf5088968fbe5a790d
      'key': settings.get('key'),
      'secret': settings.get('secret'),
      'profile': session.profile_name,
      'bucket': Bucket.name,
=======
      'profile': session.profile_name,
      'bucket': bucket.name,
>>>>>>> Support boto3 and wipe out changes regarding my AWS credential fetching.
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
<<<<<<< 3de298f34d2d1d19eeed4adf5088968fbe5a790d
    for key in Bucket.objects.filter(Prefix=folder + '/', Delimiter='/'):
=======
    for key in bucket.objects.filter(Prefix=folder+'/', Delimiter='/'):
>>>>>>> Support boto3 and wipe out changes regarding my AWS credential fetching.
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
    print("s3 exception on %s: %s" % (key, e))
  except:
    print("Unexpected error: %s" % sys.exc_info()[0])
  finally:
    pool.release()
