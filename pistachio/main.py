import cache
import s3
import settings


def load(s=settings.load()):
  # Validate the settings
  s = settings.validate(s)

  # Attempt to load from cache
  loaded_cache = cache.load(s['cache'])
  if loaded_cache is not None: return loaded_cache

  # Otherwise, download from s3, and save to cache
  loaded = s3.download(s['key'], s['secret'], s['bucket'], s['path'])
  cache.write(s['cache'], loaded)

  return loaded


def attempt_reload(s=settings.load()):
  # Validate the settings
  s = settings.validate(s)

  # Attempt to download from s3 and save to cache
  try:
    loaded = s3.download(s['key'], s['secret'], s['bucket'], s['path'])
    cache.write(s['cache'], loaded)
  except:
    print('Pistachio failed to reload cache')
