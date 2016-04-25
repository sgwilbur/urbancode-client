#!/usr/bin/env python
'''
 Simple script to delete offline agents.

 Example use:

./ucd-delete_offline_agents.py -s https://192.168.1.117 -p XXX

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
  print ''' ucd-delete_offline_agents
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

  # Just by name
  # /rest/agent?rowsPerPage=250&pageNumber=1&orderField=name&sortType=asc&filterFields=name&filterValue_name=ucd&filterType_name=like&filterClass_name=String

  # By name and status
  # /rest/agent?rowsPerPage=250&pageNumber=1&orderField=name&sortType=asc&filterFields=name&filterFields=status&filterValue_name=ucd&filterType_name=like&filterClass_name=String&filterValue_status=ONLINE&filterType_status=eq&filterClass_status=Enum

  # By name, status, and version
  # /rest/agent?rowsPerPage=250&pageNumber=1&orderField=name&sortType=asc&filterFields=name&filterFields=status&filterFields=agentVersion&filterValue_name=ucd&filterType_name=like&filterClass_name=String&filterValue_status=ONLINE&filterType_status=eq&filterClass_status=Enum&filterValue_agentVersion=6&filterType_agentVersion=like&filterClass_agentVersion=String

  rows_per_page = 1
  status = 'OFFLINE'

  agents_offline = '/rest/agent?rowsPerPage=%d&pageNumber=1&orderField=name&sortType=asc&filterFields=status&filterValue_status=%s&filterType_status=eq&filterClass_status=Enum' % ( rows_per_page, status )
  agents_offline = '/rest/agent?orderField=name&sortType=asc&filterFields=status&filterValue_status=%s&filterType_status=eq&filterClass_status=Enum' % ( status )

  print( 'Checking for offline agents with query: %s' % ( agents_offline ) )

  agents = ucd.get_json( uri=agents_offline )

  print( 'Found %d agents offline.' % ( len(agents) ) )

  for agent in agents:
      # http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.2.0/com.ibm.udeploy.api.doc/topics/rest_cli_agentcli_delete.html?lang=en
      r = ucd.delete( uri='/cli/agentCLI?agent=%s' % ( agent['id'] ) )

      if r.status_code != 204:
        print( 'Error deleting agent %s, error %s' % (agent['id'], r.text ))
        ucd.debug_response( r )


if __name__ == '__main__':
  __main__()
