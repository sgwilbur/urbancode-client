#!/usr/bin/env python
'''
 Sample script to help produce a customizable version of the Release Pipeline view for custom reporting or visualizations.

 While this is a non-trivial excercise to do, seeing a complete working example like this should be enough to help you create your own variants of this in your language of choice. In addition this script will output a copy of the primary json objects in a pretty printed formate to help you identify how the data is being represented and include additional attributes in your reports as desired.

Example use:
./ucr-full_pipeline.py -s https://192.168.1.117 -u admin -p XXX

'''
from pprint import pprint

import sys
import getopt
import json
import time

sys.path.append('..')
from ucclient import ucclient
from ucclient import utils
from ucclient.ucd import ucdclient
from ucclient.release import ucrclient

debug = 0
user = ''
password = ''
base_url = ''
release_name = ''

def usage():
  print ''' ucr-full_pipeline
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  -u|--user username
  -p|--password password
  -r|--release Release Name - Release to get information about
'''

'''
 Helper method to flatten a version or recurse if it is a suite or application
'''
def process_version( version ):

  cur_version = {
    'id': version['id'],
    'name': version['application']['name'],
    'version': version['name'],
    'statuses': [ status['status']['name'] for status in version['versionStatuses'] ],
    'type': version['application']['level'],
    'type_id':  version['application']['id']
    }

  children = [ process_version( child ) for child in version['children'] ]

  if( cur_version['type'] == 'SUITE' ):
    # means the children and Applications
    cur_version['applications'] = children
  elif ( cur_version['type'] == 'APPLICATION' ):
    # meand the children are Components
    cur_version['components'] = children
  elif( cur_version['type'] == 'COMPONENT' ):
    # Should be base of recursion
    pass
  else:
    raise Exception('Processing versions failed on an unknown type %s' % (version_type) )

  return cur_version

'''
 Main logic that does all the work
'''
def __main__():

  global debug, user, password, base_url, release_name
  release_id = ''

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:u:p:r:v", ['help','server=', 'user=', 'password=', 'release='])
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
    elif o in ( '-r', '--release'):
      release_name = a
    else:
      assert False, "unhandled option"
      usage()
      sys.exit()

  if not base_url or not password or not release_name:
    print('Missing required arguments')
    usage()
    sys.exit()

  ucr = ucrclient( base_url, user, password , debug )

  # Given a specific release by name, first translate that to the id

  # list of available releases
  releases = ucr.get_json( '/releases/?format=name&name=*' )

  for release in releases:
    if release_name == release['name']:
      release_id = release['id']
      break

  if not release_id:
    print( ' Available releases: [%s]' % ( ', '.join([ release['name'] for release in releases  ]) ) )
    raise Exception( 'Release %s not found' % ( release_name ) )

  ## First get the 4 queries the web client uses to build the pipeline view

  # 1. Get specific Release
  #/releases/90e0edce-092d-48bc-8313-5ca81083e7e7?format=pipeline
  release_pipeline = ucr.get_json( '/releases/%s?format=pipeline' % ( release_id ) )

  # 2. Get deployments for this Release
  # /pipelineView/90e0edce-092d-48bc-8313-5ca81083e7e7/releaseDeployments
  pipeline_release_deployments = ucr.get_json( '/pipelineView/%s/releaseDeployments' % ( release_id ) )

  # 3. Get Applications for rhis Releas
  # /pipelineView/90e0edce-092d-48bc-8313-5ca81083e7e7/allApplicationVersions
  pipeline_all_application_versions = ucr.get_json( '/pipelineView/%s/allApplicationVersions' % ( release_id ) )

  # 4. Get Latest Application Versions for this Release
  # http://ucr02/pipelineView/<release_id>/latestApplicationVersions
  pipeline_latest_application_versions = ucr.get_json( '/pipelineView/%s/latestApplicationVersions' % ( release_id ) )

  # Write out the starter json as refernce to the weeds we are hacking through
  utils.write_pretty_json( 'release_pipeline.json', release_pipeline )
  utils.write_pretty_json( 'pipeline_release_deployments.json', pipeline_release_deployments )
  utils.write_pretty_json( 'pipeline_all_application_versions.json', pipeline_all_application_versions )
  utils.write_pretty_json( 'pipeline_latest_application_versions.json', pipeline_latest_application_versions )


  ## Start disecting this information into a more useful format

  # Get participating applications
  applications = [ application['name'] for application in release_pipeline['applications'] ]
  # Get phaseModel name & environments in a useful format
  my_phases = []

  for phase in release_pipeline['phases']:
    cur_phase = {}

    # First get the name and gates for the current phase
    cur_phase['name'] = phase['phaseModel']['name']
    if phase['phaseModel']['gates']:
      cur_phase['gates'] = [ gate['status']['name'] for gate in phase['phaseModel']['gates'] ]
    else:
      cur_phase['gates'] = []

    # Need more digging to find environments, as they are not referenced by lifecyle phase, but by applicationTarget id
    # creating a dict to key into by id to simplify any access via what is used everywhere else...
    cur_phase['environments'] = {} # { 'id' : env['name'] }

    for env in phase['environments']:
      cur_phase['env_id'] = env['id']
      for app_env in env['applicationTargets']:
        cur_phase['environments'][ app_env['id'] ] = { 'id' : app_env['id'], 'name': app_env['name'], 'deployments': {} }

        # Bring in the deployments if they exist
        if env['id'] in pipeline_release_deployments:
          ## TODO: pull out the useful deployment info next/last, add version info here
          cur_phase['env_id'] = env['id']
          # for either last or next
          #   last - provides currently deployed
          #   next - provides scheduled to be deployed
          for key, deploy in pipeline_release_deployments[ env['id'] ].items() :

            # Pull the useful fields from this object
            current_deployment = {
              'id' : deploy['id'],
              'status' : deploy['deploymentExecution']['status'],
              'execution_id' : deploy['deploymentExecution']['id'],
              'dateCreated' : deploy['dateCreated'],
              'scheduledDate': deploy['scheduledDate'],
              # Build a simple list of application/versions & component/versions
              # Need to handle Snapshots, Applications, and Component levels
              'versions': [ process_version(version) for version in deploy['versions']  ]
              }

            cur_phase['environments'][ app_env['id'] ]['deployments'][ key ] = current_deployment

    # Store in my custom phases array
    my_phases.append( cur_phase )


  ## At this point all the data I think we need is in release_pipeline and my_phases
  utils.write_pretty_json( 'my_phases.json', my_phases )
  # pprint( my_phases )

  #
  ## Example output of the results that can be formatted or used as a base to tweaking
  ## what information you want to report on.
  #
  print( ' Release: %s \n%s\n%s' % ( release_pipeline['name'], utils.javats_tostr( release_pipeline['targetDate'] ), release_pipeline['description'] ) )
  print( ' Applications: %s ' % (','.join( applications )) )

  for phase in my_phases:
    print( '\t%s(%s)  Requires[%s]' % ( phase['name'], phase['env_id'], ','.join( phase['gates'] ) ) )
    #pprint( phase['environments'] )
    for env in phase['environments'].values():
      print( '\t\t%s(%s)' % ( env['name'], env['id'] ) )
      for key, deployment in env['deployments'].items():
        print( '\t\t %s: %s - %s' % ( key, utils.javats_tostr( deployment['scheduledDate'] ), deployment['status'] ) )
        print( '\t\t\tversions: ')
        for version in deployment['versions']:
          print( '\t\t\t %s: %s v%s [%s]' % ( version['type'], version['name'], version['version'], ','.join( version['statuses']) ) )

          if version['type'] == 'SUITE':
            for app in version['applications']:
              comps = [ '%s: %s v%s [%s]' % ( comp['type'], comp['name'], comp['version'], ','.join(comp['statuses']) ) for comp in app['components'] ]
              print( '\t\t\t\t %s: %s v%s [%s]' % ( app['type'], app['name'], app['version'], ','.join(app['statuses']) ) )
              for comp in comps:
                print( '\t\t\t\t\t %s' % comp )
          else:
            comps = [ '%s: %s v%s [%s]' % ( comp['type'], comp['name'], comp['version'], ','.join(comp['statuses']) ) for comp in version['components'] ]
            for comp in comps:
              print( '\t\t\t\t %s' % comp )

if __name__ == '__main__':
  __main__()
