#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucr-example_template.py --help

Example use:

./ucr-example_template.py -s https://192.168.1.117 -u admin -p XXX arg1 arg2 ... argN

'''
import json
from pprint import pprint

import sys
import getopt

from ucclient import ucclient
from urbancode_client.deploy import ucdclient
from urbancode_client.release import ucrclient

debug = 0
user = ''
password = ''
base_url = ''

def usage():
  print ''' ucr-example_template
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

  # Peel and specfic arguments off the end for this call
  arg1, arg2 = sys.argv[-2:]

  ucr = ucrclient.ucrclient( base_url, user, password , debug )

  # Find your snapshot
  snapshot_id = "b4ad4aab-a05f-486f-8ba1-924a1b30b3a9"

  # Get a snapshot version
  snapshot = ucr.get_json( '/versions/%s' % ( snapshot_id) )
  pprint( snapshot )

  # Get the statuses you can apply
  statuses = ucr.get_json( '/status/editableByUser' )
  pprint( statuses )

  # Pick your status
  status_id = "87bfccb1-40d5-4b2c-bbd9-05fb02ac3638"

  # Build status update
  status_to_add = {"appVersion": snapshot_id, "status": status_id ,"canEdit":True }

  # Add Status to version
  r = ucr.post( uri='/versionStatus/', data=json.dumps( status_to_add ) )
  ucr.debug_response( r )

if __name__ == '__main__':
  __main__()
