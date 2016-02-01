from . import cache
from . import s3
from . import settings

SETTINGS = settings.load()
memo = None


def load(s=SETTINGS):
  # Use memoized if available
  global memo
  if memo:
    return memo

  # Fetch AWS credentials
  s = settings.fetch_credentials(s)

  # Validate the settings
  s = settings.validate(s)

  # Attempt to load from cache unless disabled
  loaded_cache = cache.load(s)
  if loaded_cache is not None:
    return loaded_cache

  # Otherwise, download from s3, and save to cache
  conn = s3.create_connection(s)
  loaded = s3.download(conn, s['bucket'], s['path'], s['parallel'])
  cache.write(s, loaded)

  # Memoize
  memo = loaded

  return loaded


def attempt_reload(s=SETTINGS):
  # Fetch AWS credentials
  s = settings.fetch_credentials(s)

  # Validate the settings
  s = settings.validate(s)

  # Attempt to download from s3 and save to cache
  try:
    conn = s3.create_connection(s)
    loaded = s3.download(conn, s['bucket'], s['path'], s['parallel'])
    cache.write(s, loaded)
    # Memoize
    global memo
    memo = loaded
    print('Pistachio successfully reloaded cache')
  except:
    print('Pistachio failed to reload cache')
