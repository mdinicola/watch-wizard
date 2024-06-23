from utils import EnhancedJSONEncoder
from services.config import ConfigService
import json
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_config_service = ConfigService()

def get_config(event, context) -> dict:
    try:
        data = {
            'trakt': _config_service.trakt_config,
            'plex': _config_service.plex_config,
            'alexa': _config_service.alexa_config,
            'config': _config_service
        }
        return {
            'statusCode': 200,
            'body': json.dumps(data, cls=EnhancedJSONEncoder)
        }
    except Exception as e:
        _logger.exception(e)
        message = 'Plex connection unsuccessful.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }