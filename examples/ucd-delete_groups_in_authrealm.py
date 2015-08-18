#!/usr/bin/env python

import json
import re
import sys
sys.path.append('..')
from ucclient import ucclient

def __main__():

  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://192.168.1.117'

  uri_security_group = '/security/group'
  delete_from_auth_realm_name = 'TestAuthRealm'

  ucd = ucclient( base_url, user, password , 0)

  r = ucd.get( uri=uri_security_group )

  if r.status_code != 200:
    ucd.debug_response( r )
    raise Exception( 'Failed to get groups' )

  groups = r.json()

  for group in groups:
    auth_realm_name = group['authorizationRealm']['name']
    #print( '%s %s %s' % ( group['name'] , group['id'], auth_realm_name ) )

    if auth_realm_name == delete_from_auth_realm_name:
      group_name = group['name']
      group_id = group['id']

      print( 'Found one to delete' )
      print( '%s %s %s' % ( group_name , group_id, auth_realm_name ) )

      uri_delete_group = '%s/%s' % ( uri_security_group, group_id )
      r = ucd.delete( uri=uri_delete_group )

      if r.status_code != 200:
        print( 'Error deleting Group %s with id %s' % ( group_name, group_id ) )
        ucd.debug_response( r )

__main__()
