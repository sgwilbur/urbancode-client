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
from datadiff import diff

import sys
sys.path.append('..')
from ucclient.ucd import ucdclient

role_uri = '/security/role'
team_uri = '/security/team'

security_type_uri = '/security/resourceType'
user_uri = '/security/user'
group_uri  = '/security/group'

'''
 Print Team
'''
def print_team( team ):
  id = team['id']
  name = team['name']
  print( ' Team: %s - %s' % ( id, name ) )

  role_mappings = team[ 'roleMappings' ]
  for member_map in role_mappings:
    role = member_map['role']

    member_type = ''
    if 'user' in member_map:
      member_type = 'user'
    elif 'group' in member_map:
      member_type = 'group'
    else:
     raise Exception( 'Unknown role type ' )

    member = member_map[ member_type ]
    print( '\t <%s> %s : %s' % ( role['name'], member_type[0:1], member['name'] ) )

def compare_roles( role1, role2):
  print( 'Comparing %s and %s' % (role1['name'], role2['name']) )

  role1_set = set( role1['actions'] )
  role2_set = set( role2['actions'] )
  in1only = role1_set - role2_set
  in2only = role2_set - role1_set

  if not in1only and not in2only:
    print('Roles are equal')
  else:
    if in1only:
      print( 'In %s only [%s]' % (role1['name'], ', '.join(in1only) ) )
      for action_id in in1only:
        print( '\taction: %s ' % ( role1['actions'][ action_id ] ) )
    if in2only:
      print( 'In %s only [%s]' % (role2['name'], ', '.join(in2only) ) )
      for action_id in in2only:
        print( '\taction: %s ' % ( role1['actions'][ action_id ] ) )


def __main__():
  # hard coded
  user = 'PasswordIsAuthToken'
  password = '51d0e176-3fec-4e58-ab41-62df4e13eab8'
  base_url = 'https://192.168.1.117'
  ucd = ucdclient( base_url, user, password , 0 )

  # Get teams
  #print( 'Get Teams')
  #r = ucd.get( uri=team_uri )
  #teams = r.json()

  #for current_team in teams:
    #current_team_uri = team_uri + '/' + current_team['id']
    #r = ucd.get( uri=current_team_uri )
    #current_team_full = r.json()
    #print_team( current_team_full )

  # Get roles
  #print( 'Get Roles')
  r = ucd.get( uri=role_uri )
  if r.status_code != 200:
    ucd.debug_response( r )
    return

  # Get the quick list of roles
  roles = r.json()
  print( 'Defined Roles: ' + ', '.join([ role['name'] for role in roles] ) )

  # Get Action Mappings only, otherwise they are included when you get the role
  # '/security/role/fd39f89f-3e31-46de-b24e-09c3e66b9cd4/actionMappings'

  #pprint( roles )
  role_dict = {}
  for role in roles:
    role_dict[ role['name'] ] = {}
    role_dict[ role['name'] ]['name'] = role['name']
    role_dict[ role['name'] ]['id'] = role['id']
    current_role_uri = '%s/%s/actionMappings' % (role_uri, role['id'] )
    r = ucd.get( uri=current_role_uri )
    #ucd.debug_response( r )
    actions = r.json()
    action_dict = {}
    for cur_action in actions:
      action_dict[ cur_action['action']['id'] ] = cur_action['action']
    role_dict[ role['name'] ]['actions'] = action_dict
    #pprint( actions )

  #pprint( role_dict )

  role_name1 = 'Observer'
  role_name2 = 'Stakeholder'

  if role_name1 in role_dict and role_name2 in role_dict:
    compare_roles( role_dict[ role_name1 ], role_dict[ role_name2 ] )

__main__()
