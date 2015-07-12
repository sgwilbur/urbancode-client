from ucclient import ucclient
import json
'''
 UrbanCode Deploy Client for implemneting any specific behavior for Deploy.
'''
class ucdclient( ucclient ):

  authz_realm_uri = '/security/authorizationRealm'

#  def __init__(self, base_url, user, password, debug=False ):
#    self._DEBUG = debug
#    self.session_key_header = 'UCD_SESSION_KEY'

  def get_authz_realm_by_name( self, authz_realm_name ):
    r = self.get( uri=ucdclient.authz_realm_uri )

    if r.status_code != 200:
      raise Exception('Unable to retieve Authorization Realms')
      self.debug_response( r )

    for authz_realm in r.json():
          if authz_realm['name'] == authz_realm_name:
              return authz_realm

    raise Exception('Authorization Realm %s not found' % (authz_realm_name) )

  def create_authz_realm( self, name, description='', authorizationRealmName='com.urbancode.security.authorization.internal.InternalAuthorizationModule'):
    new_authz_realm = { 'name': name , 'description' : description, 'authorizationModuleClassName': authorizationRealmName, 'properties': {'group-mapper': '00000000000000000000000000000000'}}
    body = json.dumps( new_authz_realm )
    r = self.post( uri=ucdclient.authz_realm_uri, data=body )

    if r.status_code == 200:
     return r.json()
    elif r.status_code == 403:
      return self.get_authz_realm_by_name( name )
    else:
      self.debug_response( r )
      raise Exception( 'Failed to create new AuthorizationRealm')
