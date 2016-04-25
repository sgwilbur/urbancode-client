#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucr-get_deployments.py --help

Example use:

./ucd-get_deployments.py -s https://192.168.1.117 -p XXX arg1 arg2 ... argN

'''
import json
from pprint import pprint
import time, datetime

import sys
import getopt

from ucclient import ucclient

debug = 0
user = ''
password = ''
base_url = ''

def usage():
  print ''' ucd-get_deployments
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  -u|--user username
  -p|--password password - Supply password 

  <Insert specific parameters for this example >
'''

def ts_tostr( ts ):
  return time.strftime('%Y-%m-%d %H:%M:%S', ts)

def print_sds( sds ):
  for sd in sds:
    apps = [ app['name'] for app in sd['release']['baseApplication']['children']]
    print ts_tostr( time.gmtime(sd['scheduledDate']/1000) )
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

  ucr = ucclient( base_url, user, password , debug )


  start_time_ms = 1438401600000
  end_time_ms = 1441080000000

  c_start = time.gmtime( start_time_ms / 1000 )
  c_end = time.gmtime( end_time_ms / 1000 )

  print "Times: "
  print ts_tostr( c_start )
  print ts_tostr( c_end )

  query_uri = '?'
  # After
  attribute_name = 'scheduledDate'
  attribute_class = 'Long'

  query_uri += 'filterFields=%(name)s&filterType_%(name)s=%(type)s&filterClass_%(name)s=%(class)s&filterValue_%(name)s=%(value)d' % { 'name': attribute_name, 'type': 'ge', 'class': attribute_class, 'value' : start_time_ms }
  #query_uri += 'filterFields=%(name)s&filterType_%(name)s=%(type)s&filterClass_%(name)s=%(class)s&filterValue_%(name)s=%(value)d' % { 'name': attribute_name, 'type': 'ge', 'class': attribute_class, 'value' : time.mktime( c_start ) }

  # Before
  #attribute_name = 'endTimeOverride' # Only works if the value has been overriden for completed deployments that this is not explicity set this filter fails
  attribute_name = 'scheduledDate'
  attribute_class = 'Long'

  query_uri += '&'
  query_uri += 'filterFields=%(name)s&filterType_%(name)s=%(type)s&filterClass_%(name)s=%(class)s&filterValue_%(name)s=%(value)d' % { 'name': attribute_name, 'type': 'lt', 'class': attribute_class, 'value' : end_time_ms }
  #query_uri += 'filterFields=%(name)s&filterType_%(name)s=%(type)s&filterClass_%(name)s=%(class)s&filterValue_%(name)s=%(value)d' % { 'name': attribute_name, 'type': 'lt', 'class': attribute_class, 'value' : time.mktime( c_end ) }
  query_uri += '&orderField=%(name)s&sortType=asc' % { 'name' :attribute_name }

  #query_uri = ''

  query_uri = '/scheduledDeployments%s' %( query_uri)
  print "Getting scheduledDeployments calling %s " % ( query_uri )

  r = ucr.get( query_uri )
  if r.status_code == 200:
    sds = r.json()
  else:
    ucr.debug_response( r )
    sys.exit(1)

  print 'Filtered results (%s)' % ( r.headers['content-range'] )
  filtered_results = [ ts_tostr( time.gmtime(sd['scheduledDate']/1000) ) for sd in sds ]

  print_sds( sds )

  query_uri = ''
  query_uri = '/scheduledDeployments%s' %( query_uri)
  r = ucr.get( query_uri )
  if r.status_code == 200:
    sds = r.json()
  else:
    ucr.debug_response( r )


  print 'Unfiltered results (%s)' % ( r.headers['content-range'] )
  unfiltered_results = [ ts_tostr( time.gmtime(sd['scheduledDate']/1000) ) for sd in sds ]
  print_sds( sds )

  print '\nDiff'
  for sd in unfiltered_results:
    if sd not in filtered_results:
      print sd


  get_specific_deployment = '/scheduledDeployments/7a15c95e-ccbe-47e0-a6af-20b8e9b79433'

  #r = ucr.get( get_specific_deployment )
  #pprint( r.json() )


if __name__ == '__main__':
  __main__()
