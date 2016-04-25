#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucr-login_for_testing.py --help

Example use:

./ucr-login_for_testing.py -s https://192.168.1.117 -u admin -p XXX arg1 arg2 ... argN

'''
import json
from pprint import pprint

import sys
import getopt
import random

from ucclient import ucclient
from urbancode_client.deploy import ucdclient
from urbancode_client.release import ucrclient

debug = 0
user = ''
password = ''
base_url = ''

def usage():
  print ''' ucr-login_for_testing
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  -u|--user username
  -p|--password password

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

  # Login and pull the license url
  ucr = ucrclient.ucrclient( base_url, user, password , debug )

  licenses = ucr.get_json( '/license' )
  # pprint( licenses )

  print( 'Licenses: ' )
  for license in licenses:
    if license['available'] == -99:
      print( ' %s ( No licenses of this type )' % ( license['feature'] ) )
    else:
      print( ' %s ( %s / %s )' % ( license['feature'], license['used'], license['available']) )

if __name__ == '__main__':
  __main__()
