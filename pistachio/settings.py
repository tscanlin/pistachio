import os
import stat
import yaml
import ConfigParser

from . import cache
from . import util

""" Special Variables """
# Pistachio
PISTACHIO_FILE_NAME='.pistachio'
PISTACHIO_ALTERNATIVE_FILE_NAME='pistachio.yaml'
# AWS
AWS_DIR='.aws'
AWS_FILE_NAME='credentials'
AWS_ENV_VARIABLES=['aws_access_key_id', 'aws_secret_access_key', 'aws_session_token']

def load():
  """
  Configure pistachio settings
  """
  settings = {}  # Settings
  pistachio_files = []  # Pistachio specific files

  # Search bottom up from the current directory for settings files
  path = os.getcwd()
  while True:
    # Check for PISTACHIO_ALTERNATIVE_FILE_NAME file
    alternative_settings_file = os.path.join(path, PISTACHIO_ALTERNATIVE_FILE_NAME)
    if os.path.isfile(alternative_settings_file): pistachio_files.append(alternative_settings_file)
    # Check for PISTACHIO_FILE_NAME file
    settings_file = os.path.join(path, PISTACHIO_FILE_NAME)
    if os.path.isfile(settings_file): pistachio_files.append(settings_file)
    # Break out if we're at the root directory
    if path == '/': break
    # Check the parent directory next
    path = os.path.abspath(os.path.join(path, os.pardir))

  # Check for a PISTACHIO_FILE_NAME file in the HOME directory
  if os.getenv('HOME'):
    pistachio_settings_path = os.path.abspath(os.path.join(os.getenv('HOME'), PISTACHIO_FILE_NAME))
    if os.path.isfile(pistachio_settings_path): pistachio_files.append(pistachio_settings_path)

  # Load settings from files
  for pistachio_file in reversed(pistachio_files):
    settings.update(validate_pistachio_file(pistachio_file))

  # Override settings from any PISTACHIO environment variables
  for var, val in os.environ.items():
    if var == 'PISTACHIO_PATH':
      # When pistachio path is set through environment variables, folders are ':' delimited
      settings['path'] = val.split(':')
    elif var.startswith('PISTACHIO_'):
      key = var.split('PISTACHIO_', 1)[1]
      settings[key.lower()] = val

  return settings


def fetch_credentials(settings):
  """
  Fetch aws credentials
  """
  aws_credentials = {}  # AWS credentials
  aws_files = []  # AWS specific files

  # Check for a AWS_FILE_NAME file in the HOME -> AWS_DIR directory
  if os.getenv('HOME'):
    aws_settings_path = os.path.abspath(os.path.join(os.getenv('HOME'), AWS_DIR, AWS_FILE_NAME))
    if os.path.isfile(aws_settings_path): 
      aws_files.append(aws_settings_path)

  # Load credentials from file depending on profile set
  for aws_file in reversed(aws_files):
    validated_aws_file = validate_aws_file(aws_file, settings['profile'])
    if validated_aws_file: aws_credentials.update(validated_aws_file)

  # Override credentials from AWS environment variables
  for var, val in os.environ.items():
    if var.lower() in AWS_ENV_VARIABLES:
      aws_credentials[var.lower()] = val

  settings.update({'aws': aws_credentials})

  return settings


def validate_pistachio_file(file):
  loaded = yaml.load(open(file,'r'))

  # Check if it's a proper yaml file
  if not loaded: raise Exception('%s is not a proper yaml file.' % file)

  # Expand the fullpath of the cache, if set
  if 'cache' in loaded:
    loaded['cache']['path'] = os.path.abspath(os.path.join(os.path.dirname(file), loaded['cache']['path']))

  # Enforce open pistachio keys or secrets
  if 'key' in loaded or 'secret' in loaded:
    print('Deprecated: Found "key" and "secret" in {0} - Using boto (aws) credentials instead'.format(file))

  return loaded


def validate_aws_file(file, profile):
  config = ConfigParser.SafeConfigParser()
  loaded = {}

  # Check if it's a proper ini file
  try:
    config.readfp(open(file, 'r'))
  except ConfigParser.MissingSectionHeaderError or ConfigParser.ParsingError:
    raise Exception('%s is not a proper ini file.' % file)

  # Check if profile exists within file
  if not config.has_section(profile):
    return loaded

  # Check file security for aws keys and secrets
  if config.has_option(profile, 'aws_access_key_id') or config.has_option(profile, 'aws_secret_access_key') or config.has_option(profile, 'aws_session_token'):
    mode = oct(stat.S_IMODE(os.stat(file).st_mode))
    if mode not in ['0o600', '0600']:
      raise Exception('AWS credentials file "{0}" contains a key|secret|token. Mode must be set to "0600" or "0o600", not "{1}"'.format(file, mode))

  # Load ini config into a dict
  loaded = dict(config.items(profile))

  return loaded


# Validate settings and set defaults
def validate(settings):
  """
  For the settings to be valid it must fulfill any of the following:
  1. Have a valid cache file
  2. Have a aws_access_key_id & aws_secret_access_key & bucket defined
  3. Have skipauth set to true as well as a bucket defined
  """
  # Default settings
  if 'path' not in settings or settings['path'] is None: settings['path'] = ['']
  if 'cache' not in settings: settings['cache'] = {}
  settings['cache'].setdefault('enabled', True)
  if 'parallel' not in settings: settings['parallel'] = False
  if 'skipauth' not in settings: settings['skipauth'] = False

  # # Check if There is a valid cache
  # if ((settings.get('cache', {}).get('path', None) and os.path.isfile(settings['cache']['path'])) and
  #    # cache exists
  #    settings['cache'].get('enabled', True) and
  #    # cache is enabled
  #    (not settings['cache'].get('expires', None) or not cache.is_expired(settings['cache']))):
  #    # 'expires' doesn't exist or is not expired
  #   pass
  # # Check if aws_access_key_id & aws_secret_access_key & bucket are defined
  # elif 'aws_access_key_id' in settings and 'aws_secret_access_key' in settings and 'bucket' in settings:
  #   pass
  # # Check if userole is set to true & bucket are defined
  # elif settings.get('skipauth') and 'bucket' in settings:
  #   pass
  # else:
  #   raise ValueError("""
  #     For the settings to be valid it must fulfill any of the following:
  #     1. Have a valid cache file
  #     2. Have a aws_access_key_id & aws_secret_access_key & bucket defined
  #     3. Have skipauth set to true as well as a bucket defined
  #     """)

  # Type conversions
  if not isinstance(settings['path'], list):
    settings['path'] = [settings['path']]
  settings['parallel'] = util.truthy(settings['parallel'])
  settings['skipauth'] = util.truthy(settings['skipauth'])

  return settings
