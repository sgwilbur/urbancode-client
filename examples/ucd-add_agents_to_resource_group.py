#!/usr/bin/env python
'''
Helper to add agents with a given pattern name and/or tag to a specific resource group.

 Example of
  Check the usage statement below or run ./ucd-add_agents_to_resource_group.py --help

Example use:

./ucd-example_template.py -s https://192.168.1.117 -u user -p XXX arg1 arg2 ...

'''
import json
import sys
import getopt
import re
from pprint import pprint

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

  agents = ucd.get_json( '/rest/agent' )

  #pprint( agents )

  #  {"name":"ucdandr","agentId":"45bdeeda-a26e-4c85-85bf-0dbee7bdb890","parentId":"2dac4c05-d78b-4ad5-9c6e-dec3a9358aba"}

  name_regex = re.compile( 'ucd.*' )

  tags = ['prd']

  for agent in agents:
    pprint( agent )

    if( re.match( name_regex, agent['name'] ) ):
      print( 'Found an agent matching the pattern: %s ' % (agent['name']) )

      agent_tags = [ tag['name'] for tag in agent['tags'] ]

      # build sets and check length of union
      if len( set( i for i in tags) & set(i for i in agent_tags)):
        print( 'Found an agent with tags we are lookign for' )
        print( 'Tags we want: ', tags )
        print( '  Agent tags: ', agent_tags )

      data = {
        "name":     agent['name'],
        "agentId":  agent['id'],
        "parentId": "2dac4c05-d78b-4ad5-9c6e-dec3a9358aba"
        }
      r = ucd.put( '/rest/resource/resource', data=json.dumps(data) )
      pprint( r )

if __name__ == '__main__':
  __main__()
