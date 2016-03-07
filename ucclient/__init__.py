
import requests
# quiet warnings for self-signed certificates
requests.packages.urllib3.disable_warnings()

import json
import re


'''
 UrbanCode Client is the super class to provide the session management and
 wrappers around the high level operations that are shared between all clients.
'''
class ucclient():

  '''
   Setup a new UrbanCode client
  '''
  def __init__(self, base_url, user, password , debug=False):
    self._DEBUG = debug
    self.base_url = base_url
    self.auth_user = user
    self.auth_password = password
    self.session = requests.Session()

    # Login
    self.session.auth = ( self.auth_user, self.auth_password )
    self.session.verify = False
    self.challenge_uri = '/'

    response = self.session.get( self.base_url + self.challenge_uri )

    if 'set-cookie' not in response.headers and response.status_code != requests.codes.ok:
     self.debug_response( response )
     raise Exception( 'Failed to login to UrbanCode' )

    cookies =  response.headers['set-cookie']
    # Figure out which client this is expecting a cookie named UC[BDR]_SESSION_KEY
    re_match = re.search('(UC[BDR]_SESSION_KEY)=(.{36});', cookies )
    if re_match:
      if self._DEBUG:
        print( " %s : %s " % ( re_match.group(1), re_match.group(2) ) )
      self.session.headers.update({re_match.group(1): re_match.group(2) })

  '''
    Get wrappers with the session
  '''
  def get( self, uri ):
    return self.session.get( self.base_url + uri, headers={'accept': 'application/json'} )

  def get_json( self, uri ):
      r = self.get( uri )
      if r.status_code not in [ 200 ]:
        self.debug_response( r )
        raise Exception( 'Error calling GET on %s returned HTTP %d' % ( uri, r.status_code ) )
      return r.json()

  '''
    Put wrapper
  '''
  def put( self, uri, data={} ):
    return self.session.put( self.base_url + uri, data=data, headers={'accept': 'application/json', 'content-type': 'application/json'} )

  def put_json( self, uri, data={}):
    r = self.put( uri, data )
    if r.status_code not in [ 200 ]:
      self.debug_response( r )
      raise Exception( 'Error calling PUT on %s return HTTP %d' % ( uri, r.status_code ) )
    return r.json()

  def put_plain( self, uri, data={} ):
    return self.session.put( self.base_url + uri, data=data, headers={'accept': 'text/plain', 'content-type': 'text/plain'} )

  '''
    Post wrappers
  '''
  def post( self, uri, data={} ):
    return self.session.post( self.base_url + uri, data=data, headers={'accept': 'application/json', 'content-type': 'application/json'} )

  def post_json( self, uri, data={} ):
      r = self.post( uri, data )
      if r.status_code not in [ 201 ]:
        self.debug_response( r )
        raise Exception( 'Error calling POST on %s returned HTTP %d' % ( uri, r.status_code ) )
      return r.json()

  '''
    Delete wrapper
  '''
#  def delete( self, uri ):
#    return self.session.delete( self.base_url + uri, headers={ 'accept':'application/json', 'content-type': 'application/json'} )

  def delete( self, uri ):
    r = self.session.delete( self.base_url + uri, headers={ 'accept':'application/json', 'content-type': 'application/json'} )
    if r.status_code not in [200, 204]:
      self.debug_response( r )
      raise Exception( 'Error calling DELETE on %s returned HTTP %d ' % ( uri, r.status_code ) )
    # returning the response object anyway, since some old calls to this method
    return r

  def delete2( self, uri ):
    r = self.session.delete( self.base_url + uri, headers={ 'accept':'*/*', 'content-type': 'application/x-www-form-urlencoded'} )
    if r.status_code not in [200, 204]:
      self.debug_response( r )
      raise Exception( 'Error calling DELETE on %s returned HTTP %d ' % ( uri, r.status_code ) )
    # returning the response object anyway, since some old calls to this method
    return r


  def delete3( self, uri, data={} ):
    r = self.session.delete( self.base_url + uri, data=data, headers={ 'accept':'application/json', 'content-type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'
} )
    if r.status_code not in [200, 204]:
      self.debug_response( r )
      raise Exception( 'Error calling DELETE on %s returned HTTP %d ' % ( uri, r.status_code ) )
    # returning the response object anyway, since some old calls to this method
    return r

  '''
   Helper for debugging the response object returned
  '''
  def debug_response( self, response ):
    print( " self.session.cookies: %s " % ( self.session.cookies ) )
    print( " self.session.headers: %s " % ( self.session.headers ) )
    print( "         response.url: %s " % ( response.url ) )
    print( "    response.encoding: %s " % ( response.encoding ) )
    print( " response.status_code: %s " % ( response.status_code ) )
    print( "     response.headers: %s " % ( response.headers ) )
    print( "        response.text: %s " % ( response.text ) )
