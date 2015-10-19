#!/usr/bin/env python
'''
 Example of comparing the effective permissions of a role, and the ability to
 inspect two roles for differneces.
  Focusing on read-only scenarios.
'''
import json
import re
import urllib
from pprint import pprint
import time, datetime

import sys
sys.path.append('..')
from ucclient.ucd import ucdclient

def __main__():

  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://192.168.1.117'

  ucd = ucdclient( base_url, user, password , 0 )

  application_name = 'JPetStore'

  ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
  snapshot_name = 'AS-%s' % ( ts )
  snapshot_description = 'Automated snapshot'

  # Get application id
  # /rest/deploy/application

  r = ucd.get( '/rest/deploy/application?name=%s' % (application_name) )
  application = r.json()[0]
  #print( application )

  # Get components and get latest version id of each
  get_application_components_uri = '/rest/deploy/component?&filterFields=applications.id&filterValue_applications.id=%s&filterType_applications.id=eq&filterClass_applications.id=UUID' % ( application['id'] )
  r = ucd.get( get_application_components_uri )
  components = r.json()

  # Create Snapshot with all components at latest version
  snapshot_uri = '/rest/deploy/snapshot'
  application_snapshot = { 'name' : snapshot_name, 'applicationId' : application['id'], 'description': snapshot_description, 'versionIds' : [] }
  body = json.dumps( application_snapshot )
  r = ucd.put( uri=snapshot_uri, data=body )
  snapshot = r.json()
  #pprint( snapshot )

  # Build up an array of version ids by grabbing each of the applications components
  # and grabbing the latestVersion id
  snapshot_versions = { 'versionIds' : [] }
  for component in components:
    component_latest_version_uri =  '/rest/deploy/component/%s/latestVersion' % ( component['id'] )
    r = ucd.get( component_latest_version_uri )
    if r.status_code == 200:
      component_version = r.json()
      snapshot_versions['versionIds'].append( component_version['id'])
    else:
      print('%s : Gettting latest version failed, skipping as this components has no versions.' % ( component['name']) )
      #ucd.debug_response( r )

  body = json.dumps( snapshot_versions )
  #pprint( body )
  snapshot_versions_uri = '/rest/deploy/snapshot/%s/versions' % ( snapshot['id'] )
  ucd.put( uri=snapshot_versions_uri, data=body )
  # does not return the updated snapshot just a HTTP 204 for updated

  # To get the final view of the snapshot we grab it at the end
  get_snapshot_uri = '/rest/deploy/snapshot/%s' % ( snapshot['id'] )
  r = ucd.get( get_snapshot_uri )
  updated_snapshot = r.json()
  pprint( updated_snapshot )

__main__()
