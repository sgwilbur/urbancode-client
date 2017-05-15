#!/usr/bin/env python
'''

Script to trigger a scheduled deployment to run every 15m for any component versions that are passing the required status gates.

'''
import json
from pprint import pprint
import getopt

import os, sys, inspect, time
import random
from urbancode_client.deploy import ucdclient


debug = 0
user = 'swilbur2@us.ibm.com'
password = ''
base_url = ''

def usage():
  print ''' ucd-schedule_deployment
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  [-u|--user username (do not supply when using a token) ]
  --password [password|token] - Supply password or token to connect with
  <filename of json request>
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

  ucd = ucdclient.ucdclient( base_url, user, password , debug )

  uri = '/rest/deploy/component/443318b8-d98e-42e6-8a68-ab4cc9f1c4ca/runProcess'

  print 'NN-DHP: Calling nndhp_scripts::iib_setup on SDT-TEST0'
  request_body = {
    "environmentId":"16cc9353-967f-4406-8ba9-d1ea94e86591",
    "resourceId":"6378aa93-4428-46c3-a9c2-b3fdb6169307",
    "componentProcessId":
    "7da51aab-6263-4eed-b0cb-8cfea993adf7",
    "properties":{}
    }

  # print 'NN-DHP: Calling nndhp_scripts::test_mqsistart on DEV1'
  # request_body = {
  #   "environmentId":"b0813fcd-86ef-4848-b5e6-efc91e1d4fe2",
  #   "resourceId":"0765dfbe-89f4-4f19-a37e-eeb14a045f2f",
  #   "componentProcessId":"63f6fc22-a3b3-48c5-845f-dde04cb3444a",
  #   "properties":{}
  # }


  request_id = ucd.put_json( uri=uri, data=json.dumps( request_body ) )
  print request_id


if __name__ == '__main__':
  __main__()
