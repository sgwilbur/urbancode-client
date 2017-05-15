#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucd-example_template.py --help

Example use:

./ucd-example_template.py -s https://192.168.1.117 -u user -p XXX arg1 arg2 ... argN

'''
import json
import sys
import getopt
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
  #snapshot_id = '683564c6-9ec7-4a5b-b78c-e01f383be7d1'
  snapshot_id = 'ab757d3c-c96e-47a6-b580-6b3aff8071bf'

  snapshot = ucd.get_json( uri='/rest/deploy/snapshot/%s' % (snapshot_id) )
  pprint( snapshot )

  versions = ucd.get_json( uri='/rest/deploy/snapshot/%s/versions' % (snapshot_id) )
  #pprint( versions )

  #return

  print( "\n#### Delete the Snapshot ###" )
  if snapshot['active'] == 'True':
    response = ucd.delete( uri='/rest/deploy/snapshot/%s' % (snapshot_id) )

    if response.status_code != 204:
      print( 'ERROR: %s' % (response) )


  print( "\n#### Iterate overs versions inside the Snapshot ####")

  for version in versions:
    #pprint( version )
    for d_version in version['desiredVersions']:
      pprint( d_version )
      version_id = d_version['id']
      version_name = d_version['name']

      if version_id:
        print( version['name'] )
        print( '\t%s : %s' % (version_id, version_name) )

        response = ucd.delete( uri='/rest/deploy/snapshot/%s' % (snapshot_id) )

        if response.status_code != 200:
          print( 'ERROR deleting component %s : %s' % (version['name'], response.text ) )


  # response = ucd.delete( uri='/rest/deploy/snapshot/%s' % (snapshot_id) )




  # ... Do some stuff ...

if __name__ == '__main__':
  __main__()
