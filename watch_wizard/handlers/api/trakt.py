from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types

from http import HTTPStatus

from utils import enhanced_json_serializer
from models.trakt import DeviceAuthData
from services.config import ConfigService
from services.trakt import TraktService

logger = Logger()
app = APIGatewayRestResolver(enable_validation = True, serializer = enhanced_json_serializer)

config_service = None
trakt_service = None

def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)


def init():
    global config_service, trakt_service

    if config_service is None:
        config_service = ConfigService()
    if trakt_service is None:
        trakt_service = TraktService(config_service.trakt_config)


@app.get('/trakt/health')
def health_check() -> dict:
    init()
    try:
        data = {
            'trakt': trakt_service.test_connection()
        }
        return data
    except Exception as e:
        data = {
            'trakt': False,
            'msg': str(e)
        }
        return data


@app.get('/trakt/auth-code')
def get_auth_code() -> dict:
    init()
    return trakt_service.get_auth_code()


@app.post('/trakt/authenticate-device')
def authenticate_device(device_auth_data: DeviceAuthData) -> Response:
    init()
    device_code = device_auth_data.device_code
    poll_interval = device_auth_data.poll_interval

    response = trakt_service.authenticate_device(device_auth_data)

    return Response(
        status_code = response['status_code'],
        content_type = content_types.APPLICATION_JSON,
        body = {
            'msg': response['message']
        }
    )

## Error Handling

@app.exception_handler(Exception)
def handle_exception(e: Exception):
    logger.exception(e)
    return Response(
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR,
        content_type = content_types.APPLICATION_JSON,
        body = {
            'error': {
                'msg': str(e)
            }
        }
    )