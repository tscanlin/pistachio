import os
import stat
import yaml

# Attempt to load cache from cache_path
def load(cache_path):
  # Load the file from a cache if one exists
  if cache_path and os.path.isfile(cache_path):
    mode = oct(stat.S_IMODE(os.stat(cache_path).st_mode))
    if not mode == '0600':
      raise Exception('Cache file "%s" mode must be set to "0600"' % cache_path)
    return yaml.load(open(cache_path,'r'))

  # Otherwise return None
  return None


# Write cache to cache_path
def write(cache_path, config):
  if cache_path:
    with open(cache_path, 'w') as pistachio_cache:
      pistachio_cache.write( yaml.dump(config, default_flow_style=False))
    os.chmod(cache_path, 0600)
