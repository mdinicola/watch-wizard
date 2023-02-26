from services.config import ConfigService
from services.plex import PlexService
import json
import logging

_logger = logging.getLogger(__name__)
_config_service = ConfigService.load_config()
_plex_service = PlexService(_config_service.plex_config)

def health_check(event, context):
    try:
        plex_status = _plex_service.test_connection()
        data = {
            'plex': plex_status
        }
        return {
            'statusCode': 200,
            'body': json.dumps({'status': data})
        }
    except Exception as e:
        _logger.exception(e)
        message = 'Plex connection unsuccessful.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }