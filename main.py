import actions
import auth
import json
import os
from pprint import pp
from util import response
            
def handle(event, context):
    request = event['Records'][0]['cf']['request']
    method = request['method']
    headers = request['headers']
    
    if request['uri'].startswith('/publish'):
        request['uri'] = request['uri'][8:]
 
    if method == 'PUT':
        authenticated, authentication = auth.authenticate(headers)
        
        if authenticated:
            # TODO: Ensure URI begins with a valid repository
            # TODO: Ensure URI ends with a valid file type
        
            uri = request['uri']
            
            
            if method == 'PUT':
                if auth.authorize(authentication, 'write', uri):
                    return actions.upload(authentication['username'], event['Records'][0]['cf']['config']['distributionDomainName'], request)
                else:
                    return response(401, 'Access Denied', 'User does not have permission to write to ' + uri)
            else:
                return actions.invoke(uri.strip('/'), request['querystring'])
        else:
            return authentication
    elif method == "GET":
        # Redirect GET requests to the static site endpoint
        request['headers']['host'] = [{'key': 'host', 'value': 'maven.quiltmc.org.s3-website-us-west-2.amazonaws.com'}]
        
        del request['origin']['s3']
        
        request['origin']['custom'] = {
          'customHeaders': {},
          'domainName': 'maven.quiltmc.org.s3-website-us-west-2.amazonaws.com',
          'keepaliveTimeout': 5,
          'path': '',
          'port': 80,
          'protocol': 'http',
          'readTimeout': 30,
          'sslProtocols': [
            'TLSv1',
            'TLSv1.1',
            'TLSv1.2'
          ]
        }
            
        # S3 has some unfortunate internal handling of unusual characters in
        # URI's, so we need to replace and encode this ourselves.
        request['uri'] = request['uri'].replace('+', '%20')
        
        return request
    else:
        return response(400, 'Invalid Method')


def lambda_handler(event, context):
    print("REQUEST", event)

    response = handle(event, context)
    
    print("RESPONSE", response)
    
    return response