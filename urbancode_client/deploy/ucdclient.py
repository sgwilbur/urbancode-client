#
import json
from pprint import pprint

# import ucd modules
from .. import common

'''
 UrbanCode Deploy Client for implemneting any specific behavior for Deploy.
'''
class ucdclient( common.ucclient ):

  applications_uri = '/rest/deploy/application'
  application_create_uri = '/cli/application/create'
  components_uri = '/rest/deploy/component'
  component_create_uri = '/cli/component/create'
  authz_realm_uri = '/security/authorizationRealm'
  team_uri = '/security/team'

  ## Auth Realms

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

  ## Teams

  def create_team( self, name, description ):
    new_team_uri = '/cli/team/create?team=%s&description=%s' % ( name, description )

    r = self.put( uri=new_team_uri )

    if r.status_code == 200:
      return r.json()
    elif r.status_code == 400:
      #print r.text
      return '{}'

  def get_teams( self ):
    return self.get_json( self.teams_uri )

  def delete_team_byid( self, id ):
    team_uri = '%s/%s' % ( self.teams_uri, id )
    r = self.delete( team_uri )

    if r.status_code != 200:
      self.debug_response( r )

  def delete_team( self, name ):
    teams = self.get_teams()

    pprint( teams )
    team = {}
    for cur_team in teams:
      if cur_team['name'] == name:
        team = cur_team

    if not team:
      print( 'delete_team: No team %s found!' % ( name ) )
    else:
      self.delete_team_byid( team['id'] )

  ## Applications

  '''
   Create a new Application
   http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.1/com.ibm.udeploy.api.doc/topics/rest_cli_application.html?lang=en
  '''
  def create_application( self, name, description='' ):
    application = {}
    new_app = {
        'name': name,
        'description': description,
        'notificationSchemeId':'',
        'enforceCompleteSnapshots':'false',
        'teamMappings':[],
    }
    body = json.dumps( new_app )
    r = self.put( uri=self.application_create_uri, data=body )

    if r.status_code == 200:
      application = r.json()
    elif r.status_code == 400:
      print( r.text )

    return application

  def delete_application( self, name ):
    app = {}
    try:
      app = self.get_application( name )
    except Exception as e:
      # print( 'Application does not exist' )
      return

    delete_uri = '%s/%s' % ( self.applications_uri, app['id'] )
    self.delete( delete_uri )

  def get_applications( self ):
    return self.get_json( self.applications_uri )

  def get_application( self, name ):
    app = {}
    for cur_app in self.get_applications():
      if cur_app['name'] == name:
        app = cur_app
        break
    if not app:
     raise Exception('No Application %s found' % (name) )
    return app

  def get_application_byid( self, id ):
    app_uri = '%s/%s' % ( self.applications_uri, id )
    return self.get_json( app_uri )

  ## Components

  def get_components( self ):
    comp = {}
    r = self.get( self.components_uri )
    if r.status_code == 200:
      comp = r.json()
    else:
      self.debug_response( r )

    return comp

  def get_component( self, name ):
    comps = self.get_components()
    for cur_comp in comps:
      if name == cur_comp['name']:
        return cur_comp

    raise Exception( 'Component %s not found ')


  def create_component( self, body ):
    r = self.put( uri=self.component_create_uri, data=json.dumps(body) )
    if r.status_code == 200:
      return r.json()
    elif r.status_code == 400:
      print( r.text )
    else:
      self.debug_response( r )
      raise Exception( 'Failed to Create or Update Component exiting.')

  def tag_component( self, component_id, tag ):
    tag_uri = '/cli/component/tag?component=%s&tag=%s' % ( component_id, tag )
    r = self.put( tag_uri )
    if r.status_code != 204:
      self.debug_response( r )
      raise Exception( 'Failed to tag component')

  def trigger_component_source_import( self, component_id, version_or_tag='*' ):
    import_uri = '/rest/deploy/component/%s/integrate' % ( component_id )
    integrate_props = {
         'properties' : { 'versionOrTag' : version_or_tag }
    }
    body = json.dumps( integrate_props )
    r  = self.put( uri=import_uri, data=body )

    if r.status_code == 200:
      print( 'Successfully submitted Version import request, check the Component Configuration page for more information.')
    else:
      self.debug_response( r )
      raise Exception( 'Failed to request import.')

  def delete_component( self, name ):
    self.delete_component_byid( self.get_component( name ) )

  def delete_component_byid( self, id ):
    delete_uri = '%s/%s' % ( self.components_uri, id )
    r = self.delete( delete_uri )
    if r.status_code != 200:
      self.debug_response( r )
      raise Exception( 'Error deleting component %s' % ( id ) )
