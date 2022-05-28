from dataclasses import is_dataclass, asdict
from clients.trakt_client import TraktClient
from clients.aws_secrets_manager import SecretsManagerSecret
from clients.google_assistant import format_google_actions_response
from os import environ
import json
import boto3
import logging

SERVICE_NAME = environ['ServiceName']
AWS_SECRET_NAME = environ['TraktSecretName']
TRAKT_CLIENT_ID_KEY = 'CLIENT_ID'
TRAKT_CLIENT_SECRET_KEY = 'CLIENT_SECRET'

_logger = logging.getLogger(__name__)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)

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

def recommend_movie(event, context):
    trakt_client = TraktClient(AWS_SECRET_NAME)
    movie = trakt_client.get_recommended_movie()

    message = f'You should watch {movie.title} ({movie.year})'

    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }

def recommend_movie_and_speak(event, context):
    trakt_client = TraktClient(AWS_SECRET_NAME)
    movie = trakt_client.get_recommended_movie()

    message = f'You should watch {movie.title} ({movie.year})'
    request_data = json.loads(event['body'])
    response = format_google_actions_response(request_data, message)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }