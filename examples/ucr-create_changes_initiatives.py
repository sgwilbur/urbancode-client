#!/usr/bin/env python
'''
 Example of
  Check the usage statement below or run ./ucr-example_template.py --help

Example use:

./ucr-example_template.py -s https://192.168.1.117 -u admin -p XXX arg1 arg2 ... argN

'''
import json
from pprint import pprint

import sys
import getopt
import random
sys.path.append('..')
from ucclient import ucclient
from ucclient.ucd import ucdclient
from ucclient.release import ucrclient

debug = 0
user = ''
password = ''
base_url = ''

def usage():
  print ''' ucr-example_template
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  -u|--user username
  -p|--password password

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

  max_initiatives = 100
  max_changes_per_initiatve = 50

  ucr = ucrclient( base_url, user, password , debug )

  change_types = ucr.get_change_types()
  #print "Change Types: "
  #pprint( change_types )

  change_statuses = ucr.get_change_statuses()
  #print "Change statuses: "
  #pprint( change_statuses )

  applications = ucr.get_applications()
  #print "Applications(%d): " % ( len(applications) )
  #pprint( applications )

  releases = ucr.get_releases_editable()
  #print "Releases editable(%d)):" % ( len(releases) )
  #pprint( releases )

  initiatives = ucr.get_initiatives()
  #print "Initiatives: "
  #pprint( initiatives )

  changes = ucr.get_changes()
  #print "Changes(%d): " % ( len(changes) )
  #pprint( changes )

  print "Deleting all the existing Changes"
  for change in changes:
    #pprint( change )
    ucr.delete_change( change['id'] )
    print '.',

  print "Deleting all the existing Initiatives"
  for initiative in initiatives:
    #pprint( initiative )
    ucr.delete_initiative( initiative['id'] )
    print '.',

  # get releases
  # get applications per release
  # end result is a list of releases with an array of apps

  # Get a dictionary of words
  word_file = "/usr/share/dict/words"
  WORDS = open(word_file).read().splitlines()

  for i in range( max_initiatives ):

    word_file = "/usr/share/dict/words"
    initiative = ucr.create_initative( name='project%3d - %s' % (i, random.choice(WORDS) ) )
    num_changes = random.randint( 0, max_changes_per_initiatve )

    # Pick a release to file them against
    releaseId = releases[ random.randint(0, len(releases) - 1) ]['id']
    release = ucr.get_release( releaseId )
    apps = [ app['id'] for app in release['applications'] ]

    print "Creating %d changes for this initiative %s against release %s" % ( num_changes, initiative['name'], release['name'] )

    for j in range( num_changes ):
     # generate some of this data
      name = "Test Change %s" % ( random.choice(WORDS) )
      description = "Description"
      severity = "S1"

      applicationId = apps[ random.randint( 0, len(apps) - 1 ) ]
      initiativeId = initiative['id']
      releaseId = release['id']
      status = random.choice( change_statuses.keys() )
      change_type = change_types[ random.randint( 0, len(change_types) - 1 ) ]
      # This is not required, but I think should be the behavior
      typeId = change_type['id']

      change =  ucr.create_change( typeId=typeId, name=name, status=status, severity=severity, releaseId=releaseId, applicationId=applicationId, initiativeId=initiativeId, description=description, change_type=change_type)



if __name__ == '__main__':
  __main__()
