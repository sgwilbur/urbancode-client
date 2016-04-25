#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucd-example_template.py --help

Example use:

./ucd-example_template.py -s https://192.168.1.117 -p XXX arg1 arg2 ... argN

'''
import json
import urllib
from pprint import pprint

import sys
import getopt

from urbancode_client.deploy import ucdclient

debug = 0
user = 'PasswordIsAuthToken'
password = ''
base_url = ''

def usage():
  print ''' ucd-example_template
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

  ucd = ucdclient.ucdclient( base_url, user, password , debug )

  #application_id ='aa93dec4-b721-4106-bb1d-c314ccf91286'
  application_id ='Node+App+2'
  name = 'ENV'
  description = 'environment'
  color = '#00B2EF'

  environment_cli_uri = '/cli/environment/createEnvironment?'
  environment_cli_params = 'application=%s&name=%s' % ( application_id, name )
  #environment_cli_params = 'application=%s' % ( application_id )

  # r = ucd.put( uri='%s%s' % (environment_cli_uri, environment_cli_params) )
  #r = ucd.post( '/cli/environment/createEnvironment?application=Node+App+2&name=ENV5' )
  r = ucd.put_plain( '/cli/environment/createEnvironment?application=Node+App+2&name=ENV5' )
  ucd.debug_response( r )

if __name__ == '__main__':
  __main__()
