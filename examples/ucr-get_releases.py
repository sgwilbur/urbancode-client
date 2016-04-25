#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucr-get_releases.py --help

Example use:

./ucd-get_releases.py -s https://192.168.1.117 -u user -p XXX arg1 arg2 ... argN

'''
import json
from pprint import pprint
import time, datetime

import sys
import getopt

from ucclient import ucclient
from ucclient import utils
from urbancode_client.deploy import ucdclient
from urbancode_client.release import ucrclient

debug = 0
user = ''
password = ''
base_url = ''

def usage():
  print ''' ucd-get_releases
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  -u|--user username
  -p|--password password - Supply password
'''

def ts_tostr( ts ):
  return time.strftime('%Y-%m-%d %H:%M:%S', ts)

def print_sds( sds ):
  for sd in sds:
    apps = [ app['name'] for app in sd['release']['baseApplication']['children']]
    print ts_tostr( time.gmtime(sd['scheduledDate']/1000) )
    print utils.print_javats( sd['scheduledDate'] )
#    print '''%s
#    %s
#    Applications:
#      %s
#    ''' % ( ts_tostr( time.gmtime(sd['scheduledDate']/1000) ), sd['release']['name'], ', '.join(apps) )
    #pprint( sds )

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

  start_time_ms = 1438401600000
  end_time_ms = 1441080000000

  c_start = time.gmtime( start_time_ms / 1000 )
  c_end = time.gmtime( end_time_ms / 1000 )

  #  print "Times: "
  #  print ts_tostr( c_start )
  #  print ts_tostr( c_end )

  #r = ucr.get( get_specific_deployment )
  #pprint( r.json() )

  releases = ucr.get_releases()

  for release in releases:
    cur_release = ucr.get_release( id=release['id'], format='pipeline' )
    target_date = utils.javats_tostr( cur_release['targetDate'] ) if 'targetDate' in cur_release else '[No Target Date Set]'
    print( '%s - %s ' % ( cur_release['name'], target_date ) )



if __name__ == '__main__':
  __main__()
