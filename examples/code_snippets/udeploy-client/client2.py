#!/usr/bin/env python
import requests
import json
import re

# hard coded
user = 'admin'
passwd = 'admin'
base_url = 'https://localhost:8443'

def get_h( s, uri='' ):
  r = s.get( base_url + uri )

  if 1:
    print "r.request.headers: ", r.request.headers
    print "s.cookies: ", s.cookies
    print "r.headers: ", r.headers
    print "r.text: ", r.text

def __main__():
  s = requests.Session()
  s.auth = ( user, passwd )
  s.verify = False
  r = s.get( base_url + '/security/user' )

#  print "r.request.headers: ", r.request.headers
#  print "s.cookies: ", s.cookies
#  print "r.headers: ", r.headers
#  print "r.text: ", r.text

  my_c =  r.headers['set-cookie']

  if 'UCD_SESSION_KEY' in my_c: 
#     m = re.search('UCD_SESSION_KEY=(.{8}-.{4}-.{4}-.{4}-.{12});', my_c )
     m = re.search('UCD_SESSION_KEY=(.{36});', my_c )
     if m:
#       print "match group: ", m.group(1)
       s.headers.update({'UCD_SESSION_KEY': m.group(1) })


  get_h( s, '/rest/deploy/application')
       
  new_item_dict = {'name':'Team.3','description':'','notificationSchemeId':'','enforceCompleteSnapshots':'false','teamMappings':[], }

  print "new_item_dict: ", new_item_dict

#  body = json.dumps({'body': new_item_json })
  body = json.dumps( new_item_dict )
#  body = u'{"body":' + new_item_json +  u', }'
  
  print "body: ", body

  jo = json.loads( body)
  
  print "jo['Name']: ", jo['name']


  url = base_url + '/rest/deploy/application' 
#  s.headers.update({'content-type': 'application/json;charset=UTF-8'})
  r = s.put(url=url, data=body )
  
  print "r.request.headers: ", r.request.headers
  print "s.cookies: ", s.cookies
  print "r.headers: ", r.headers
  print "r.text: ", r.text
  
 
__main__()  