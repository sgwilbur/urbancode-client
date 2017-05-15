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

  application_name = 'NN-DHP'
  # used to search process names for sub-string match
  process_filter = 'DHP-IIB / DHP-IIB'

  # Get all applicationProcess

  applications_uri = '/rest/deploy/application'
  applications = ucd.get_json( uri=applications_uri )
  application_id = ''

  for app in applications:
    if app['name'] == application_name:
      application_id = app['id']
      break

  if application_id == '':
    print( 'Application with name [%s] not found' % ( application_name ) )
    pprint( applications )
    sys.exit(1)


  # Find processes for specific app_id
  app_processes_uri = '/rest/deploy/application/%s/processes/false?rowsPerPage=10&pageNumber=1&sortType=asc' % (application_id)
  processes = ucd.get_json( uri=app_processes_uri )

  # Inspect all the processes that get returned
  # pprint( processes )

  for process in processes:
    pprint( process )

  # Create a list of process ids of all the process names that contain the filter
  processes_to_delete = [ process['id'] for process in processes if process_filter in process['name'] ]

  print( 'Processes to be deleted: ')
  pprint( processes_to_delete )

  for process_id in processes_to_delete:
    delete_uri = '/rest/deploy/applicationProcess/%s' % ( process_id )
    r = ucd.delete( uri=delete_uri )
    pprint( r )


if __name__ == '__main__':
  __main__()
