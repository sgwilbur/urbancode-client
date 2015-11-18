#!/usr/bin/env python
'''
 Helper to experiment with importing and exporting to the UCR calendar.

 Example JSON for an event:

{u'dateCreated': 1434743552795,
  u'description': u'Annual Company Retreat',
  u'endDate': 1434870000000,
  u'id': u'84e8c088-2bf3-4a87-ac35-39f11f26be69',
  u'isOneDay': False,
  u'name': u'Company Retreat',
  u'releases': [],
  u'startDate': 1434610800000,
  u'type': {u'color': u'#e6e6fa',
            u'dateCreated': 1437061524476,
            u'description': u'',
            u'ghostedDate': 0,
            u'id': u'954dd2fe-5dc8-4d01-900e-04005a719142',
            u'name': u'Company Event',
            u'order': 0,
            u'version': 1},
  u'version': 1},

'''
import json
import re
import urllib
import time, datetime
import csv
import copy
from pprint import pprint

import sys
import getopt
sys.path.append('..')
from ucclient import ucclient

debug = 0
user = ''
password = ''
base_url = ''

# Define the columns required for reading and used for writing csv files
ucr_event_attributes = ['id','name', 'description', 'startDate', 'endDate', 'type', 'version', 'isOneDay', 'releases', 'dateCreated']

csv_delimiter = ','
csv_quote_char = '\''

'''
 Usage statement
'''
def usage():
  print ''' ucd-events_porter
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  -u|--user username
  -p|--password password - Supply password
  -m|--mode [import|export]
  -f|--file events.csv - path to file to read from in import mode, or write to in export mode
'''

'''
 Write an events object pulled from the /events/ uri, the only significant
 changes that will be made to the object to ease formatting:
 1. swapping out the embedded type object with just the type['name']
 2. Cutting off the ms from the startDate & endDate to make them valid epochs
'''
def write_csv( events, fname='events.csv' ):
  global csv_delimiter, csv_quote_char

  for event in events:
    # Java epochs time is in miliseconds so throw that part away
    start =  event['startDate'] #/ 1000
    end = event['endDate'] #/ 1000
    created = event['dateCreated'] #/ 1000
    # probably want to do this local time, not GMT/UTC ?
    c_start = time.gmtime( start )
    c_end = time.gmtime( end )
    #print( time.strftime('%Y-%m-%d %H:%M:%S'), c_start )
    #print( '%s %s-%s ( %s - %s )' % ( event['name'], start, end, c_start, c_end ) )

    # put a string format version for people to write?
    event['startDate'] = start
    event['endDate'] = end
    event['dateCreated'] = created

    # cleanup type to a simple string rather than embedded type def
    event['type'] = event['type']['name']

  with open(fname, 'wb') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=csv_delimiter, quotechar=csv_quote_char, quoting=csv.QUOTE_ALL)

    # write the header columns
    csv_writer.writerow( ucr_event_attributes )

    for event in events:
      row_values = []
      for attrib_name in ucr_event_attributes:
         row_values.append( event[ attrib_name ] )
      csv_writer.writerow( row_values )

'''
 Read in a csv file that *must* contain the expected column formats.
 requires the current event_types object to re-embed the eventType object
'''
def read_csv(event_types, fname='events.csv'):
  global csv_delimiter, csv_quote_char

  with open(fname, 'rb') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=csv_delimiter, quotechar=csv_quote_char)

    # Create and events array
    events = []

    # skip header row, we know what this is but just confirm they match
    header_row = csv_reader.next()
    if header_row != ucr_event_attributes:
      raise Exception( 'Header row does not match the expected colums of: \nactual %s \nexpecting %s' %( header_row, ucr_event_attributes ) )

    for row in csv_reader:
      event = {}
      # build the event object with the key and index
      for i in range(len( ucr_event_attributes )):
        # Only add non-empty values to the event object for update/creation
        if row[i]:
          event[ unicode( ucr_event_attributes[i] ) ] = unicode(row[i])

      # Cleanup the data and convert back to proper types from plain strings

      # cleanup type to a simple string rather than embedded type def
      event['type'] = filter( lambda e: e['name'] == event['type'], event_types )[0]

      event['startDate'] = int(event['startDate'])# * 1000
      event['endDate'] = int(event['endDate' ])# * 1000
      event['dateCreated'] = int(event['dateCreated'])# * 1000

      event['releases'] = eval( event['releases'] )
      event['isOneDay'] = eval( event['isOneDay'] )
      event['version']  = int(event['version'])

      events.append( event )

  return events

'''
 Simple main wrapper to call the ucclient and pull the events
'''
def __main__():

  global debug, user, password, base_url

  mode = ''
  fname = ''

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:u:p:m:f:v", ['help','server=', 'user=', 'password=', 'mode=', 'file='])
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
    elif o in ( '-m', '--mode' ):
      mode = a
    elif o in ( '-f', '--file' ):
      fname = a
    else:
      assert False, "unhandled option"
      usage()
      sys.exit()

  if not base_url or not password or not mode or not fname:
    print('Missing required arguments')
    usage()
    sys.exit()

  ucr = ucclient( base_url, user, password , 0 )

  if mode == 'export':
    # Pull the events and cleanup the data before writing it out
    events = ucr.get_json( '/events' )
    events_start = copy.deepcopy( events )
    #pprint( events_obj )

    write_csv( events_start, fname )

  elif mode == 'import':

    # Now lets' read it back out
    event_types = ucr.get_json( '/eventTypes' )

    events_readin = read_csv( event_types, fname=fname )

    for event in events_readin:
      # pprint( event )

      if 'id' in event:
        # looks like an existing event, try and update
        r = ucr.put( uri='/events/%s' % ( event['id'] ), data=json.dumps(event) )
        if r.status_code in [200, 201]:
          print( 'Successfully updated event: %s ' % ( r.json()['name'] ) )
        else:
          ucr.debug_response( r )
          print( 'Failed to update event: %s \nserver returned: %s' % ( event, r.text ) )
      else:
        r = ucr.post( uri='/events/', data=json.dumps(event) )
        if r.status_code  in [200, 201]:
          print( 'Sucessfully created new event: %s ' % ( r.json()['name'] ) )
        else:
          ucr.debug_response( r )
          print( 'Failed to submit event: %s \nserver returned: %s' % (event, r.text ) )

  # elif mode == 'test':
  #
  #   events_readin = read_csv( event_types, fname=fname )
  #
  #   ###
  #   ### Failing on dataCreated which is actually using the ms part of the epoch...
  #   ###
  #   if events_start == events_readin:
  #     print( 'yey!')
  #   else:
  #     print( 'boo, they ain\'t match')
  #     pprint( events_start[0] )
  #     pprint( events_readin[0] )

  else:
    print('Invalid mode: %s' % (mode) )
    usage()
    sys.exit()

if __name__ == '__main__':
  __main__()
