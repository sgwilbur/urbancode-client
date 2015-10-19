#!/usr/bin/env python
'''
Example of creating a new component via the API then importing new versions. The documentation shows how to do this via the cli based APIs, if you also inspect the web client in action you can use both these sources to use the REST APIs instead.

Create new Component:
http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.3/com.ibm.udeploy.api.doc/topics/rest_cli_component_create_put.html
Import New Version of Component:
 http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.3/com.ibm.udeploy.api.doc/topics/rest_cli_component_integrate_put.html

Example use:
./ucd-create_new_components.py -s https://192.168.1.117 -s https://ucd -u admin -p XXX

'''
import json
from pprint import pprint

import sys
import getopt
sys.path.append('..')
from ucclient.ucd import ucdclient

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

  ucd = ucdclient( base_url, user, password , debug )

  component_name = 'SVN Component 1'

  # Get list of existing components
  components =  ucd.get_json( '/rest/deploy/component')
  existing_component_names = [ comp['name'] for comp in components ]

  if component_name in existing_component_names:
    for comp in components:
      if component_name == comp['name']:
        print( 'Found existing component.')
        comp_id = comp['id']
        continue
  else:
    print( 'Creating new component.')
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

    body = json.dumps( new_component_body )
    r = ucd.put( uri='/cli/component/create', data=body )

    if r.status_code == 200:
      print( 'Submitted component successfully!')
      comp_id = r.json()['id']
    else:
      ucd.debug_response( r )
      raise Exception( 'Failed to Create or Update Component exiting.')

  # Add any Tags we need to for this component
  tag_uri = '/rest/tag/Component'
  tag_properties = {
    'properties' : {
      'ids': [ comp_id ],
      'name': 'CompTag0'
    }
  }
  r = ucd.put( uri=tag_uri, data=json.dumps( tag_properties) )
  #tag_uri = '/cli/component/tag?component=%s&tag=%s' % ( comp_id, 'CompTag0')
  #r = ucd.put( tag_uri )

  if r.status_code == 204:
    print( 'Successfully added Tag to component')
  else:
    ucd.debug_response( r )
    raise Exception( 'Failed to tag component')

  # Import new versions
  import_uri = '/rest/deploy/component/%s/integrate' % ( comp_id )
  integrate_props = {
   'properties' : { 'versionOrTag' : '1.0' }
  }
  body = json.dumps( integrate_props )
  r  = ucd.put( uri=import_uri, data=body )

  if r.status_code == 200:
    print( 'Successfully submitted Version import request, check the Component Configuration page for more information.')
  else:
   ucd.debug_response( r )
   raise Exception( 'Failed to request import.')

if __name__ == '__main__':
  __main__()
