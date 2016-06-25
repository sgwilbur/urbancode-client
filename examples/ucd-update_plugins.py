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
import re
import os
import zipfile
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

  plugin_dir  = '/Volumes/Scribe/home/swilbur@us.ibm.com/clients/35143 - Macys/20160623/plugins/'
  verbose = 0
  delete_plugins = 0

  # Peel and specfic arguments off the end for this call
  arg1, arg2 = sys.argv[-2:]

  ucd = ucdclient.ucdclient( base_url, user, password , debug )

  ## Look at the current plugins
  current_plugins = ucd.get_json( rest_uri )


  for plugin in current_plugins:
    # {u'description': u'This plugin provides steps for launching instances, terminating instances, associating ip addresses, waiting for instances, creating a security group, and getting the public DNS for the Amazon EC2 tool.', u'pluginId': u'com.urbancode.air.plugin.AmazonEC2', u'versionNumber': 4, u'version': u'4.423632', u'ghostedDate': 0, u'id': u'4db7cc91-6993-4287-8cdd-a1e80ec1f5be', u'name': u'AmazonEC2'}
    print( '%s %s %s(%s) ' % (plugin['pluginId'], plugin['name'], plugin['versionNumber'], plugin['version']) )
    #pprint( plugin )

    # if delete_plugins:
    #   print 'Deleting plugin.'
    #   r =  s.delete( url = base_url + rest_uri + '/' + plugin['id'] )
    #   #      print_h( r, s )
    #   if r.status_code == 200:
    #     print 'Success!'
    #   else:
    #     print 'Something went wrong...'
    #     print_h( r, s )

  installed_plugins = [ plugin['pluginId'] for plugin in current_plugins ]

  file_list = os.listdir( plugin_dir );
  plugins_list = [ cur_file for cur_file in file_list if cur_file.endswith('.zip') ]
  #post_url = base_url + rest_uri  + "?UCD_SESSION_KEY=" + ucd.session.headers['UCD_SESSION_KEY']
  post_url = '%s%s?UCD_SESSION_KEY=%s' % (base_url, rest_uri, ucd.session.headers['UCD_SESSION_KEY'] )

  for cur_plugin in plugins_list:
    plugin_archive = zipfile.ZipFile( os.path.join( plugin_dir, cur_plugin), 'r')
    info_xml = plugin_archive.read('info.xml')

    plugin_type            = re.search( '<integration type="(.*)"/>', info_xml).group(1)
    plugin_description     = re.search( '<tool-description>(.*)</tool-description>', info_xml).group(1).strip()
    plugin_release_version = re.search( '<release-version>(.*)</release-version>', info_xml).group(1).strip()
    #print info_xml

    # <identifier version="6" id="com.urbancode.air.plugin.MavenResolve" name="Maven Resolve"/>
    plugin_xml = plugin_archive.read('plugin.xml')
    m = re.search( '<identifier version="(.*)" id="(.*)" name="(.*)"/>', plugin_xml )
    plugin_major_version = m.group(1).strip()
    plugin_id      = m.group(2).strip()
    plugin_name    = m.group(3).strip()

    #print( ' %s %s %s ' % (plugin_type, plugin_description, plugin_release_version ) )
    #print( ' %s %s %s ' % (plugin_major_version, plugin_id, plugin_name ) )

    print( ' %s %s %s(%s) %s' % ( plugin_id, plugin_name, plugin_major_version, plugin_release_version, plugin_type ) )


    if plugin_id in installed_plugins:
      print( 'Already installed, lets check the version')
      # FIXME: this will prevent any version updates from being applied.

      continue
    else:
      print " Uploading: ", cur_plugin
      files = {'file': ( cur_plugin , open( os.path.join( plugin_dir, cur_plugin)  , 'rb'), 'application/zip', {'Expires': '0'})}

      r =  ucd.session.post(post_url, files=files)

      if r.status_code == 200:
        print 'Success!'
      else:
        print 'Something went wrong...'
        ucd.debug_response( r )


__main__()
