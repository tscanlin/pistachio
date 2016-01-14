import os
import time
import yaml


# Attempt to load cache from cache_path
def load(settings):
  if not settings.get('cache'):
    return None

  cache = settings['cache']
  # Load the file from a cache if one exists and not expired
  if ((cache.get('path', None) and os.path.isfile(cache['path'])) and
     cache.get('enabled', True) and
     ('expires' not in cache or not is_expired(cache))):
    loaded = yaml.load(open(cache['path'], 'r'))

    # If path exists in settings and cached file and both values don't match - cache is invalid
    if settings.get('path') and loaded['pistachio'].get('path') and settings['path'] != loaded['pistachio']['path']:
      return None

    return loaded

  # Otherwise return None
  return None


# Write cache to cache_path
def write(settings, config):
  if not settings.get('cache'):
    return None
  cache = settings['cache']
  if settings.get('path') and config.get('pistachio'):
    config['pistachio']['path'] = settings['path']
  if cache.get('path', None) and cache['enabled']:
    with open(cache['path'], 'w') as pistachio_cache:
      pistachio_cache.write( yaml.safe_dump(config, default_flow_style=False))
    os.chmod(cache['path'], 0o600)

# Check if cache is expired. 'expires' in minutes
def is_expired(cache):
  if time.time() - os.path.getmtime(cache['path']) > cache['expires']*60:
    return True
  return False
