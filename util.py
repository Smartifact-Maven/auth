import boto3

def response(statusCode, description, body=None):
    return {
        'status': str(statusCode),
        'statusDescription': description,
        'headers': {},
        'body': body if body is not None else description
    }
    

def get_table():
    return boto3.resource('dynamodb', region_name='us-east-1').Table('maven-auth-users')
