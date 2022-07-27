from common.enhanced_json_encoder import EnhancedJSONEncoder
from clients.trakt_client import TraktClient
from clients.aws_secrets_manager import SecretsManagerSecret
from os import environ
import json
import boto3
import logging

AWS_SECRET_NAME = environ['TraktSecretName']
TRAKT_CLIENT_ID_KEY = 'CLIENT_ID'
TRAKT_CLIENT_SECRET_KEY = 'CLIENT_SECRET'

_logger = logging.getLogger(__name__)

def get_auth_code(event, context):
    secret = SecretsManagerSecret(client = boto3.client('secretsmanager'), secret_name = AWS_SECRET_NAME)
    client_id = secret.get_value(TRAKT_CLIENT_ID_KEY)
    client_secret = secret.get_value(TRAKT_CLIENT_SECRET_KEY)
    response = TraktClient.get_auth_code(client_id, client_secret)

    return {
        'statusCode': 200,
        'body': json.dumps(response, cls=EnhancedJSONEncoder)
    }

def authenticate_device(event, context):
    try:
        device_auth_data = json.loads(event['body'])['device_auth_data']
        device_code = device_auth_data['device_code']
        poll_interval = device_auth_data['poll_interval']
    except (KeyError, ValueError):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Request must include valid device_auth_data'
            })
        }
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Malformed request'
            })
        }

    response = TraktClient.authenticate_device(device_code, poll_interval, AWS_SECRET_NAME)

    return {
        'statusCode': response['status_code'],
        'body': json.dumps({
            "message": response['message']
        })
    }