from utils.enhanced_json_encoder import EnhancedJSONEncoder
from services.config import ConfigService
from services.trakt import TraktService
from services.movies import MovieService
import json
import logging

_logger = logging.getLogger(__name__)
_config_service = ConfigService.load_config()

def recommend_movie(event, context):
    try:
        trakt_client = TraktService(_config_service.trakt_config.get('secret_name'), 
                                    _config_service.config.get('secrets_manager_endpoint'))
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