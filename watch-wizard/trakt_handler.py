from dataclasses import dataclass, is_dataclass, asdict
from secretsmanager import SecretsManagerSecret
from trakt import core
import json
import time
import boto3
import logging

SERVICE_NAME = 'WatchWizard'
SECRET_NAME = f'apps/{SERVICE_NAME}'
TRAKT_CLIENT_ID_KEY = 'CLIENT_ID'
TRAKT_CLIENT_SECRET_KEY = 'CLIENT_SECRET'

logger = logging.getLogger(__name__)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)

@dataclass
class DeviceCode:
    user_code: str
    device_code: str
    verification_url: str
    poll_interval: int

@dataclass
class DeviceToken:
    oauth_token: str
    oauth_refresh: str
    oauth_expires_at: str

def _request_device_code(client_id: str, client_secret: str):
    response = core.get_device_code(client_id = client_id, client_secret = client_secret)
    return DeviceCode(user_code = response['user_code'], device_code = response['device_code'], 
        verification_url = response['verification_url'], poll_interval = response['interval'])

def get_auth_code(event, context):
    secret = SecretsManagerSecret(client = boto3.client('secretsmanager'), logger = logger, secret_name = SECRET_NAME)
    client_id = secret.get_value(TRAKT_CLIENT_ID_KEY)
    client_secret = secret.get_value(TRAKT_CLIENT_SECRET_KEY)
    device_code = _request_device_code(client_id, client_secret)

    response = {
        'data': device_code
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response, cls=EnhancedJSONEncoder)
    }

def authenticate(event, context):
    body = json.loads(event['body'])
    device_code = body['data']['device_code']
    core.CONFIG_TYPE = 'AWS_SECRETS_MANAGER'
    core.CONFIG_SECRET_NAME = SECRET_NAME
    core.load_config()

    success_message = "You've been successfully authenticated."

    error_messages = {
        404: 'Invalid device_code',
        409: 'You already approved this code',
        410: 'The tokens have expired, restart the process',
        418: 'You explicitly denied this code',
    }

    response = {
        'message': 'Something went wrong.  Please try again',
        'status_code': 500
    }
    
    interval = body['data']['poll_interval']

    while True:
        auth_response = core.get_device_token(device_code = device_code, 
            client_id= core.CLIENT_ID, client_secret = core.CLIENT_SECRET, store = True)

        if auth_response.status_code == 200:
            response['message'] = success_message
            response['status_code'] = 200
            break

        elif auth_response.status_code == 429:  # slow down
            interval *= 2

        elif auth_response.status_code != 400:  # not pending
            response['message'] = error_messages.get(auth_response.status_code, auth_response.reason)
            response['status_code'] = auth_response.status_code
            break

        time.sleep(interval)

    return {
        "statusCode": response['status_code'],
        "body": json.dumps(response, cls=EnhancedJSONEncoder)
    }