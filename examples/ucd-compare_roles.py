#!/usr/bin/env python
'''
 Example of comparing the effective permissions of a role, and the ability to
 inspect two roles for differneces.
  Focusing on read-only scenarios.

  Check the usage statement below or run ./ucd-compare_roles.py --help
'''
import json
import re
import urllib
from pprint import pprint
from datadiff import diff

import sys
import getopt
sys.path.append('..')
from ucclient.ucd import ucdclient

debug = 0
role_uri = '/security/role'
team_uri = '/security/team'

#security_type_uri = '/security/resourceType'
#user_uri = '/security/user'
#group_uri  = '/security/group'

user = 'PasswordIsAuthToken'
password = ''
base_url = ''

#password = '51d0e176-3fec-4e58-ab41-62df4e13eab8'
#base_url = 'https://192.168.1.117'

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

'''
 Compare two Role objects that we built earlier, this requires that the
 actions list is a dict not a list
'''
def compare_roles( role1, role2):
  global debug

  print( 'Comparing %s and %s' % (role1['name'], role2['name']) )
  if debug:
    pprint( role1 )
    pprint( role2 )
  role1_set = set( role1['actions'] )
  role2_set = set( role2['actions'] )
  in1only = role1_set - role2_set
  in2only = role2_set - role1_set

  if not in1only and not in2only:
    print('Roles are equal')
  else:
    if in1only:
      print( 'Only in %s (%d)' % (role1['name'], len(in1only)) )
      if debug:
          print( '[%s]' % (', '.join(in1only) ) )
      for action_id in in1only:
        action = role1['actions'][ action_id ]
        print( '\tAction: %s ' % ( action['description'] ) )
    if in2only:
      print( 'Only n %s (%d)' % (role2['name'], len(in2only) ) )
      if debug:
          print( '[%s]' % (', '.join(in2only) ) )
      for action_id in in2only:
        action = role2['actions'][ action_id ]
        print( '\tAction: %s ' % ( action['description'] ) )

def usage():
  print ''' ucd-compare_roles
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  [-u|--user username (do not supply when using a token) ]
  --password [password|token] - Supply password or token to connect with
   "<Role Name>" "<Role Name>" - 2 Roles to compare, quotes only required when Role Name contains spaces
'''

def __main__():

  global debug, user, password, base_url

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:u:p:v", ['help','server=', 'user=', 'password='])
  except getopt.GetoptError as err:
  # print help information and exit:
    print(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  output = None
  for o, a in opts:
    if o == '-v':
      debug = True
    elif o in ('-h', '--help'):
      usage()
      sys.exit()
    elif o in ( '-s', '--server'):
      base_url = a
    elif o in ( '-u', '--user'):
      user = a
    elif o in ( '-p', '--password'):
      password = a
    else:
      assert False, "unhandled option"
      usage()
      sys.exit()

  if not base_url or not password:
    print('Missing required arguments')
    usage()
    sys.exit()

  # define here if you want to do this static-like
  #role_name1 = 'Observer'
  #role_name2 = 'Stakeholder'
  # Pull the last two items off the arguments list
  role_name1, role_name2 = sys.argv[-2:]

  ucd = ucdclient( base_url, user, password , debug )

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
  #pprint( roles )

  # Get Action Mappings only, otherwise they are included when you get the role
  # '/security/role/<id>/actionMappings'

  # Build a simple Role dictionary, slighly different than the version that
  # comes from just pulling the role /security/role/<id> as the actions are a
  # dictionary instead of a list for easier referencing instead of searching
  # and make the simple set operations possible
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

  # Compare the roles
  if role_name1 in role_dict and role_name2 in role_dict:
    compare_roles( role_dict[ role_name1 ], role_dict[ role_name2 ] )
  else:
    print('Either %s or %s are not valid Roles' % (role_name1, role_name2) )

if __name__ == '__main__':
  __main__()
