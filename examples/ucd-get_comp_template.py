#!/usr/bin/env python
'''
Helper to pull the contents of a Component Template

Example use:

./ucd-get_comp_template.py -s https://192.168.1.117 -p XXX

'''
import json
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

  # Peel and specfic arguments off the end for this call
  arg1, arg2 = sys.argv[-2:]

  ucd = ucdclient.ucdclient( base_url, user, password , debug )

  #comp_template_id = '5b36f7a2-a458-48bd-b046-7a44656c5861'
  comp_template_id = '250f14f1-8042-435f-893e-8bc267183c82'
  comp_template_uri = '/rest/deploy/componentTemplate/%s/' % ( comp_template_id )

  comp_template = ucd.get_json( uri=comp_template_uri)

  pprint( comp_template )


if __name__ == '__main__':
  __main__()
