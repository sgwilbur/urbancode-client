#!/usr/bin/env python

import json
import re
#from ucclient import ucclient
import sys
sys.path.append('..')
from ucclient.ucd import ucdclient


def __main__():

  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://172.16.62.138'

  # login
  ucd = ucdclient( base_url, user, password , debug=0)

  '''
   Create an Auth Realm
  '''
  authz_realm_uri = '/security/authorizationRealm'

  authz_realm_name = 'AuthzTestRealm'
  new_authz_realm = { 'name': authz_realm_name , 'description' : '', 'authorizationModuleClassName': 'com.urbancode.security.authorization.internal.InternalAuthorizationModule', 'properties': {'group-mapper': '00000000000000000000000000000000'}}
  body = json.dumps( new_authz_realm )
  #r = ucd.post( uri=authz_realm_uri, data=body )

  print ucd.create_authz_realm( 'testing' )

  # 200 ok should have new authz realm content in response text
  # 403 already exists ?

  #ucd.debug_response( r )
  group_name = 'TestGroup'
  authz_realm_id = ''
  new_group = ''
  '''
   Create a group
  '''
  security_group_uri = '/security/group'

  #r = ucd.put( uri=security_group_uri )


__main__()
