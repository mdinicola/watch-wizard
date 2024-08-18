from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types

from http import HTTPStatus

from utils import enhanced_json_serializer
from services.config import ConfigService

logger = Logger()
app = APIGatewayRestResolver(serializer = enhanced_json_serializer)

config_service = None

def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)


def init():
    global config_service
    if config_service is None:
        config_service = ConfigService()


@app.get('/config')
def get_config():
    init()
    return config_service


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