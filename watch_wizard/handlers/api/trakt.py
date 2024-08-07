from utils import EnhancedJSONEncoder
from services.config import ConfigService
from services.trakt import TraktService
import json
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_config_service = ConfigService()
_trakt_service = TraktService(_config_service.trakt_config)

def get_auth_code(event, context) -> dict:
    try:
        response = _trakt_service.get_auth_code()

        return {
            'statusCode': 200,
            'body': json.dumps(response, cls=EnhancedJSONEncoder)
        }
    except Exception as e:
        response = {
            'message': 'An unknown error has occurred',
            'error': e
        }
        return {
            'statusCode': 500,
            'body': json.dumps(response, cls=EnhancedJSONEncoder)
    }

def authenticate_device(event, context) -> dict:
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

    response = _trakt_service.authenticate_device(device_code, poll_interval)

    return {
        'statusCode': response['status_code'],
        'body': json.dumps({
            "message": response['message']
        })
    }

def health_check(event, context) -> dict:
    try:
        trakt_status = _trakt_service.test_connection()
        data = {
            'trakt': trakt_status
        }
        return {
            'statusCode': 200,
            'body': json.dumps({'status': data}, cls=EnhancedJSONEncoder)
        }
    except Exception as e:
        _logger.exception(e)
        message = 'Trakt connection unsuccessful.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }