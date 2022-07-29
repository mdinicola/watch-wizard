from common.enhanced_json_encoder import EnhancedJSONEncoder
from clients.trakt_client import TraktClient
from os import environ
import json
import logging

AWS_SECRET_NAME = environ['TraktSecretName']
TRAKT_CLIENT_ID_KEY = 'CLIENT_ID'
TRAKT_CLIENT_SECRET_KEY = 'CLIENT_SECRET'

_logger = logging.getLogger(__name__)

def recommend_movie():
    trakt_client = TraktClient(AWS_SECRET_NAME)
    return trakt_client.get_recommended_movie()

def recommend_movie_api_request(event, context):
    try:
        movie = recommend_movie()
   
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