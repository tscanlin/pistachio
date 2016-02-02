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

  # Validate the settings
  s = settings.validate(s)

  # Attempt to load from cache unless disabled
  loaded_cache = cache.load(s)
  if loaded_cache is not None:
    return loaded_cache

  # Set defaults before connecting to S3
  s = settings.set_defaults(s)

  # Otherwise, download from s3, and save to cache
  session = s3.create_connection(s)
<<<<<<< 3de298f34d2d1d19eeed4adf5088968fbe5a790d
  loaded = s3.download(session, s)
=======
  loaded = s3.download(session, s['bucket'], s['path'], s['parallel'])
>>>>>>> Support boto3 and wipe out changes regarding my AWS credential fetching.
  cache.write(s, loaded)

  # Memoize
  memo = loaded

  return loaded


def attempt_reload(s=SETTINGS):
  # Validate the settings
  s = settings.validate(s)

  # Attempt to download from s3 and save to cache
  try:
    session = s3.create_connection(s)
<<<<<<< 3de298f34d2d1d19eeed4adf5088968fbe5a790d
    loaded = s3.download(session, s)
=======
    loaded = s3.download(session, s['bucket'], s['path'], s['parallel'])
>>>>>>> Support boto3 and wipe out changes regarding my AWS credential fetching.
    cache.write(s, loaded)
    # Memoize
    global memo
    memo = loaded
    print('[Pistachio]: Successfully reloaded cache')
  except:
    print('[Pistachio]: Failed to reload cache')
