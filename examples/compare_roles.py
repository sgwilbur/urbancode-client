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

import sys
sys.path.append('..')
from ucclient.ucd import ucdclient


role_uri = '/security/role'
team_uri = '/security/team'

security_type_uri = '/security/resourceType'
user_uri = '/security/user'
group_uri  = '/security/group'

action_mappings_uri = '/security/role/20000000000000000000000000010001/actionMappings'

permission_groupings = [ 'Agent', 'Agent Pools', 'Application', 'Cloud Connection', 'Component', 'Component Template', 'Environment', 'Process', 'Resource', 'Resource Template', 'Server Configuration', 'Web UI']

for current_group_name in permission_groupings:
  uri_encoded_permission_group_name = urllib.quote( current_group_name )
  actions_uri = '/security/resourceType/%s/actions' % ( uri_encoded_permission_group_name )
  resource_roles_uri = '/security/resourceType/%s/resourceRoles' % ( uri_encoded_permission_group_name )

#  print(' actions: %s \n resourceRoles: %s' % (actions_uri, resource_roles_uri ) )

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

def __main__():

  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://172.16.62.132:8444'

  ucd = ucdclient( base_url, user, password , 0 )

  # Get teams
  print( 'Get Teams')
  r = ucd.get( uri=team_uri )
  teams = r.json()

  for current_team in teams:
    #pprint( current_team )
    current_team_uri = team_uri + '/' + current_team['id']
    r = ucd.get( uri=current_team_uri )
    current_team_full = r.json()
#    pprint( current_team_full )
    print_team( current_team_full )

  # Get roles
  print( 'Get Roles')
  r = ucd.get( uri=role_uri )
  roles = r.json()

  # Get Action Mappings only, otherwise they are included when you get the role
  # '/security/role/fd39f89f-3e31-46de-b24e-09c3e66b9cd4/actionMappings'

  for current_role in roles:
    #pprint( current_role )
    current_role_uri = role_uri + '/' + current_role['id']
    r = ucd.get( uri=current_role_uri )
    current_role_full = r.json()
        #pprint( current_role_full )

    #print( "\n\n >>> \n")



__main__()
