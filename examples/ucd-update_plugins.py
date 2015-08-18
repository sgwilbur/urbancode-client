#!/usr/bin/env python
import os, requests, json, re

# hard coded
user        = 'admin'
passwd      = 'admin'
base_url    = 'https://172.16.62.177:443'
rest_uri    = '/rest/plugin/automationPlugin'
rest_uri_src= '/rest/plugin/sourceConfigPlugins'

plugin_dir  = '/Users/sgwilbur/Dropbox/UCD-plugins/'
verbose = 1
delete_plugins = 1 

## Simple helper method to print out some session and request info.
def print_h( r, s ):
  print "r.request.headers: ", r.request.headers
  print "s.cookies: ", s.cookies
  print "r.headers: ", r.headers
  print "r.text: ", r.text

##
def __main__():
  s = requests.Session()
  s.auth = ( user, passwd )
  s.verify = False
  r = s.get( base_url + '/security/user' )
  my_c =  r.headers['set-cookie']

  if 'UCD_SESSION_KEY' in my_c: 
     m = re.search('UCD_SESSION_KEY=(.{36});', my_c )
     if m:
       s.headers.update({'UCD_SESSION_KEY': m.group(1) })

  url = base_url + rest_uri

## Look at the current plugins
  r = s.get( url )
  if r.status_code != 200:
    print 'Something went wrong...'
    print_h( r, s )
    exit  

  current_plugins = json.loads( r.text )
  for plugin in current_plugins:
# {u'description': u'This plugin provides steps for launching instances, terminating instances, associating ip addresses, waiting for instances, creating a security group, and getting the public DNS for the Amazon EC2 tool.', u'pluginId': u'com.urbancode.air.plugin.AmazonEC2', u'versionNumber': 4, u'version': u'4.423632', u'ghostedDate': 0, u'id': u'4db7cc91-6993-4287-8cdd-a1e80ec1f5be', u'name': u'AmazonEC2'}
#    print plugin        
    print plugin['id']
    print plugin['name'], " (", plugin['version'], ")"
    if verbose:
      print plugin['pluginId']
      print plugin['version']
      print plugin['versionNumber']
      print plugin['description'][0:100], "..."
      print plugin['ghostedDate']

    if delete_plugins:
      print 'Deleting plugin.'
      r =  s.delete( url = base_url + rest_uri + '/' + plugin['id'] )
      #      print_h( r, s )
      if r.status_code == 200:
        print 'Success!'
      else:
        print 'Something went wrong...'
        print_h( r, s )


  post_url = url + "?UCD_SESSION_KEY=" + s.headers['UCD_SESSION_KEY']

  file_list = os.listdir( plugin_dir );
  plugins_list = [ cur_file for cur_file in file_list if cur_file.endswith('.zip') ]

  for cur_plugin in plugins_list:
      print " Uploading: ", cur_plugin
      files = {'file': ( cur_plugin , open( os.path.join( plugin_dir, cur_plugin)  , 'rb'), 'application/zip', {'Expires': '0'})}
#      continue

      r =  s.post(url, files=files)
#      print_h( r, s )
      if r.status_code == 200:
        print 'Success!'
      else:
        print 'Something went wrong...'
        print_h( r, s )
 
__main__()  
