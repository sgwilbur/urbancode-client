#!/usr/bin/env python
'''
 Sample script to help produce a customizable version of the Release Pipeline view for custom reporting or visualizations.

 While this is a non-trivial excercise to do, seeing a complete working example like this should be enough to help you create your own variants of this in your language of choice. In addition this script will output a copy of the primary json objects in a pretty printed formate to help you identify how the data is being represented and include additional attributes in your reports as desired.

Example use:
./ucr-full_pipeline.py -s https://192.168.1.117 -u admin -p XXX

'''
from pprint import pprint

import pdb
import sys
import getopt
import json
import time


from ucclient import ucclient
from ucclient import utils
from urbancode_client.deploy import ucdclient
from urbancode_client.release import ucrclient

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

  ucr = ucrclient.ucrclient( base_url, user, password , debug )

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
  pdb.set_trace()

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
  # key by app id for later and store latest version information here!
  applications = {}
  for app in pipeline_latest_application_versions:
    if 'children' not in app:
      pass

    children = []
    for child in app['children']:
      children.append( {
        'id' : child['application']['id'],
        'name': child['application']['name'],
        'latestVersion': { 'id': child['id'], 'name': child['name'] },
      })
    applications[ app['application']['id'] ] = {
      'id': app['application']['id'],
      'name': app['application']['name'],
      'latestVersion': { 'id': app['id'], 'name': app['name'] },
      'children': children
     }

  #pprint( applications )

  # Get phaseModel name & environments in a useful format
  my_phases = []

  for phase in release_pipeline['phases']:
    # First build up the basic current phase information
    cur_phase = {
      'environments': {},
      'gates': [ gate['status']['name'] for gate in phase['phaseModel']['gates'] ],
      'id': phase['id'],
      'name': phase['phaseModel']['name'],
    }

    for env in phase['environments']:
      cur_phase['environments'][ env['id'] ] = {
        'applicationTargets': {},
        'id' : env['id'],
        'name': env['name'],
        'deployed': [],
        'deployments': {}
        }

      # Build a view of what is already deployed
      for app_id, app in pipeline_all_application_versions.items():
        if env['id'] in app.keys():
          cur_phase['environments'][ env['id'] ]['deployed'].append( {
            'id': app_id,
            'versionId': app[ env['id'] ]['id'],
            'version': app[ env['id'] ]['name'] } )

      # Bring in the deployments if they exist
      if env['id'] in pipeline_release_deployments:
        # Bring in current deployments for either last or next
        #   last - provides currently deployed
        #   next - provides scheduled to be deployed
        for key, deploy in pipeline_release_deployments[ env['id'] ].items() :
          # Pull the useful fields from this object
          cur_phase['environments'][ env['id'] ]['deployments'][ key ] = {
            'id' : deploy['id'],
            'status' : deploy['deploymentExecution']['status'],
            'execution_id' : deploy['deploymentExecution']['id'],
            'dateCreated' : deploy['dateCreated'],
            'scheduledDate': deploy['scheduledDate'],
            # Build a simple list of application/versions & component/versions
            # Need to handle Snapshots, Applications, and Component levels
            'versions': [ process_version(version) for version in deploy['versions']  ]
            }

      # Store the application environments, is this useful...
      for app_env in env['applicationTargets']:
        cur_phase['environments'][ env['id'] ]['applicationTargets'][ app_env['id'] ] = {
          'id' : app_env['id'],
          'name': app_env['name']
          }

    # Store in my custom phases array
    my_phases.append( cur_phase )

  ## At this point all the data I think we need is in release_pipeline and my_phases
  utils.write_pretty_json( 'my_phases.json', my_phases )
  # pprint( my_phases )

  ## Example output of the results that can be formatted or used as a base to tweaking
  ## what information you want to report on.
  ## This is already getting too complex to be useful, time to switch to a template...
  print( 'Release: %s \n  %s\n  %s' % ( release_pipeline['name'], utils.javats_tostr( release_pipeline['targetDate'] ), release_pipeline['description'] ) )
  print( '  Applications: %s ' % (','.join( applications )) )

  print( 'Phases:' )
  for phase in my_phases:
    print( '  %s(%s)  Requires[%s]' % ( phase['name'], phase['id'], ','.join( phase['gates'] ) ) )

    for env_id, env in phase['environments'].items():
      print( '%sEnvironments:' % ('\t' * 1) )
      print( '%s %s (%s):' % ('\t' * 1, env['name'], env['id']) )

      # Made up of the following application environments
      print( '%sApplication Targets:' % ('\t' * 2) )
      for target in env['applicationTargets'].values():
        print( '%s  %s (%s)' % ( '\t' * 3, target['name'], target['id'] ) )

      print( '%sDeployed: ' % ('\t' * 2) )
      for app in env['deployed']:
        print( '%s  %s - %s' % ( '\t' * 3, applications[ app['id'] ]['name'], app['version'] ) )

      # show next and last deployments
      print( '%sDeployments: ' % ('\t' * 2) )
      for key, deployment in env['deployments'].items():
        print( '%s%s: %s - %s' % ( '\t' * 3, key, utils.javats_tostr( deployment['scheduledDate'] ), deployment['status'] ) )
        print( '%sVersions Deployed: ' % ( '\t' * 4 ) )

        for version in deployment['versions']:
          print( '%s %s: %s v%s [%s]' % ( '\t' * 5, version['type'], version['name'], version['version'], ','.join( version['statuses']) ) )

          if version['type'] == 'SUITE':
            for app in version['applications']:
              comps = [ '%s: %s v%s [%s]' % ( comp['type'], comp['name'], comp['version'], ','.join(comp['statuses']) ) for comp in app['components'] ]
              print( '%s %s: %s v%s [%s]' % ( '\t' * 6, app['type'], app['name'], app['version'], ','.join(app['statuses']) ) )
              for comp in comps:
                print( '%s %s' % ('\t' * 7, comp) )
          else:
            comps = [ '%s: %s v%s [%s]' % ( comp['type'], comp['name'], comp['version'], ','.join(comp['statuses']) ) for comp in version['components'] ]
            for comp in comps:
              print( '%s %s' % ('\t' * 6,comp) )

if __name__ == '__main__':
  __main__()
