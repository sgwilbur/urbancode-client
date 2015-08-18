#!/usr/bin/env python
import requests # pip install requests
import json
import re

_DEBUG = True

# hard coded
user = 'admin'
passwd = 'admin' # FIXME # 'password'
base_url = 'http://ucr-demo.ratl.swg.usma.ibm.com'

def __main__():
  s = requests.Session()
  login( s )
  s.headers.update({'content-type': 'application/json;charset=UTF-8'})

  #change_id = create_test_change( s )
  #delete_change( s, change_id )

  #all_changes = get_all_changes( s )
  changes_results_set = get_change_by_externalid( s, '64' )
  print changes_results_set
  
'''
 UCR login, simple auth and store the session key in the session headers
'''
def login( session ):
  # login
  session.auth = ( user, passwd )
  session.verify = False
  response = session.get( base_url + '/security/user' )
  #print_response_details( s, r )

  # Capture session key
  my_session_key =  response.headers['set-cookie']
  if 'UCR_SESSION_KEY' in my_session_key:
     match = re.search('UCR_SESSION_KEY=(.{36});', my_session_key )
     if match:
       session.headers.update({'UCR_SESSION_KEY': match.group(1) })

'''
 Create a simple Change with hardcoded values for the ucr-demos server
'''
def create_test_change( session ):
  # Example submission captured via browser REST client {"checkBox":false,"typeId":"21ee2bc1-2960-43b6-8df8-b6186ee71a81","name":"Test Add Change","status":"New","severity":"S1","release":"00000000-0000-0000-0000-000000000036","application":"d6ae7c3c-7252-4d43-a4d3-49a45e272272","initiative":null,"description":"Testing a submit","type":{"icon":"testing","name":"Test","id":"21ee2bc1-2960-43b6-8df8-b6186ee71a81","version":0,"dateCreated":1417454469679}}
  new_item_dict = {"checkBox":'false',"typeId":"21ee2bc1-2960-43b6-8df8-b6186ee71a81","name":"Test Add Change","status":"New","severity":"S1","release":"00000000-0000-0000-0000-000000000036","application":"d6ae7c3c-7252-4d43-a4d3-49a45e272272","initiative":'null',"description":"Testing a submit","type":{"icon":"testing","name":"Test","id":"21ee2bc1-2960-43b6-8df8-b6186ee71a81","version":0,"dateCreated":'1417454469679'}}
  #print "new_item_dict: ", new_item_dict

  body = json.dumps( new_item_dict )

  url = base_url + '/changes'
  session.headers.update({'content-type': 'application/json;charset=UTF-8'})
  response = session.post(url=url, data=body )
  #print_response_details(s,r)

  if response.status_code != 201:
    print_response_details( session, response )
    raise Exception( 'Failed to create Change')
  else:
    obj = response.json()

  print obj
  change_id = obj['id']
  print "Created new change: %s " % ( change_id )
  return change_id

'''
 Get all changes
'''
def get_all_changes( session ):

  query_url = '/changes/' # '/changes/?filterFields=name&orderField=name&filterType_name=like&filterValue_name=Test&filterClass_name=String'

  response = session.get( base_url + query_url, headers={'accept': 'application/json'} )
  print_response_details( session, response )

  if response.status_code != 200:
    print_response_details( session, response )
    raise Exception( 'Failed to query Changes')

  return response.json()

'''
 Test querying the Changes endpoint using the filterFields parameters
'''
def get_change_by_externalid( session, external_id ):

  #query_url = '/changes/?filterFields=&filterFields=name&orderField=name&filterType_=like&filterValue_=%s&filterClass_=String&filterType_name=like&filterValue_name=Add&filterClass_name=String' % ( external_id )
  query_url = '/changes/?filterFields=&filterType_=like&filterValue_=%s&filterClass_=String' % ( external_id )

  url = base_url + query_url
  session.headers.update({'content-type': 'application/json;charset=UTF-8', 'accept': 'application/json'})
  response = session.get( url )
  #print_response_details( session, response )

  if response.status_code != 200:
    print_response_details( session, response )
    raise Exception( 'Failed to query Changes')

  return response.json()

'''
 Delete change by the unique id
'''
def delete_change( session, change_id ):
  print "Trying to delete change %s " % ( change_id )
  url = base_url + '/changes/%s' % ( change_id )

  session.headers.update( {'content-type': 'application/json;charset=UTF-8'})
  response = session.delete( url=url )
  #print_response_details( session, response )

  if response.status_code == 200:
    print "Deleted Change %s " % ( change_id )

'''
 Helper to debug
'''
def print_response_details( session, response ):

  print "            response.url: %s " % ( response.url )
  print "       response.encoding: %s " % ( response.encoding )
  print "    response.status_code: %s " % ( response.status_code )
  print "        response.headers: %s " % ( response.headers )
  print "        session.cookies: %s " % ( session.cookies )
  print "        response.headers: %s " % ( response.headers )
  print "           response.text: %s " % ( response.text )

__main__()
