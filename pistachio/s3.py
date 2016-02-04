import boto
import sys
import threading
import yaml

from . import util

# This is module level so it can be appended to by multiple threads
config_partials = None

# rate limit
maxconn = 100
pool = threading.BoundedSemaphore(value=maxconn)

def create_connection(settings):
  """ Creates an S3 connection using credentials is skipauth is false """
  if settings.get('skipauth'):
    conn = boto.connect_s3()
  else:
    conn = boto.connect_s3(settings['key'], settings['secret'])
  return conn


def download(conn, bucket, path=[], parallel=False):
  """ Downloads the configs from S3, merges them, and returns a dict """
  bucket = conn.get_bucket(bucket, validate=False)

  # Initialize the config with the pistachio keys
  config = {
    'pistachio': {
      'key': conn.access_key,
      'secret': conn.secret_key,
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
    for key in bucket.list(folder+'/', delimiter='/'):
      if key.name.endswith('.yaml'):
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
      # timeout in 5 seconds
      thread.join(5)

  # Merge them together
  for folder in reversed(path):
    for config_partial in config_partials[folder]:
      util.merge_dicts(config, config_partial)

  return config


def fetch_config_partial(folder, key):
  """ Downloads contents of an S3 file given an S3 key object """
  try:
    pool.acquire()
    contents = key.get_contents_as_string()

    # Append the config_partials with the downloaded content
    global config_partials
    config_partials[folder].append(yaml.load(contents))

  except boto.exception.S3ResponseError:
    print("boto exception on %s" % key )
  except:
    print "Unexpected error:", sys.exc_info()[0]
  finally:
    pool.release()
