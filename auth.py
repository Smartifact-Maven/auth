import base64
import boto3
import hashlib
import json
from util import get_table, response

def hash(password):
    m = hashlib.sha256()
    m.update(password.encode(encoding='UTF-8', errors='strict'))
    return base64.b64encode(m.digest())

def authenticate(headers):
    if 'authorization' not in headers:
        return (False, response(400, 'Bad Request', 'Authorization header missing'))

    authorization = headers['authorization'][0]['value']

    if not authorization.startswith('Basic'):
        return (False, response(400, 'Bad Request', 'Authorization type not supported'))
    else:
        authorization = base64.b64decode(authorization[6:])
        [username, password] = authorization.decode('utf-8').split(':', 1)

    table = get_table()
    
    password = hash(password)
    
    user = table.get_item(
        Key={
            'username': username
        },
        ConsistentRead=True
    )
    
    if 'Item' in user:
        user = user['Item']
    else:
        return (False, response(401, 'User \'' + username + '\' does not exist'))

    existing_password = user['password']

    if existing_password == password:
        user['username'] = username
        return (True, user)
    else:
        return (False, response(401, "Incorrect password"))
        
def authorize(user, action, uri='*'):
    print(f'AUTHORIZE user={user} action={action} uri={uri}')
    if action != 'admin' and authorize(user, 'admin', uri):
        return True
    
    if 'permissions' not in user or action not in user['permissions']:
        return False
    
    for scope in user['permissions'][action]:
        if scope == '*' or uri.startswith(scope):
            return True
    
    return False