import os
import time
import yaml


def load(settings):
  """Attempt to load cache from cache_path"""
  cache = settings['cache']

  if not cache:
    return None

  # Load the file from a cache if one exists and not expired
  if is_valid(cache):
    loaded = read(cache)

    settings_path = settings['path']
    cache_path = loaded.get('pistachio',{})['path']

    # Check if cache matches the path we want to load from
    if settings_path and cache_path and settings_path != cache_path:
      return None

    return loaded

  # Otherwise return None
  return None


def write(settings, config):
  """Write cache to cache_path"""
  if not settings.get('cache'):
    return None

  cache = settings['cache']
  cache_disabled = set(cache.get('disable', [])) & set(settings.get('path', []))

  if settings.get('path') and config.get('pistachio'):
    config['pistachio']['path'] = settings['path']
  if cache.get('path') and cache['enabled'] and not cache_disabled:
    with open(cache['path'], 'w') as pistachio_cache:
      pistachio_cache.write(yaml.safe_dump(config, default_flow_style=False))
    os.chmod(cache['path'], 0o600)


def read(cache):
  return yaml.load(open(cache['path'], 'r'))


def is_valid(cache):
  """Check if cache exists and is valid"""
  return exists(cache) and is_enabled(cache) and not is_expired(cache)


def exists(cache):
  return os.path.isfile(cache['path'])


def is_enabled(cache):
  return cache['enabled']


def is_expired(cache):
  """Check if cache is expired. 'expires' in minutes"""
  if 'expires' in cache and time.time() - os.path.getmtime(cache['path']) > cache['expires']*60:
    return True
  return False
