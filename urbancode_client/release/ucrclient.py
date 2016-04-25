import json

from .. import common
'''
 UrbanCode Release Client for implemneting any specific behavior for Release.

 See the API for more details:

 conventions:
 http://www-01.ibm.com/support/knowledgecenter/SS4GCC_6.1.2/com.ibm.urelease.doc/topics/rest_api_ref_conventions.html?lang=en

'''
class ucrclient( common.client ):

  application_uri = '/applications'

  change_uri = '/changes'
  change_type_uri = '/changeTypes'
  change_statuses_uri = '%s/statuses' % ( change_uri )

  initiative_uri = '/initiatives'

  release_uri = '/releases'
  release_editable_uri = '%s/editable' % (release_uri)

  '''
   Application methods
  '''
  def get_applications( self ):
    return self.get_json( uri=self.application_uri )

  '''
   Change methods
  '''
  def get_change_types( self ):
   return self.get_json( self.change_type_uri )

  def get_change_statuses( self ):
    return self.get_json( self.change_statuses_uri )

  def get_changes( self ):
    return self.get_json( self.change_uri )

  #FIXME: Cannot create with just typeId, must have a valid type object or Change shows no type..., actually typeId seems to be ignored
  # so this is probably a defect on the server side or a workaround to some other problem
  def create_change( self, change_type, typeId, name, status, severity, releaseId='', applicationId='', initiativeId='', description='' ):

    #new_change = {'type' : change_type, "typeId":typeId, "name": name, "status": status, "severity": severity, "release": releaseId, "application": applicationId, "initiative": initiativeId, "description":description }
    new_change = {'type' : change_type, "name": name, "status": status, "severity": severity, "release": releaseId, "application": applicationId, "initiative": initiativeId, "description":description }
    body = json.dumps( new_change )
    return self.post_json( uri=self.change_uri, data=body )

  def delete_change( self, id ):
    this_change_uri = '%s/%s' % ( self.change_uri, id )
    r = self.delete( uri=this_change_uri )

  '''
   Initative methods
  '''
  def get_initiatives( self ):
    return self.get_json( self.initiative_uri )

  def create_initative( self, name, description='' ):
    initiative_body = { 'name' : name,  'description': description }
    body = json.dumps( initiative_body )
    return self.post_json( uri=self.initiative_uri, data=body )

  def delete_initiative( self, id ):
    this_initative_uri = '%s/%s' % ( self.initiative_uri, id )
    r = self.delete( uri=this_initative_uri )


  '''
    Release methods
  '''
  def get_release( self, id, format='' ):
    release_format = '?format=%s' % (format) if format else ''
    return self.get_json( uri='%s/%s%s' % ( self.release_uri, id, release_format ) )

  '''
   Get a simple list of releases id/name pairs
  '''
  def get_releases( self ):
    return self.get_json( uri='%s/name' % (self.release_uri) )

  def get_releases_editable( self ):
    return self.get_json( uri=self.release_editable_uri )
