from . import main
import yaml
import argparse

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Pistachio - Credential Loader for S3 Stored Credentials')
  parser.add_argument('section', type=str, nargs='*',
                      help='sections of the config to load (supports multiple)')
  parser.add_argument('-o', '--output', dest='output', default='yaml', metavar='TYPE',
                      help='output type supports yaml (default), bash, and docker')
  parser.add_argument('--bucket', type=str,
                      help='s3 bucket to load credentials from')
  parser.add_argument('--path', type=str,
                      help='s3 path to load credentials from')
  parser.add_argument('--skipauth', action='store_true', default=False,
                      help='skip auth')
  parser.add_argument('--parallel', action='store_true', default=False,
                      help='parallelize')
  parser.add_argument('--cache', type=str, default=None,
                      help='parallelize')

  args = parser.parse_args()

  if args.bucket:
    main.SETTINGS['bucket'] = args.bucket
  if args.path:
    main.SETTINGS['path'] = args.path
  if args.skipauth:
    main.SETTINGS['skipauth'] = args.skipauth
  if args.parallel:
    main.SETTINGS['parallel'] = args.parallel
  if args.cache:
    if main.SETTINGS and not isinstance(main.SETTINGS.get('cache', None), dict):
      main.SETTINGS['cache'] = {}
    main.SETTINGS['cache']['path'] = args.cache

  credentials = main.load()

  sections = args.section
  if not sections:
    sections = credentials.keys()

  if args.output == 'yaml':
    print(yaml.dump(credentials, default_flow_style=False)),
  elif args.output in ('bash', 'docker'):
    for section in sections:
      for key in credentials[section]:
        if isinstance(credentials[section][key], dict):
          # skip dicts (what should we do for nested keys?)
          continue

        if args.output == 'bash':
          print "export %s='%s'" % (str(key).upper(), credentials[section][key])
        elif args.output == 'docker':
          print "-e %s='%s'" % (str(key).upper(), credentials[section][key]),
  else:
    print "Invalid output type: %s" % args.output
