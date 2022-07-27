from clients.google_actions import format_response
from clients.trakt_client import TraktClient
from os import environ
import json
import logging

AWS_SECRET_NAME = environ['TraktSecretName']
TRAKT_CLIENT_ID_KEY = 'CLIENT_ID'
TRAKT_CLIENT_SECRET_KEY = 'CLIENT_SECRET'

_logger = logging.getLogger(__name__)

def handle_response(event, context):
    try:
        request_data = json.loads(event['body'])
        handler_name = request_data['handler']['name']
        
        if handler_name == 'recommend_movie':
            return recommend_movie(request_data)
        else:
            message = f'Handler name {handler_name} is not valid'
            return {
                'statusCode': 400,
                'body': json.dumps(message)
            }

    except Exception as e:
        _logger.exception(e)
        message = 'An unexpected error ocurred.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }

def recommend_movie(request_data):
    trakt_client = TraktClient(AWS_SECRET_NAME)
    movie = trakt_client.get_recommended_movie()
    message = movie.recommendation_message()
    response = format_response(request_data, message)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }