from utils.enhanced_json_encoder import EnhancedJSONEncoder
from services.trakt import TraktService
from services.aws_secrets_manager import SecretsManagerService
from services.movies import MovieService
from handlers.alexa import handle_skill_request
import os
import json
import logging

_logger = logging.getLogger(__name__)

AWS_SECRET_NAME = os.environ['TraktSecretName']
AWS_SECRETS_MANAGER_ENDPOINT = os.environ['SecretsManagerEndpoint']
TRAKT_CLIENT_ID_KEY = 'CLIENT_ID'
TRAKT_CLIENT_SECRET_KEY = 'CLIENT_SECRET'

def get_auth_code(event, context):
    secret = SecretsManagerService(client = SecretsManagerService.get_client(), secret_name = AWS_SECRET_NAME)
    client_id = secret.get_value(TRAKT_CLIENT_ID_KEY)
    client_secret = secret.get_value(TRAKT_CLIENT_SECRET_KEY)

    if client_id == '' or client_secret == '':
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Trakt configuration is invalid or not set'})
        }

    response = TraktService.get_auth_code(client_id, client_secret)

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

    response = TraktService.authenticate_device(device_code, poll_interval, AWS_SECRET_NAME, AWS_SECRETS_MANAGER_ENDPOINT)

    return {
        'statusCode': response['status_code'],
        'body': json.dumps({
            "message": response['message']
        })
    }

def recommend_movie(event, context):
    try:
        trakt_client = TraktService(AWS_SECRET_NAME, AWS_SECRETS_MANAGER_ENDPOINT)
        movie = MovieService(trakt_client).recommend_movie()
   
        return {
            'statusCode': 200,
            'body': json.dumps(movie, cls=EnhancedJSONEncoder)
        }

    except Exception as e:
        _logger.exception(e)
        message = 'An unexpected error ocurred.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }
    
def handle_alexa_skill_request(event, context):
    response = handle_skill_request(event['headers'], event['body'])
   
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }