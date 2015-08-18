#!/usr/bin/env python
import requests, urllib
import re, json
'''
 Example of connecting to the RTCP rest api and deleting an environment.
 
 @see http://pic.dhe.ibm.com/infocenter/rtwhelp/v8r5m1/index.jsp?topic=%2Fcom.ibm.rational.rtcp.sysadmin.doc%2FRTCP_REST_ref_environments.html
 
 Only works if there are no dependencies, if the delete fails with HTTP 420, go to the RTCP console check
 your agents and remove any active Rules that may be referencing the transient environments.

'''
# hard coded
user = 'admin'
passwd = 'admin'
host = 'devops.workshop'
port = '7819'
base_url = 'http://' + host + ':' + port + '/RTCP'
rest_url = base_url + '/rest'

def __main__():

    s = requests.Session()
    s.auth = ( user, passwd )
    s.verify = False
    
#    r = s.get( rest_url + '/environments/?domain=JKE&env=DEV 7ce7e6f4-18bb-4daf-aa0e-ea31d26768be' )
#    r = s.get( base_url + '/#Vie:JKE' )
    
#    print "r.request.headers: ", r.request.headers
#    print "s.cookies: ", s.cookies
#    print "r.headers: ", r.headers
#    print "r.text: ", r.text
   
   
#  Silly helper so I can just cut and past from the web page, since I can't seem to scrape it...
    text = '''
DEV 37d43f05-e1ab-4307-ba68-2194be90b0cd
DEV 419c7d38-63bd-44cd-b304-3a0c39da6ed7
DEV d41e8d1b-6776-4708-840b-3ae4118baf82
'''.strip()

    bad_envs = text.splitlines()

    url = rest_url + '/environments/'
# Question: Not sure how to query ?
#  url = base_url + '/environments/?domain=JKE&env=DEV*'
# Answer: in this release this is not a query url at all, you need to have the full
# environment name to do anything with it.
#  url = base_url + '/environments/JKE/' + urllib.quote('DEV 1a951f3b-3d03-44d4-95a3-15094b820c12') + '/'	
#  print "call GET on " + url
#  r = s.get( url=url )
#  print "response: " + r.text


    for cur_env in bad_envs:
        url = rest_url + '/environments/JKE/' + urllib.quote(cur_env) +'/'
        print "call GET on " + url
        r = s.get( url=url )
        print "response: " + r.text

        print "call DELETE on " + url
        r = s.delete( url=url )
        print "response: ", r.text
        print r
        print "\n"

__main__()  