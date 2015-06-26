#!/usr/bin/env python
#import requests
# quiet warnings for self-signed certificates
#requests.packages.urllib3.disable_warnings()

import json
import re
from ucclient import ucclient


def __main__():

  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://192.168.1.117'

  applications_uri = '/rest/deploy/application'
  ucd = ucclient( base_url, user, password )

  # get the existing applications
  response = ucd.get( uri=applications_uri )
  print( "Get existing applications: %s" % ( response.json() ) )

  '''
   Create a new Application
   http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.1/com.ibm.udeploy.api.doc/topics/rest_cli_application.html?lang=en

  '''
  app_name = 'Application2'
  print "Try and create %s " % ( app_name )
  new_app = {'name': app_name,'description':'','notificationSchemeId':'','enforceCompleteSnapshots':'false','teamMappings':[], }
  body = json.dumps( new_app )
  r = ucd.put(uri=applications_uri, data=body )
  print( "Create new application response: %s " % ( r.text ) )
  ucd.debug_reponse( r )

  '''
   Get Application Properties
   http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.1/com.ibm.udeploy.api.doc/topics/rest_cli_application_getproperties_get.html?lang=en
   example:
   GET /cli/application/getProperties?application=JPetStore
  '''
  print "Get Application properties for %s " % (app_name)
  property_get_uri = '/cli/application/getProperties?application=%s' % ( app_name )
  r = ucd.get( uri=property_get_uri )
  # 200 ok created
  # 400 if app already exists
  ucd.debug_reponse( r )

  '''
   Set a property
   http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.1/com.ibm.udeploy.api.doc/topics/rest_cli_application_propvalue_put.html?lang=en
   example:
   PUT /cli/application/propValue?application=JPetStore&name=Prop4&value=value4
  '''
  prop_name = 'testing.property1'
  prop_value = 'test value'
  prop_is_secure = 'false'
  print "Set property %s to value %s on application %s" % ( prop_name, prop_value, app_name )
  property_set_uri = '/cli/application/propValue?application=%s&name=%s&value=%s&isSecure=%s' % ( app_name, prop_name, prop_value, prop_is_secure )
  r = ucd.put( uri=property_set_uri )
  # 200 ok on create
  # 200 on update if already exists
  ucd.debug_reponse( r )

  '''
   Get a specific property value
http://www-01.ibm.com/support/knowledgecenter/SS4GSP_6.1.1/com.ibm.udeploy.api.doc/topics/rest_cli_application_getproperty_get.html?lang=en
   GET /cli/application/getProperty?application=JPetStore&name=Prop4

  '''
  print "Get property %s value on application %s " % ( prop_name, app_name )
  property_get_uri = '/cli/application/getProperty?application=%s&name=%s' % ( app_name, prop_name )
  r = ucd.get( uri=property_get_uri )
  ucd.debug_reponse( r )


__main__()
