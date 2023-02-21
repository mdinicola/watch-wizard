from plexapi.exceptions import Unauthorized as UnauthorizedException
from services.config import ConfigService
from services.plex import PlexService
import json
import logging

_logger = logging.getLogger(__name__)
_config_service = ConfigService.load_config()

def authenticate(event, context):
    try:
        tfa_code_data = json.loads(event['body'])['tfa_code']
        tfa_code = tfa_code_data['code']
        
        _config_service.load_plex_credentials()
        
        plex_service = PlexService(_config_service.plex_config.get('token'), _config_service.plex_config.get('server_name'))
        
        plex_service.authenticate(_config_service.plex_config.get('username'), _config_service.plex_config.get('password'),
                                    tfa_code)
        
        _config_service.save_plex_config(plex_service.token)
   
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Plex authenticated successfully'})
        }
    except(UnauthorizedException):
        return {
            'statusCode': 401,
            'body': json.dumps({
                'message': 'Invalid credentials or TFA code'
            })
        }
    except(KeyError, ValueError):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Request must include valid tfa_code'
            })
        }
    except Exception as e:
        _logger.exception(e)
        message = 'An unexpected error ocurred.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }
    
def test(event, context):
    try:
        plex_service = PlexService(_config_service.plex_config.get('token'), _config_service.plex_config.get('server_name'))
        plex_service.test_connection()
    except Exception as e:
        _logger.exception(e)
        message = 'An unexpected error ocurred.  See log for details'
        return {
            'statusCode': 500,
            'body': json.dumps({'message': message})
        }