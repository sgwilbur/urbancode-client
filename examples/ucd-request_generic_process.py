#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucd-example_template.py --help

Example use:

./ucd-example_template.py -s https://192.168.1.117 -u user -p XXX arg1 arg2 ... argN

'''
import json
import sys
import getopt
from pprint import pprint
import time

from urbancode_client.deploy import ucdclient

debug = 0
user = 'PasswordIsAuthToken'
password = ''
base_url = ''

def usage():
  print ''' ucd-example_template
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  [-u|--user username (do not supply when using a token) ]
  --password [password|token] - Supply password or token to connect with
  <Insert specific parameters for this example >
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

  # Peel and specfic arguments off the end for this call
  arg1, arg2 = sys.argv[-2:]

  ucd = ucdclient.ucdclient( base_url, user, password , debug )

  # Get list of GP
  # https://localhost:9443/rest/process/request?rowsPerPage=10&pageNumber=1&orderField=submittedTime&sortType=desc&filterFields=processPath&filterValue_processPath=processes%2Ffff4c56c-96a6-4fd9-955b-d294599f4de8&filterType_processPath=eq&filterClass_processPath=String&outputType=BASIC

  # View a specific GP
  # https://localhost:9443/#process/fff4c56c-96a6-4fd9-955b-d294599f4de8/10

  # Get list of Resources
  #https://localhost:9443/rest/resource/resource/tree?rowsPerPage=10000&pageNumber=1&orderField=name&sortType=asc&UCD_SESSION_KEY=e85e9f7d-cbe5-41ab-a55a-99ff39df80d1

  # Request a generic process
  # POST https://localhost:9443/rest/process/request
  # {"resource":"55afd7b9-406d-4a56-ab73-6d3578807fd8","properties":{"resource":"55afd7b9-406d-4a56-ab73-6d3578807fd8"},"processId":"fff4c56c-96a6-4fd9-955b-d294599f4de8"}

  # Response:
  # {"id":"7d792a4e-8845-412d-9d6e-e052baabdc8c","submittedTime":1482419504439,"userName":"admin","processPath":"processes\/fff4c56c-96a6-4fd9-955b-d294599f4de8","processVersion":10}

  # Check Status
  # GET https://localhost:9443/rest/process/request/7d792a4e-8845-412d-9d6e-e052baabdc8c


  # Generic Process Information
  generic_process_id    = 'fff4c56c-96a6-4fd9-955b-d294599f4de8'
  resource_id           = '55afd7b9-406d-4a56-ab73-6d3578807fd8'

  request_body = {
    'processId' : generic_process_id,
    'resource': resource_id,
    'properties' : { 'resource': resource_id }
  }
  print 'Requesting generic process %s run on resource %s' %( generic_process_id, resource_id )
  response_json = ucd.post_json( uri='/rest/process/request', data=json.dumps( request_body ) )

  pprint( response_json )
  request_id = response_json['id']

  waiting_for_request_to_complete = True
  max_count = 5

  while( waiting_for_request_to_complete and max_count > 0 ):
    print 'Loop [%d][%i]' % (waiting_for_request_to_complete, max_count)

    response_json = ucd.get_json( uri='/rest/process/request/%s' % (request_id) )
    #pprint( response_json )

    if 'state' in response_json:
      current_state = response_json['state']
      print 'Running process [%s]' % (current_state)

      print ''

      if current_state == 'CLOSED':
          waiting_for_request_to_complete = False
          current_result = response_json['result']
          print 'Request complete state [%s] results [%s]' % (current_state,current_result)
          if current_result == 'FAULTED':
            pprint( response_json )

    time.sleep(2)
    max_count = max_count - 1


if __name__ == '__main__':
  __main__()
