from services.config import ConfigService
from handlers.alexa.requests import LaunchRequestHandler, HelpIntentHandler, SessionEndedRequestHandler
from handlers.alexa.requests import IntentReflectorHandler, CancelOrStopIntentHandler, CatchAllExceptionHandler
from handlers.alexa.requests import MovieRecommendationIntentHandler, MovieAvailabilityIntentHandler
from services.alexa import AlexaService
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_config_service = ConfigService()

# Configures and returns an AlexaService
def alexa_service() -> AlexaService:
    # Creates AlexaClient and verifies configured skill_id matches incoming Alexa requests
    alexa_service = AlexaService(_config_service.alexa_config)

    # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
    alexa_service.add_request_handlers([ LaunchRequestHandler(), MovieRecommendationIntentHandler(), MovieAvailabilityIntentHandler(),
                                        HelpIntentHandler(), CancelOrStopIntentHandler(), SessionEndedRequestHandler(), IntentReflectorHandler() ])

    alexa_service.add_exception_handler(CatchAllExceptionHandler())
    return alexa_service

def handle_skill_request(event, context):
    handler = alexa_service().get_lambda_handler()
    return handler(event, context)