#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucd-example_template.py --help

Example use:

./ucd-get_plugins.py -s https://192.168.1.117 -u user -p XXX arg1 arg2 ... argN

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
  print ''' ucd-get_plugins
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

  # hard coded
  rest_uri    = '/rest/plugin/automationPlugin'
  rest_uri_src= '/rest/plugin/sourceConfigPlugins'

  plugin_dir  = '/Users/sgwilbur/Dropbox/UCD-plugins/'
  verbose = 0
  delete_plugins = 1

  # Peel and specfic arguments off the end for this call
  arg1, arg2 = sys.argv[-2:]

  ucd = ucdclient.ucdclient( base_url, user, password , debug )

  current_plugins = ucd.get_json( rest_uri )

  for plugin in current_plugins:
    print plugin['name'], " (", plugin['version'], ")"
    if verbose:
      print plugin['id']
      print plugin['pluginId']
      print plugin['version']
      print plugin['versionNumber']
      print plugin['description'][0:100], "..."
      print plugin['ghostedDate']

    # if delete_plugins:
    #   print 'Deleting plugin.'
    #   r =  s.delete( url = base_url + rest_uri + '/' + plugin['id'] )
    #   #      print_h( r, s )
    #   if r.status_code == 200:
    #     print 'Success!'
    #   else:
    #     print 'Something went wrong...'
    #     print_h( r, s )

    #   post_url = url + "?UCD_SESSION_KEY=" + s.headers['UCD_SESSION_KEY']
    #
    #   file_list = os.listdir( plugin_dir );
    #   plugins_list = [ cur_file for cur_file in file_list if cur_file.endswith('.zip') ]
    #
    #   for cur_plugin in plugins_list:
    #       print " Uploading: ", cur_plugin
    #       files = {'file': ( cur_plugin , open( os.path.join( plugin_dir, cur_plugin)  , 'rb'), 'application/zip', {'Expires': '0'})}
    # #      continue
    #
    #       r =  s.post(url, files=files)
    # #      print_h( r, s )
    #       if r.status_code == 200:
    #         print 'Success!'
    #       else:
    #         print 'Something went wrong...'
    #         print_h( r, s )

if __name__ == '__main__':
  __main__()
