#!/usr/bin/env python
import json
from pprint import pprint
import time, datetime

import sys
import optparse
sys.path.append('../..')
from ucclient import ucclient
from ucclient import utils
from ucclient.ucd import ucdclient
from ucclient.release import ucrclient
from flask import Flask
from flask import render_template

from werkzeug.contrib.cache import SimpleCache

debug = 0
user = 'admin'
password = 'admin'
base_url = 'http://192.168.1.121'


'''
 Takes a flask.Flask instance and runs it. Parses command-line flags to configure the app.
  Flask snippet: http://flask.pocoo.org/snippets/133/
'''
def flaskrun(app, default_host="127.0.0.1", default_port="5000"):
    """
    """

    # Set up the command-line options
    parser = optparse.OptionParser()
    parser.add_option("-H", "--host",
                      help="Hostname of the Flask app " + \
                           "[default %s]" % default_host,
                      default=default_host)
    parser.add_option("-P", "--port",
                      help="Port for the Flask app " + \
                           "[default %s]" % default_port,
                      default=default_port)

    # Two options useful for debugging purposes, but
    # a bit dangerous so not exposed in the help message.
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help=optparse.SUPPRESS_HELP)
    parser.add_option("-p", "--profile",
                      action="store_true", dest="profile",
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()

    # If the user selects the profiling option, then we need
    # to do a little extra setup
    if options.profile:
        from werkzeug.contrib.profiler import ProfilerMiddleware

        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                       restrictions=[30])
        options.debug = True

    app.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )

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
 Setup Application and routes
'''
app = Flask(__name__)
cache = SimpleCache()
cache_timeout = 5 * 60
ucr = ucrclient( base_url, user, password , debug )

'''
 Add some variables that can be used in templates
'''
@app.context_processor
def inject_config():
    return dict(user=user, base_url=base_url)

@app.template_filter('timestamptostr')
def tstostr_filter(s):
  # Need to return '' value when this is undefined as the util function is not tolerant of empty values
  return utils.javats_tostr( s ) if s else ''

@app.route("/")
def index():
  return render_template( 'index.j2' )

@app.route('/pipeline')
def get_releases():
  releases = cache.get('releases')
  if releases is None:
    print( 'Cache miss!' )
    releases = ucr.get_releases()
    cache.set('releases', releases, timeout=cache_timeout)
  else:
    print('Cache hit!')
  return render_template('pipeline_release_select.j2', title="Select a Release", releases=releases)

@app.route('/pipeline/<release_id>')
def get_pipeline( release_id ):

  release_pipeline_key = '%s-release_pipeline' % (release_id)
  release_pipeline = cache.get( release_pipeline_key )
  if release_pipeline is None:
    release_pipeline = ucr.get_json( '/releases/%s?format=pipeline' % ( release_id ) )
    cache.set( release_pipeline_key, release_pipeline, timeout=cache_timeout)

  pipeline_release_deployments_key = '%s-pipeline_release_deployments' % (release_id)
  pipeline_release_deployments = cache.get( pipeline_release_deployments_key )
  if pipeline_release_deployments is None:
    pipeline_release_deployments = ucr.get_json( '/pipelineView/%s/releaseDeployments' % ( release_id ) )
    cache.set( pipeline_release_deployments_key, pipeline_release_deployments, timeout=cache_timeout)

  pipeline_all_application_versions_key = '%s-pipeline_all_application_versions'
  pipeline_all_application_versions = cache.get( pipeline_all_application_versions_key )
  if pipeline_all_application_versions is None:
    pipeline_all_application_versions = ucr.get_json( '/pipelineView/%s/allApplicationVersions' % ( release_id ) )
    cache.set( pipeline_all_application_versions_key, pipeline_all_application_versions, timeout=cache_timeout)

  pipeline_latest_application_versions_key = '%s-pipeline_latest_application_versions' % (release_id)
  pipeline_latest_application_versions = cache.get( pipeline_latest_application_versions_key )
  if pipeline_latest_application_versions is None:
    pipeline_latest_application_versions = ucr.get_json( '/pipelineView/%s/latestApplicationVersions' % ( release_id ) )
    cache.set( pipeline_latest_application_versions_key, pipeline_latest_application_versions, timeout=cache_timeout)

  applications = cache.get( 'applications' )
  if applications is None:
    applications = {}
    for app in pipeline_latest_application_versions:
      children = []
      if 'children' in app:
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
    cache.set('applications', applications, timeout=cache_timeout)

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

  return render_template( 'pipeline.j2',
    release_id=release_id,
    release_pipeline=release_pipeline,
    pipeline_release_deployments=pipeline_release_deployments,
    pipeline_all_application_versions=pipeline_all_application_versions,
    pipeline_latest_application_versions=pipeline_latest_application_versions,
    applications=applications,
    my_phases=my_phases
    )

if __name__ == "__main__":
    flaskrun(app)
