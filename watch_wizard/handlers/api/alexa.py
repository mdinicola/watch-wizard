from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types

from http import HTTPStatus

from handlers.alexa.lambdas import alexa_service

logger = Logger()
app = APIGatewayRestResolver()


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)


@app.post('/alexa/skills')
def handle_skill_request() -> dict:
    handler = alexa_service().get_webservice_handler()
    response = handler.verify_request_and_dispatch(app.current_event.headers, app.current_event.body)
    return response


# Error Handling

@app.exception_handler(Exception)
def handle_exception(e: Exception):
    logger.exception(e)
    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content_type=content_types.APPLICATION_JSON,
        body={
            'error': {
                'msg': str(e)
            }
        }
    )
