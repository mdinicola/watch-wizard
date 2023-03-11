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
    
def search(event, context):
    try:
        query_parameters = event.get('queryStringParameters', {})
        query = query_parameters.get('query', '')
        query_year = query_parameters.get('year', '')
        query_type = query_parameters.get('type', 'movie')
        query_limit = query_parameters.get('limit', 1)
        
        if query == '':
            raise Exception('Invalid query parameter')

        if query_year != '':
            query = f'{query} ({query_year})'
        else:
            query = f'{query}'

        media_list = _media_service.search(query, query_type, query_limit)
            
        return {
            'statusCode': 200,
            'body': json.dumps(media_list, cls=EnhancedJSONEncoder)
        }
    except Exception as e:
        _logger.exception(e)
        message = 'An unexpected error ocurred.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }