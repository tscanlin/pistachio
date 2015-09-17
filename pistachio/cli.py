import argparse
import yaml
import pistachio
import sys
import re

def credential_name(string):
  if string == '':
    return ''

  if re.match('^[0-9a-zA-Z\.]+$', string):
    return string
  else:
    raise argparse.ArgumentTypeError('Value must match ^[0-9a-zA-Z\.]+$')


def main():
  parsers = {}
  parsers['super'] = argparse.ArgumentParser(
    description='Secure Credential Storage/Retrieval'
  )

  subparsers = parsers['super'].add_subparsers()
  parsers['get'] = subparsers.add_parser('get',
                                         help='retrieve a credential')
  parsers['get'].add_argument('credential', type=str,
                              help='credential to retrieve')
  parsers['get'].set_defaults(action='get')

  parsers['getall'] = subparsers.add_parser('getall',
                                            help='retrieve all credentials')
  parsers['getall'].set_defaults(action='getall')

  parsers['put'] = subparsers.add_parser('put',
                                         help='store a credential')
  parsers['put'].add_argument('credential', type=credential_name,
                              help='credential name')
  parsers['put'].add_argument('value', type=str,
                              help='credential value')
  parsers['put'].set_defaults(action='put')

  # default command is 'getall'
  if len(sys.argv) == 1:
    args = parsers['super'].parse_args(['getall'])
  else:
    args = parsers['super'].parse_args()

  if 'action' in vars(args):
    if args.action.lower() == 'get':
      print(pistachio.getSecret(args.credential))
    elif args.action.lower() == 'put':
      pistachio.putSecret(args.credential, args.value)
    else: # getall
      print(yaml.dump(pistachio.load(), default_flow_style=False))
