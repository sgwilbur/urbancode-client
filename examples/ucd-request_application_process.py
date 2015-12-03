#!/usr/bin/env python
'''

Script to trigger a scheduled deployment to run every 15m for any component versions that are passing the required status gates.

'''
import json
from pprint import pprint
import getopt

import os, sys, inspect
sys.path.insert( 0, '/Users/sgwilbur/workspaces/uc-clients')

from ucclient.ucd import ucdclient

debug = 0
user = 'PasswordIsAuthToken'
password = ''
base_url = ''

def usage():
  print ''' ucd-schedule_deployment
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  [-u|--user username (do not supply when using a token) ]
  --password [password|token] - Supply password or token to connect with
  <filename of json request>
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

  json_fname = sys.argv[-1]

  ucd = ucdclient( base_url, user, password , debug )

  with open( json_fname ) as data_file:
    request_body = json.load(data_file)

  request_id = ucd.put_json( uri='/cli/applicationProcessRequest/request', data=json.dumps( request_body ) )
  print request_id

if __name__ == '__main__':
  __main__()
