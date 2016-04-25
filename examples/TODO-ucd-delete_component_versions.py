#!/usr/bin/env python
'''
Example of creating a new component via the API then importing new versions. The documentation shows how to do this via the cli based APIs, if you also inspect the web client in action you can use both these sources to use the REST APIs instead.

Create new Component:
http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.3/com.ibm.udeploy.api.doc/topics/rest_cli_component_create_put.html
Import New Version of Component:
 http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.3/com.ibm.udeploy.api.doc/topics/rest_cli_component_integrate_put.html

Example use:
./ucd-create_new_components.py -s https://192.168.1.117 -s https://ucd -u admin -p XXX

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
  print ''' ucd-example_template
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  [-u|--user username (do not supply when using a token) ]
  --password [password|token] - Supply password or token to connect with
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

  ucd = ucdclient( base_url, user, password , debug )

  component_name = 'SVN Component 1'
  version = '1.1'

if __name__ == '__main__':
  __main__()
