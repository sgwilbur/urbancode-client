#!/usr/bin/env python

import base64
import httplib2

# hard coded
user = 'admin'
passwd = 'admin'
url = 'https://devops.uc6.demo:8443'

# derived
auth = base64.encodestring( user + ':' + passwd )

http = httplib2.Http(cache=None, timeout=30, disable_ssl_certificate_validation=True)
http.add_credentials( user, passwd )
 
response, content = http.request( url, 'GET', headers={ 'Authorization' : 'Basic ' + auth }ß)

#print response
print content