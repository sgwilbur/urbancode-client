#!/usr/bin/env python
'''
Helper library to extract the properties from UCD.

v0.7
sgwilbur
'''
import json
from pprint import pprint

import os
import sys
import getopt

from urbancode_client.deploy import ucdclient

debug = 0
user = 'PasswordIsAuthToken'
password = ''
base_url = ''
verbose = 1

def usage():
  print ''' ucd-example_template
  [-h|--help] - Optional, show usage
  [-v|--verbose] - Optional, turn on debugging
  -s|--server http[s]://server[:port] - Set server url
  [-u|--user username (do not supply when using a token) ]
  --password [password|token] - Supply password or token to connect with
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

  props = {}


  # Loop over all apps
  app_rest_uri    = '/rest/deploy/application'
  applications = ucd.get_json( app_rest_uri )

  # Filter down to a specific app that I want by name, could also do something like
  # this with tags if desired...
  #filter_app_name    = 'UCD App'
  #applications = [ app for app in applications if app['name'] == filter_app_name ]

  for app in applications:
        cur_app = {}

        app_name = app['name']
        app_id = app['id']

        props[ app_name ] = { 'name': app_name, 'id': app_id }

        # Get app properties
        app_properties = ucd.get_json( '/cli/application/getProperties?application=' + app_id )
        app['properties'] = app_properties

        # Get all components for the current application, but just take what I want from the component obj via a dict comprehension
        components = ucd.get_json( '/rest/deploy/application' + '/' + app_id + '/components' )
        components = [ { 'name': component['name'], 'id' : component['id'] } for component in components ]

        for comp in components:
            current_component = ucd.get_json( '/cli/component/getProperties?component=' + comp['id'] )
            comp['properties'] = current_component

            # Get processes and iterate
            comp_processes = ucd.get_json( '/rest/deploy/component/' + comp['id'] + '/processes/false' )
            comp_processes = [ { 'name': process['name'], 'id' : process['id'] } for process in comp_processes ]

            for comp_process in comp_processes:
                #comp_processes = ucd.get_json( '/cli/componentProcess/info?component=' + comp['id'] +'&componentProcess=' + comp_process['name'] )
                # TODO: Get properties for the current process
                comp_process['properties'] = []

            comp['processes'] = comp_processes

        app['components'] = components

        # Loop over each process for the current application
        # TODO: not sure how to get these props?
        processes = ucd.get_json('/rest/deploy/application' + '/' + app_id + '/processes/' + 'false' )
        for process in processes:
            current_processes = ucd.get_json( '/rest/deploy/applicationProcess/' + process['id'] + '/' + str(process['version']) )
            process['properties'] = current_processes

        app['processes'] = []

        # Loop over each environment for the current application, simplify output
        environments = ucd.get_json( '/rest/deploy/application' + '/' + app_id + '/environments/' + 'false' )
        environments = [ { 'name': environment['name'], 'id' : environment['id'] } for environment in environments ]

        for env in environments:
            current_env = ucd.get_json('/rest/deploy/environment/' + env['id'] )

            # Get environment properties
            env_properties = ucd.get_json( '/cli/environment/getProperties?environment=' + env['id'] )
            env['properties'] =  env_properties

            # Get environment component properties, requires component list to check with
            env_comp_properties = {}
            for component in components:
                cur_env_comp_properties = ucd.get_json( '/cli/environment/componentProperties?environment=' + env['id'] + '&component=' + component['id'] )
                env_comp_properties[ component['name'] ] = cur_env_comp_properties

            env['compProperties'] = env_comp_properties

            # Get all resources for current environment
            base_resources = ucd.get_json( '/cli/environment/getBaseResources?environment=' + env['id'] )
            base_resources = [ { 'id': resource['id'], 'name': resource['name']} for resource in base_resources ]
            # print( base_resources )

            for resource in base_resources:
                resource_properties = ucd.get_json( '/cli/resource/getProperties?resource=' + resource['id'] )
                resource['properties'] = resource_properties

            env['resources'] = base_resources

        app['environments'] = environments


  # For reference you can inspect the dict blob I have assembled
  #    pprint( applications )
  #    pprint( applications, depth=3 )

  with open('properties.html', 'w+') as outfile:
        outfile.write("<html><head></head><body>")

        for app in applications:

            #pprint( app )

            outfile.write("<hr/>")
            outfile.write( "<h3>"+ app['name'] +" (" + app['id'] +")</h3>" )

            outfile.write( "<table border='1'>" )
            outfile.write("<tr>")
            outfile.write("<td> Scope </td>")
            outfile.write("<td> Location </td>")
            outfile.write("<td> Name </td>")
            outfile.write("<td> Value </td>")
            outfile.write("<td> Description </td>")
            outfile.write("</tr>")

            for app_properties in app['properties']:
                outfile.write("<tr>")
                outfile.write("<td> application </td>")
                outfile.write("<td>" + app['name'] +"  </td>")
                outfile.write("<td>" + app_properties['name'] + "</td>")
                outfile.write("<td>" + app_properties['value'] +"</td>")
                outfile.write("<td>" + app_properties['description'] +"</td>")
                outfile.write("</tr>")

            for component in app['components']:
                for component_properties in component['properties']:
                    outfile.write("<td> component </td>")
                    outfile.write("<td> " + component['name'] +"  </td>")
                    outfile.write("<td>" + component_properties['name'] + "</td>")
                    outfile.write("<td>" + component_properties['value'] +"</td>")
                    outfile.write("<td>" + component_properties['description'] +"</td>")
                    outfile.write("</tr>")

                # For each component process
                for component_process in component['processes']:
                    for component_process_properties in component_process['properties']:
                        outfile.write("<td> component process </td>")
                        outfile.write("<td> " + component['name'] +"/"+ component_process['name'] +"  </td>")
                        outfile.write("<td>" + component_process_properties['name'] + "</td>")
                        outfile.write("<td>" + component_process_properties['value'] +"</td>")
                        outfile.write("<td>" + component_process_properties['description'] +"</td>")
                        outfile.write("</tr>")

            for environment in app['environments']:
                #
                for cur_prop in environment['properties']:
                    outfile.write("<td> environment </td>")
                    outfile.write("<td>" + environment['name'] + "</td>")
                    outfile.write("<td>" + cur_prop['name'] + "</td>")
                    outfile.write("<td>" + cur_prop['value'] +"</td>")
                    outfile.write("<td>" + cur_prop['description'] +"</td>")
                    outfile.write("</tr>")
                #
                for comp_name, env_comp_props in environment['compProperties'].iteritems():
                    for cur_prop in env_comp_props:
                        outfile.write("<td> environment component </td>")
                        outfile.write("<td>" + environment['name'] +" / "+ comp_name + "</td>")
                        outfile.write("<td>" + cur_prop['name'] + "</td>")
                        outfile.write("<td>" + cur_prop['value'] +"</td>")
                        outfile.write("<td>" + cur_prop['description'] +"</td>")
                        outfile.write("</tr>")
                #
                for resource in environment['resources']:
                    for cur_prop in resource['properties']:
                        outfile.write("<td> resource </td>")
                        outfile.write("<td>" + resource['name'] + "</td>")
                        outfile.write("<td>" + cur_prop['name'] + "</td>")
                        outfile.write("<td>" + cur_prop['value'] +"</td>")
                        outfile.write("<td>" + cur_prop['description'] +"</td>")
                        outfile.write("</tr>")
            #
            #            pprint( app['processes'], depth=2 )
            #
            for process in app['processes']:
                # pprint( process['properties'] )
                for cur_prop in process['properties']:
                    outfile.write("<td> process </td>")
                    outfile.write("<td>" + process['name'] + "</td>")
                    outfile.write("<td>" + cur_prop['name'] + "</td>")
                    outfile.write("<td>" + cur_prop['value'] +"</td>")
                    outfile.write("<td>" + cur_prop['description'] +"</td>")
                    outfile.write("</tr>")
            outfile.write( "</table>" )
        outfile.write("</body></html>")

__main__()
