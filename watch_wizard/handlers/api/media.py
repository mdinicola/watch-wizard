from utils import EnhancedJSONEncoder
from services.config import ConfigService
from services.media import MediaService
import json
import logging

_logger = logging.getLogger(__name__)
_config_service = ConfigService.load_config()
_media_service = MediaService(_config_service.trakt_config, _config_service.plex_config, 
                                _config_service.config.get('secrets_manager_endpoint'))

def recommend_movie(event, context):
    try:
        movie = _media_service.recommend_movie()
   
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
    
def get_availability(event, context):
    try:
        query_parameters = event.get('queryStringParameters', {})
        media_query = query_parameters.get('query')
        media_type = query_parameters.get('media_type', 'movie')
        media = _media_service.get_availability(media_query, media_type)
        return {
            'statusCode': 200,
            'body': json.dumps(media, cls=EnhancedJSONEncoder)
        }
    except Exception as e:
        _logger.exception(e)
        message = 'An unexpected error ocurred.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }