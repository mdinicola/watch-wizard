from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types
from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.shared.types import Annotated
from aws_lambda_powertools.event_handler.openapi.exceptions import RequestValidationError, ValidationException

from http import HTTPStatus
from typing import Optional

from utils import enhanced_json_serializer
from services.config import ConfigService
from services.trakt import TraktService
from services.plex import PlexService
from services.media import MediaService
from models.media import Movie

logger = Logger()
app = APIGatewayRestResolver(enable_validation = True, serializer = enhanced_json_serializer)

config_service = None
trakt_service = None
plex_service = None
media_service = None

def lambda_handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)


def init():
    global config_service, trakt_service, plex_service, media_service

    if config_service is None:
        config_service = ConfigService()
    if trakt_service is None:
        trakt_service = TraktService(config_service.trakt_config)
    if plex_service is None:
        plex_service = PlexService(config_service.plex_config)
    if media_service is None:
        media_service = MediaService(trakt_service, plex_service)


@app.get('/media/recommend-movie')
def recommend_movie():
    init()
    return media_service.recommend_movie()


@app.get('/media/search')
def search(title: Annotated[str, Query()], 
    year: Annotated[Optional[str], Query()] = '', 
    media_type: Annotated[Optional[str], Query(pattern = '^(movie|tvshow)$', alias = 'type')] = 'movie', 
    limit: Annotated[Optional[int], Query()] = 1):
        init()
        query = f'{title}'
        if year != '':
            query = f'{title} ({year})'

        return media_service.search(query, media_type, limit)

## Error Handling

@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationException)
def handle_validation_error(e: ValidationException):
    logger.error(e.errors())
    return Response(
        status_code = HTTPStatus.BAD_REQUEST,
        content_type = content_types.APPLICATION_JSON,
        body = {
            'errors': e.errors()
        }
    )

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