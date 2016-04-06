import os
import time
import yaml

opened_cache = None


def load(settings):
  """Attempt to load cache from cache_path"""
  if not settings['cache']:
    return None

  # Load the file from a cache if one exists and not expired
  if is_valid(settings):
    return read(settings['cache'])

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
  if not opened_cache:
    opened_cache = yaml.load(open(cache['path'], 'r'))
  return opened_cache


def is_valid(settings):
  """Check if cache exists and is valid"""
  cache = settings['cache']
  if exists(cache) and is_enabled(cache) and not is_expired(cache):
    loaded = read(cache)

    # Check if cache matches the path we want to load from
    if settings['path'] == loaded.get('pistachio',{}).get('path', None):
      return True

  return False


def exists(cache):
  return os.path.isfile(cache['path'])


def is_enabled(cache):
  return cache['enabled']


def is_expired(cache):
  """Check if cache is expired. 'expires' in minutes"""
  if 'expires' in cache and time.time() - os.path.getmtime(cache['path']) > cache['expires']*60:
    return True
  return False
