import logging

from . import cache
from . import s3
from . import settings

logger = logging.getLogger(__name__)
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
  loaded = s3.download(session, s)
  cache.write(s, loaded)

  # Memoize
  memo = loaded

  return loaded


def attempt_reload(s=SETTINGS):
  # Validate the settings
  s = settings.validate(s)

  # Set defaults before connecting to S3
  s = settings.set_defaults(s)

  # Attempt to download from s3 and save to cache
  try:
    session = s3.create_connection(s)
    loaded = s3.download(session, s)
    cache.write(s, loaded)
    # Memoize
    global memo
    memo = loaded
    logger.info('Successfully reloaded cache')
  except:
    logger.error('Failed to reload cache')
