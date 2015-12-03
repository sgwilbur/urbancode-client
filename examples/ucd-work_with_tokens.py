#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucd-work_with_tokens.py --help

Example use:

./ucd-work_with_tokens.py -s https://192.168.1.117 -p XXX

'''
import json
from pprint import pprint

import sys
import getopt
sys.path.append('..')
from ucclient.ucd import ucdclient

debug = 0
user = 'PasswordIsAuthToken'
password = ''
base_url = ''

def usage():
  print ''' ucd-work_with_tokens
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  [-u|--user username (do not supply when using a token) ]
  --password [password|token] - Supply password or token to connect with
  <Insert specific parameters for this example >
'''

def __main__():

  global debug, user, password, base_url

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:u:p:v", ['help','server=', 'user=', 'password='])
  except getopt.GetoptError as err:
  # print help information and exit:
    print(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  for o, a in opts:
    if o == '-v':
      debug = True
    elif o in ('-h', '--help'):
      usage()
      sys.exit()
    elif o in ( '-s', '--server'):
      base_url = a
    elif o in ( '-u', '--user'):
      user = a
    elif o in ( '-p', '--password'):
      password = a
    else:
      assert False, "unhandled option"
      usage()
      sys.exit()

  if not base_url or not password:
    print('Missing required arguments')
    usage()
    sys.exit()

  # Peel and specfic arguments off the end for this call
  arg1, arg2 = sys.argv[-2:]

  ucd = ucdclient( base_url, user, password , debug )

  # ... Do some stuff ...
  delete_tokens = False
  tokens_uri = '/security/authtoken'
  users_uri = '/security/user'

  # Get Current Tokens
  tokens = ucd.get_json( tokens_uri )
  pprint( tokens )

  # Create authtoken

  # Get users to get userId
  users = ucd.get_json( '/security/user/?name=*' )
  #print( users )

  # Create a new token

  # admin - 11/5/2015 12:00 PM
  token_body = {
    'userId': "20000000000000000000000001000000",
    'description': "",
    'host': "",
    'expDate': "2015-11-05T06:00:00.000Z",
    'expTime': "1970-01-01T18:00:00.000Z",
    'expiration': 1446746400000,
  }
  # Create a new token
  r = ucd.put( uri=tokens_uri, data=json.dumps(token_body) )
  token = r.json()

  pprint( token )

  # Test to see if we can update a token
  # tokenator -  11/9/15 9:30 AM
  token_body_updated = {
    'id': token['id'],
    'token': token['token'],
    'userId': "18ea7889-76f2-4ea0-ab8a-43558b23f1ab",
    'description': "Updated",
    'host': "",
    'expDate': "2015-11-09T06:00:00.000Z",
    'expTime': "1970-01-01T15:30:00.000Z",
    'expiration': 1447083000000,
  }
  token_uri = '%s/%s' % (tokens_uri, token['id'])
  r = ucd.put( uri=token_uri, data=json.dumps(token_body_updated) )
  # Nope
  ucd.debug_response( r )
  #token = r.json()
  #pprint( token )
  #return

  # Delete all the current tokens
  tokens = ucd.get_json( tokens_uri )
  #print( tokens )

  if delete_tokens:
    for token in tokens:
      token_uri = '%s/%s' % (tokens_uri, token['id'])
      r = ucd.delete( token_uri )
      ucd.debug_response( r )


if __name__ == '__main__':
  __main__()
