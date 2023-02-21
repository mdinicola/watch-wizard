from utils.enhanced_json_encoder import EnhancedJSONEncoder
from services.config import ConfigService
from services.trakt import TraktService
import json
import logging

_logger = logging.getLogger(__name__)
_config_service = ConfigService.load_config()

def get_auth_code(event, context):
    client_id = _config_service.trakt_config.get('client_id')
    client_secret = _config_service.trakt_config.get('client_secret')

    if client_id is None or client_secret is None:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Trakt configuration is invalid or not set'})
        }

    response = TraktService.get_auth_code(client_id, client_secret)

    return {
        'statusCode': 200,
        'body': json.dumps(response, cls=EnhancedJSONEncoder)
    }

def authenticate_device(event, context):
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

    response = TraktService.authenticate_device(device_code, poll_interval, _config_service.trakt_config.get('secret_name'), 
                                                    _config_service.config.get('secrets_manager_endpoint'))

    return {
        'statusCode': response['status_code'],
        'body': json.dumps({
            "message": response['message']
        })
    }