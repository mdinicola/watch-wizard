from utils import EnhancedJSONEncoder
from services.config import ConfigService
from services.media import MediaService
from models import Movie
from typing import List
import json
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_config_service = ConfigService.load_config()
_media_service = MediaService(_config_service.trakt_config, _config_service.plex_config, 
                                _config_service.config.get('secrets_manager_endpoint'))

def recommend_movie(event, context) -> dict:
    try:
        movie: Movie = _media_service.recommend_movie()
   
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
    
def search(event, context) -> dict:
    try:
        query_parameters = event.get('queryStringParameters', {})
        query_title = query_parameters.get('title', '')
        query_year = query_parameters.get('year', '')
        query_type = query_parameters.get('type', 'movie')
        query_limit = query_parameters.get('limit', 1)
        
        if query_title == '':
            raise Exception('Invalid query parameters')
        
        query = f'{query_title}'
        if query_year != '':
            query = f'{query_title} ({query_year})'

        media_list: List[Movie] = _media_service.search(query, query_type, query_limit)
            
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