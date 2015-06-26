#!/usr/bin/env python
'''

Helper library to extract the properties from UCD.

v0.6
sgwilbur

requirements.txt:

requests==2.0.1

'''
import os
import json
import re
import requests
from pprint import pprint


# hard coded for testing
user        = 'admin'
passwd      = 'Rat1onal'
base_url    = 'https://deploy.rational.sl'

filter_app_name    = 'MyerOnline - WebSphere Commerce Server Site'
verbose = 1

## Simple helper method to print out some session and request info.
def print_request_details( r, s ):
    print "r.request.headers: ", r.request.headers
    print "s.cookies: ", s.cookies
    print "r.headers: ", r.headers
    print "r.text: ", r.text 

## quick login helper
def login( s ):
    s.auth = ( user, passwd )
    s.verify = False
    r = s.get( base_url + '/security/user' )
    my_c =  r.headers['set-cookie']
    
    if 'UCD_SESSION_KEY' in my_c: 
        m = re.search('UCD_SESSION_KEY=(.{36});', my_c )
        if m:
            s.headers.update({'UCD_SESSION_KEY': m.group(1) })

## 
## wrap the get request to return a dict from the json
def get_dict( s, url ):
    if verbose:
        print "Get: ", url
    
    r = s.get( url )
    if r.status_code != 200:
        print 'HTTP Status: ' + str(r.status_code)
        print_request_details( r, s )
        obj = []
    elif r.text:
        obj = json.loads( r.text )
    else:
        obj = []
    
    return obj

##
def __main__():
    props = {}
    s = requests.Session()
    login( s )    
    
    app_rest_uri    = '/rest/deploy/application'

    # Loop over all apps
    applications = get_dict( s, base_url + app_rest_uri )
#    pprint ( applications )

    # Filter down to a specific app that I want by name, could also do something like
    # this with tags if desired...
    applications = [ app for app in applications if app['name'] == filter_app_name ]

    for app in applications:
        cur_app = {}
        
        app_name = app['name']
        app_id = app['id']
        
        props[ app_name ] = { 'name': app_name, 'id': app_id }
        
        # Get app properties
        app_properties = get_dict( s, base_url + '/cli/application/getProperties?application=' + app_id )
        app['properties'] = app_properties
        
        # Get all components for the current application, but just take what I want from the component obj via a dict comprehension
        components = get_dict( s, base_url + '/rest/deploy/application' + '/' + app_id + '/components' )
        components = [ { 'name': component['name'], 'id' : component['id'] } for component in components ]
        
        for comp in components:
#            print comp['name']
            current_component = get_dict( s, base_url + '/cli/component/getProperties?component=' + comp['id'] )
            comp['properties'] = current_component
            
            # Get processes and iterate
            comp_processes = get_dict( s, base_url + '/rest/deploy/component/' + comp['id'] + '/processes/false' )
            comp_processes = [ { 'name': process['name'], 'id' : process['id'] } for process in comp_processes ]
            
            for comp_process in comp_processes:
#                pprint( comp_process )
                #comp_processes = get_dict( s, base_url + '/cli/componentProcess/info?component=' + comp['id'] +'&componentProcess=' + comp_process['name'] )
                # TODO: Get properties for the current process
                comp_process['properties'] = []
                
            comp['processes'] = comp_processes

        app['components'] = components

        # Loop over each process for the current application
        # TODO: not sure how to get these props?
        processes = get_dict( s, base_url + '/rest/deploy/application' + '/' + app_id + '/processes/' + 'false' )
        for process in processes:
#            pprint( process )
            current_processes = get_dict( s, base_url + '/rest/deploy/applicationProcess/' + process['id'] + '/' + str(process['version']) )
            process['properties'] = current_processes
        
        app['processes'] = []

        # Loop over each environment for the current application, simplify output
        environments = get_dict( s, base_url + '/rest/deploy/application' + '/' + app_id + '/environments/' + 'false' )
        environments = [ { 'name': environment['name'], 'id' : environment['id'] } for environment in environments ]
        
        for env in environments:
            current_env = get_dict( s, base_url + '/rest/deploy/environment/' + env['id'] )
            
            # Get environment properties
            env_properties = get_dict( s, base_url + '/cli/environment/getProperties?environment=' + env['id'] )
            env['properties'] =  env_properties
            
            # Get environment component properties, requires component list to check with
            env_comp_properties = {}
            for component in components:
                cur_env_comp_properties = get_dict( s, base_url + '/cli/environment/componentProperties?environment=' + env['id'] + '&component=' + component['id'] )
                env_comp_properties[ component['name'] ] = cur_env_comp_properties
            
            env['compProperties'] = env_comp_properties
            
            # Get all resources for current environment
            base_resources = get_dict( s, base_url + '/cli/environment/getBaseResources?environment=' + env['id'] )
            base_resources = [ { 'id': resource['id'], 'name': resource['name']} for resource in base_resources ]
#            pprint( base_resources )
            
            for resource in base_resources:
                resource_properties = get_dict( s, base_url + '/cli/resource/getProperties?resource=' + resource['id'] )
                resource['properties'] = resource_properties
                
            env['resources'] = base_resources
            
        app['environments'] = environments


# For reference you can inspect the dict blob I have assembled
#    pprint( applications )
#    pprint( applications, depth=3 )

    with open('properties.html', 'w+') as outfile:
        outfile.write("<html><head></head><body>")

        for app in applications:
            
            pprint( app )
            
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
#           
            for app_properties in app['properties']:
                outfile.write("<tr>")
                outfile.write("<td> application </td>")
                outfile.write("<td>" + app['name'] +"  </td>")
                outfile.write("<td>" + app_properties['name'] + "</td>")
                outfile.write("<td>" + app_properties['value'] +"</td>")
                outfile.write("<td>" + app_properties['description'] +"</td>")
                outfile.write("</tr>")
#            
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
#            
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
#                pprint( process['properties'] )
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
