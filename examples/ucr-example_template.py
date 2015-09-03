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
sys.path.append('..')
from ucclient import ucclient
from ucclient.ucd import ucdclient
from ucclient.release import ucrclient

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

  ucr = ucclient( base_url, user, password , debug )

  # Do something ...

if __name__ == '__main__':
  __main__()
