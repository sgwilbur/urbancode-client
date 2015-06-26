#!/usr/bin/env python
import requests
# quiet warnings for self-signed certificates
requests.packages.urllib3.disable_warnings()

import json
import re

class DeployClient():

  '''
   Setup a new Deploy client
  '''
  def __init__(self, base_url, user, password ):
    self._DEBUG = False

    self.session_key_header = 'UCD_SESSION_KEY'

    self.base_url = base_url
    self.auth_user = user
    self.auth_password = password

    self.session = requests.Session()

    # Login
    self.session.auth = ( self.auth_user, self.auth_password )
    self.session.verify = False
    response = self.session.get( self.base_url + '/security/user' )

    my_cookie =  response.headers['set-cookie']

    if self.session_key_header in my_cookie:
       re_match = re.search('%s=(.{36});' % ( self.session_key_header ), my_cookie )
       if re_match:
         self.session.headers.update({self.session_key_header: re_match.group(1) })

  '''
    Get wrapper with the session
  '''
  def get( self, uri='' ):
    return self.session.get( self.base_url + uri, headers={'accept': 'application/json'} )

  '''
    Put wrapper
  '''
  def put( self, uri, data):
    return self.session.put( self.base_url + uri, data=data, headers={'accept': 'application/json', 'content-type': 'application/json'} )

  '''
   Helper for debugging the response objects
  '''
  def debug_reponse( self, response ):
    print( "         response.url: %s " % ( response.url ) )
    print( "    response.encoding: %s " % ( response.encoding ) )
    print( " response.status_code: %s " % ( response.status_code ) )
    print( "     response.headers: %s " % ( response.headers ) )
    print( "      session.cookies: %s " % ( self.session.cookies ) )
    print( "     response.headers: %s " % ( response.headers ) )
    print( "        response.text: %s " % ( response.text ) )

def __main__():


  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://192.168.1.117'

  applications_uri = '/rest/deploy/application'

  ucd = DeployClient( base_url, user, password )

  # get the existing applications
  response = ucd.get( uri=applications_uri )
  print( "Get existing applications: %s" % ( response.json() ) )

  # Create a new application
  new_app = {'name':'Application1','description':'','notificationSchemeId':'','enforceCompleteSnapshots':'false','teamMappings':[], }
  body = json.dumps( new_app )

  # Add Application json object to body
  r = ucd.put(uri=applications_uri, data=body )
  print( "Create new application response: %s " % ( r.text ) )
  ucd.debug_reponse( r )


__main__()
