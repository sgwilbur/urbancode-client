#!/usr/bin/env python

import json
import re
import sys

from ucclient import ucclient

def __main__():

  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://192.168.1.117'

  applications_uri = '/cli/deploy/application'
  ucd = ucclient( base_url, user, password , 0)

  '''
   Create a new Application
   http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.1/com.ibm.udeploy.api.doc/topics/rest_cli_application.html?lang=en
  '''
  app_name = 'Application'
  applications_uri = '/cli/application/create'
  print "Try and create %s " % ( app_name )
  new_app = {'name': app_name,'description':'','notificationSchemeId':'','enforceCompleteSnapshots':'false','teamMappings':[], }
  body = json.dumps( new_app )
  r = ucd.put(uri=applications_uri, data=body )
  print( "Create new application response: %s %s " % ( r.status_code, r.text ) )
  #ucd.debug_response( r )


  team_name = 'Team1'
  new_team_uri = '/cli/team/create?team=%s&description=%s' % ( team_name, 'description')

  r = ucd.put( uri=new_team_uri )
  print( "Create new team response: %s" % ( r.text ) )

  '''
   Add Group to team
   /cli/teamsecurity/groups?group=<name>&team=<name>&type=<name of type>
   http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.1/com.ibm.udeploy.api.doc/topics/rest_cli_teamsecurity_groups_put.html
  '''
  group_name = 'Team1Group'
  role_name = 'ConfigEngineer'

  add_group_to_team_uri = '/cli/teamsecurity/groups?group=%s&team=%s&type=%s' % ( group_name, team_name, role_name )
  r = ucd.put( uri=add_group_to_team_uri )


  '''
  PUT https://{hostname}:{port}
  /cli/application/teams?{parameters}
  '''

  type_name = 'Standard Application'
  add_team_to_app = '/cli/application/teams?application=%s&team=%s&type=%s' % ( app_name, team_name, type_name )

  r = ucd.put( uri=add_team_to_app )
  print( "Add Team to Application response: %s %s" % ( r.status_code, r.text ) )

  '''
  Add a team to an Environment

  PUT https://{hostname}:{port}
  /cli/environment/teams?{parameters}

  '''
  env_name = 'DEV'

  add_team_to_env_uri = '/cli/environment/teams?application=%s&environment=%s&team=%s&type=' % ( app_name, env_name, team_name )
  r = ucd.put( uri=add_team_to_env_uri )
  print( "Add Team to Environment response: %s %s" % ( r.status_code, r.text ) )

  '''
   Add Team to Resource

   PUT https://{hostname}:{port}
  /cli/resource/teams?{parameters}
  '''

  resource_path = '/Application1/DEV'
  team_id = '9e9c7267-4e08-455c-b8a7-4b64038553b2'

  add_team_to_resource_uri = '/cli/resource/teams?resource=%s&team=%s&type=' % ( resource_path, team_id )
  r = ucd.put( uri=add_team_to_resource_uri )
  print( "Add Team to Resource response: %s %s" % ( r.status_code, r.text ) )

__main__()
