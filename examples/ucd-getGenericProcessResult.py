#!/usr/bin/env python
from pprint import pprint
'''

 Working on testing

'''
# getGenericProcessResult

import json
import re
from ucclient import ucclient


def __main__():

  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://172.16.62.138'

  applications_uri = '/cli/deploy/application'
  ucd = ucclient( base_url, user, password , 0)

  request_uri = '/rest/process/request'
  # process_body = { 'id': '58bf971b-1c0d-4d44-9f34-7617e9026278', 'processPath': 'processes/58bf971b-1c0d-4d44-9f34-7617e9026278', 'processVersion': '2', 'resource': '/Application1/DEV/local' }
  process_body = { 'processId': '58bf971b-1c0d-4d44-9f34-7617e9026278', 'processVersion': '3', 'resource': '/Application1/DEV/local', 'properties': [ { 'prop1' : 'prop1Value'} ], 'prop1' : 'prop1Value' }
  #process_body = {}
  body = json.dumps( process_body )
  print( 'Body: %s ' % ( body ) )
  #r = ucd.post( uri=request_uri, data=body )
  #r = ucd.post( uri=request_uri, data=body )
  #ucd.debug_response( r )

  process_request_id = '3a4ac63e-7823-469a-a9be-5901e3e523ca'
  process_request_uri = '/rest/process/request/%s/trace' % ( process_request_id )
  r = ucd.get( uri=process_request_uri)

  if r.status_code != 200:
    ucd.debug_response( r )
    raise Exception( 'Failed to get Process Request Information')

  process_request = r.json()
  #pprint( process_request )
  print( "Process id %s name %s current state %s result %s" % (process_request['id'], process_request['name'], process_request['state'], process_request['result']) )

__main__()
