#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucd-app_bootstrap.py --help

Example use:

./ucd-app_bootstrap.py -s https://192.168.1.117 -u YYY -p XXX

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
  print ''' ucd-app_bootstrap
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

  team_name = 'Team1'
  team = ucd.create_team( team_name, '' )

  app_name = 'Application2'
  application = ucd.create_application( app_name )

  components = ['comp1', 'comp2', 'comp3', 'comp4']

  for component_name in components:
    print( 'Creating new component %s' % ( component_name ) )
    new_component_body = {
            'name' : component_name,
            'description' : ' Testing the programmatic creation of components',
            'sourceConfigPlugin' : 'Subversion',
            'properties':
            {
             'SubversionComponentProperties/repoUrl' : 'svn://localhost/component1/tags',
             'SubversionComponentProperties/watchTags' : 'true',
             'SubversionComponentProperties/includes' : '**/*',
             'SubversionComponentProperties/excludes' : '',
             'SubversionComponentProperties/user' : 'admin',
             'SubversionComponentProperties/password' : 'admin',
             'SubversionComponentProperties/svnPath' : 'svn',
             'SubversionComponentProperties/saveFileExecuteBits' : 'false',
             'SubversionComponentProperties/extensions' : '',
            },
            'importAutomatically' : 'false',
            'useVfs' : 'true',
            'defaultVersionType' : 'FULL',
    }

    # Create Component
    new_comp = ucd.create_component( new_component_body )
    if not new_comp:
      print( 'Not created, must already exist' )
      new_comp = ucd.get_component( component_name )

    pprint( new_comp )

    continue

    # Add any Tags we need to for this component
    ucd.tag_component( new_comp['id'], 'CompTag0' )
    # Import new versions
    ucd.trigger_component_source_import( new_comp['id'], '1.0')


  #####
  ##### Reverse the changes
  #####

  # Delete Team(s)
  #ucd.delete_team( team['name'] )

  # Delete Application(s)
  #ucd.delete_application( app_name )

  # Delete Component(s)
  #for component_name in components:
  #  ucd.delete_component( component_name )

if __name__ == '__main__':
  __main__()
