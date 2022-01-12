from auth import hash
from pprint import pp
import json
import urllib.request
import urllib.parse
from urllib import parse
from urllib.error import HTTPError
from util import *

def create_user(params):
    username = params['username'][0]
    password = params['password'][0]
    
    if username is None:
        return response(400, 'Username missing')
        
    if password is None:
        return response(400, 'Password missing')
        
    permissions = {
        
    }
    
    for permission in params['permissions']:
        scope = '*'
        
        if '=' in permission:
            [permission, scope] = permission.split('=', 1)
            
        if permission not in permissions:
            permissions[permission] = []
        
        permissions[permission].append(scope)
        
    password = hash(password)

    get_table().update_item(
        Key={
            'username': username
        },
        UpdateExpression='SET password = :pw, #ps = :perms',
        ExpressionAttributeValues={
            ':pw': password,
            ':perms': permissions
        },
        ExpressionAttributeNames={
            '#ps': 'permissions'
        }
    )
    
    return response(200, '')

def update_password(params):
    return response(500, 'Not yet implemented')

def add_permissions(params):
    return response(500, 'Not yet implemented')

actions = {
    'create_user': create_user,
    'update_password': update_password,
    'add_permissions': add_permissions
}

def invoke(action, params):
    if action not in actions:
        return response(400, 'Invalid Action', 'Action \''+ action + '\' does not exist')
        
    return actions[action](dict(parse.parse_qs(params)))
    
def get_list(name):
    return json.loads(urllib.request.urlopen(f'http://localhost:2772/applications/Smartifact/environments/Dev/configurations/' + name))
    
def upload(uploader, distribution, request):
    url = 'http://maven.quiltmc.org.s3-website-us-west-2.amazonaws.com' + request['uri']
    
    request['headers']['x-amz-acl'] = [
        {'key': 'x-amz-acl', 'value': 'bucket-owner-full-control'}
    ]
    
    request['headers']['x-amz-meta-uploader'] = [
        {'key': 'x-amz-meta-uploader', 'value': uploader}
    ]
    
    allowed = get_list('AllowedFileSuffixes')
    blocked = get_list('BlockedFileSuffixes')
            
    if any(url.endswith(s) for s in allowed and all(not url.endswith(s) for s in blocked)):
        try:
            urllib.request.urlopen(url)
            
            return response(409, 'File Already Exists')
        except HTTPError as e:
            if e.status == 404 or e.status == 403:
                return request
            else:
                print(url)
                pp(e)
                
                return response(500, 'Internal Server Error')
    else:
        return response(400, 'Invalid file suffix')