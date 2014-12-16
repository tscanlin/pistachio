import os
import time
import yaml

# Attempt to load cache from cache_path
def load(cache):
  # Load the file from a cache if one exists and not expired
  if ((cache.get('path', None) and os.path.isfile(cache['path'])) and
     cache.get('enabled', True) and
     ('expires' not in cache or not is_expired(cache))):
    return yaml.load(open(cache['path'],'r'))

  # Otherwise return None
  return None


# Write cache to cache_path
def write(cache, config):
  if cache.get('path', None):
    with open(cache['path'], 'w') as pistachio_cache:
      pistachio_cache.write( yaml.dump(config, default_flow_style=False))
    os.chmod(cache_path, 0600)

# Check if cache is expired. 'expires' in minutes
def is_expired(cache):
  if time.time() - os.path.getmtime(cache['path']) > cache['expires']*60:
    return True
  return False
