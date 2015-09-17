from boto.dynamodb2.exceptions import ConditionalCheckFailedException
from butler import Butler
import credstash
import warnings
import sys
from . import cache
from . import s3
from . import settings

SETTINGS = settings.load()
memo = None

def getSecret(name):
  secret = None
  try:
    secret = credstash.getSecret("{}.{}".format(SETTINGS['path'], name))
  except: # attempt old-style s3 loading
    path = name.split('.')
    all_secrets = Butler(load(SETTINGS))

    # Butler hides key errors, this bubbles them up
    with warnings.catch_warnings():
      warnings.filterwarnings('error')
      try:
        secret = all_secrets.get(path)
      except:
        sys.tracebacklimit=0
        raise KeyError('{} not found!'.format(name))

  return secret

def putSecret(path, secret, version=None):
  name = "{}.{}".format(SETTINGS['path'], path)
  if not version:
    latestVersion = credstash.getHighestVersion(name)
    try:
      version = str(int(latestVersion) + 1)
    except ValueError:
      raise ValueError('Can not autoincrement version. The current version: %s is not an int'.format(latestVersion))

  try:
    if credstash.putSecret(name, secret, version):
      print("{} has been stored".format(path))
  except ConditionalCheckFailedException:
    if version == credstash.getSecret(name,version=version):
      raise ValueError('Version {} already exists. Use the -v flag to specify a new version.'.format(version))

def load(s=SETTINGS):
  # Use memoized if available
  global memo
  if memo:
    return memo

  # Validate the settings
  s = settings.validate(s)

  # Attempt to load from cache unless disabled
  loaded_cache = cache.load(s['cache'])
  if loaded_cache is not None:
    return loaded_cache

  # Otherwise, download from s3, and save to cache
  conn = s3.create_connection(s)
  loaded = s3.download(conn, s['bucket'], s['path'], s['parallel'])
  cache.write(s['cache'], loaded)

  # Memoize
  memo = loaded

  return loaded


def attempt_reload(s=SETTINGS):
  # Validate the settings
  s = settings.validate(s)

  # Attempt to download from s3 and save to cache
  try:
    conn = s3.create_connection(s)
    loaded = s3.download(conn, s['bucket'], s['path'], s['parallel'])
    cache.write(s['cache'], loaded)
    # Memoize
    global memo
    memo = loaded
  except:
    print('Pistachio failed to reload cache')
