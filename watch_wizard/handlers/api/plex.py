from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types

from http import HTTPStatus

from services.config import ConfigService
from services.plex import PlexService

logger = Logger()
app = APIGatewayRestResolver()

config_service = None
plex_service = None

def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)


def init():
    global config_service, plex_service

    if config_service is None:
        config_service = ConfigService()
    if plex_service is None:
        plex_service = PlexService(config_service.plex_config)


@app.get('/plex/health')
def health_check() -> dict:
    init()
    try:
        data = {
            'plex': plex_service.test_connection()
        }
        
        return data
    except Exception as e:
        data = {
            'plex': False,
            'msg': str(e)
        }
        return data

## Error Handling

@app.exception_handler(Exception)
def handle_exception(e: Exception):
    logger.error(e)
    return Response(
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR,
        content_type = content_types.APPLICATION_JSON,
        body = {
            'error': {
                'msg': str(e)
            }
        }
    )