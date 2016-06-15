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

from urbancode_client.deploy import ucdclient
from urbancode_client.release import ucrclient
from urbancode_client import utils

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

  # GET http://base_url/releases/
  # ?filterFields=dateCreated
  # &filterType_dateCreated=gt
  # &filterClass_dateCreated=Long
  # &filterValue_dateCreated=1421171883574
  # &orderField=dateCreated
  # &sortType=asc
  event_name = "201605"
  event_query = "/events?filterFields=name&filterType_name=eq&filterClass_name=String&filterValue_name=%s" % ( event_name )

  events = ucr.get_json( event_query )
  #pprint( events )

  if len( events ) > 1:
    print( 'Returned more than one event, not sure what to do with this')
    pprint( events )
    sys.exit(1)

  relatedDeployment = ucr.get_json( '/relatedDeployments/%s?format=details' % ( events[0]['relatedDeployment']['id'] ) )
  # pprint( relatedDeployment )

  scheduledDeployments = [ current['id'] for current in relatedDeployment['scheduledDeployments'] ]
  pprint( scheduledDeployments )

  for sd_id in scheduledDeployments:
    scheduledDeployment = ucr.get_json( '/scheduledDeployment/%s' % (sd_id) )
    pprint( scheduledDeployment, depth=1 )

    de = scheduledDeployment[ 'deploymentExecution' ]

    print( '#' * 120 )
    # {u'approval': {...},
    #  u'autoManualTaskNotification': False,
    #  u'autoPickVersions': False,
    #  u'autoStart': False,
    #  u'dateCreated': 1462906112415,
    #  u'deploymentExecution': {...},
    #  u'derivedName': u'Sample Release:DEV-1 at May 10, 2016 at 7:48:00 PM GMT',
    #  u'environment': {...},
    #  u'executingUser': u'admin',
    #  u'gateStatus': u'PASSED',
    #  u'id': u'3354ab35-a97f-4ef0-ae13-d4dde07066fe',
    #  u'phase': {...},
    #  u'phases': [...],
    #  u'regexPattern': False,
    #  u'release': {...},
    #  u'scheduledDate': 1462909680000,
    #  u'shortName': u'May 10, 2016 at 7:48:00 PM GMT',
    #  u'status': u'COMPLETE',
    #  u'statusState': u'GREEN',
    #  u'transientProgress': 100,
    #  u'version': 4,
    #  u'versions': [...]}

    print( scheduledDeployment['id'] )
    print( scheduledDeployment['derivedName'] )
    print( scheduledDeployment['shortName'] )

    print( 'Deployment Execution: ')
    # u'deploymentExecution': {u'dateCreated': 1462906112421,
    #                       u'endTimeActual': 1462906215330,
    #                       u'endTimeEstimated': 1462906215287,
    #                       u'endTimePlanned': 1462910880000,
    #                       u'ghostedDate': 0,
    #                       u'hasEdit': True,
    #                       u'id': u'c04930da-f0b5-4047-bb81-22fe53d92c02',
    #                       u'locked': False,
    #                       u'name': u'Default Plan',
    #                       u'notifications': [],
    #                       u'segments': [...],
    #                       u'startTimeActual': 1462906165941,
    #                       u'status': u'COMPLETE',
    #                       u'stopSync': False,
    #                       u'suggestedTasks': [],
    #                       u'syncSegments': True,
    #                       u'version': 2},
    print( '\t' + de['id'] )
    print( '\t' + de['name'] )
    print( '\t' + de['status'] )

    print( '\tSegments:')
    for segment in de['segments']:
    #   {u'autostart': False,
    #                                      u'dateCreated': 1462914544830,
    #                                      u'durationPlanned': 0,
    #                                      u'endTimeActual': 0,
    #                                      u'enforceSequential': False,
    #                                      u'executionPattern': u'SEQUENTIAL',
    #                                      u'id': u'a9745833-4d32-4be0-90a1-00f2af9210ef',
    #                                      u'lastRefresh': 1462914544830,
    #                                      u'name': u'Pre-Deployment Tasks',
    #                                      u'opened': False,
    #                                      u'orderedTaskIds': u'',
    #                                      u'prerequisiteOverride': False,
    #                                      u'prerequisites': [],
    #                                      u'relativePosition': 0,
    #                                      u'startTimePlanned': 1462918380000,
    #                                      u'status': u'EMPTY',
    #                                      u'syncProperties': True,
    #                                      u'syncTasks': True,
    #                                      u'tasks': [],
    #                                      u'userCanExecute': True,
    #                                      u'version': 0},
      print( '\t\t' + segment['name'] )

    print( '#' * 120 )


if __name__ == '__main__':
  __main__()
