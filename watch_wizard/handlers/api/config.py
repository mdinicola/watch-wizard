from utils import EnhancedJSONEncoder
from services.config import ConfigService
import json
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_config_service = ConfigService()

def get_config(event, context) -> dict:
    try:
        return {
            'statusCode': 200,
            'body': json.dumps(_config_service, cls=EnhancedJSONEncoder)
        }
    except Exception as e:
        _logger.exception(e)
        message = 'Unable to retrieve configuration.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }