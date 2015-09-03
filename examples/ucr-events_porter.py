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
sys.path.append('..')
from ucclient import ucclient

# Define the columns required for reading and used for writing csv files
ucr_event_attributes = ['id','name', 'description', 'startDate', 'endDate', 'type', 'version', 'isOneDay', 'releases', 'dateCreated']

'''
 Write an events object pulled from the /events/ uri, the only significant
 changes that will be made to the object to ease formatting:
 1. swapping out the embedded type object with just the type['name']
 2. Cutting off the ms from the startDate & endDate to make them valid epochs
'''
def write_csv( events, fname='events.csv' ):

  for event in events:
    # Java epochs time is in miliseconds so throw that part away
    start =  event['startDate'] #/ 1000
    end = event['endDate'] #/ 1000
    created = event['dateCreated'] #/ 1000
    # probably want to do this local time, not GMT/UTC ?
    c_start = time.gmtime( start )
    c_end = time.gmtime( end )
    print( time.strftime('%Y-%m-%d %H:%M:%S'), c_start )
    print( '%s %s-%s ( %s - %s )' % ( event['name'], start, end, c_start, c_end ) )

    # put a string format version for people to write?
    event['startDate'] = start
    event['endDate'] = end
    event['dateCreated'] = created

    # cleanup type to a simple string rather than embedded type def
    event['type'] = event['type']['name']

    # Handle releases, this is an embedded array, do I need to convert it to something else ?


  with open(fname, 'wb') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='\\', quoting=csv.QUOTE_ALL)

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
  with open(fname, 'rb') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',', quotechar='\\')

    # Create and events array
    events = []

    # skip header row, we know what this is but just confirm they match
    if csv_reader.next() != ucr_event_attributes:
      raise Exception( 'Header row does not match the expected colums of: %s' %( ucr_event_attributes ) )

    for row in csv_reader:
      event = {}
      # build the event object with the key and index
      for i in range(len( ucr_event_attributes )):
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

  # hard coded
  user = 'admin'
  password = 'admin'
  base_url = 'https://172.16.62.130:8443'

  ucr = ucclient( base_url, user, password , 0 )

  # Pull the events and cleanup the data before writing it out
  r = ucr.get( '/events' )
  events = r.json()
  events_start = copy.deepcopy(events)
  #pprint( events_obj )

  write_csv( events )

  # Now lets' read it back out
  r = ucr.get( '/eventTypes' )
  event_types = r.json()
  events_readin = read_csv( event_types )
  #pprint( events_readin )

  ###
  ### Failing on dataCreated which is actually using the ms part of the epoch...
  ###
  if events_start == events_readin:
    print( 'yey!')
  else:
    print( 'boo, they ain\'t match')
    pprint( events_start[0] )
    pprint( events_readin[0] )

__main__()
