#!/usr/bin/env python
from pprint import pprint
'''

 Working on testing

'''
# getGenericProcessResult

import json
import re
import sys

from ucclient import ucclient


def __main__():

  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://192.168.1.117/ucd01'

  applications_uri = '/cli/deploy/application'
  ucd = ucclient( base_url, user, password , 0)

  request_uri = '/rest/process/request'
  # process_body = { 'id': '58bf971b-1c0d-4d44-9f34-7617e9026278', 'processPath': 'processes/58bf971b-1c0d-4d44-9f34-7617e9026278', 'processVersion': '2', 'resource': '/Application1/DEV/local' }
  process_body = { 'processId': '58bf971b-1c0d-4d44-9f34-7617e9026278', 'processVersion': '3', 'resource': '/Application1/DEV/local', 'properties': [ { 'prop1' : 'prop1Value'} ], 'prop1' : 'prop1Value' }
  #process_body = {}
  body = json.dumps( process_body )
  #print( 'Body: %s ' % ( body ) )
  #r = ucd.post( uri=request_uri, data=body )
  #r = ucd.post( uri=request_uri, data=body )
  #ucd.debug_response( r )

  # /rest/deploy/applicationProcessRequest/ef49f792-6eaa-4b40-9590-30853948f382
  # /rest/approval/approval/da94fcea-d39e-44fd-a010-0f34ec65f3d5/withTrace

  process_request_id = '3a4ac63e-7823-469a-a9be-5901e3e523ca'
  process_request_uri = '/rest/process/request/%s/trace' % ( process_request_id )

  process_request_id = 'ef49f792-6eaa-4b40-9590-30853948f382'
  process_request_uri = '/rest/deploy/applicationProcessRequest/%s' % ( process_request_id )

  r = ucd.get( uri=process_request_uri)

  if r.status_code != 200:
    ucd.debug_response( r )
    raise Exception( 'Failed to get Process Request Information')

  process_request = r.json()
  pprint( process_request )
  #print( "Process id %s name %s current state %s result %s" % (process_request['id'], process_request['name'], process_request['state'], process_request['result']) )

__main__()
