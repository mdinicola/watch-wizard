from ask_sdk_core.dispatch_components import AbstractRequestHandler
from services.config import ConfigService
from services.trakt import TraktService
from services.movies import MovieService
import services.alexa as alexa
import ask_sdk_core.utils as ask_utils
import os
import logging

_logger = logging.getLogger(__name__)
_config_service = ConfigService.load_config()

### Define Alexa request handler classes

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Welcome to the Watch Wizard. You can say 'recommend a movie'."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class RecommendMovieIntentHandler(AbstractRequestHandler):
    """Handler for Recommend Movie Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("RecommendMovieIntent")(handler_input)

    def handle(self, handler_input):
        trakt_client = TraktService(_config_service.trakt_config.get('secret_name'), _config_service.config.get('secrets_manager_endpoint'))
        movie = MovieService(trakt_client).recommend_movie()
        message = movie.recommendation_message()
        speak_output = message

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "You can ask me to recommend a movie"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

###############################

### Lambda functions start

# Configures and returns an AlexaService
def alexa_service():
    # Creates AlexaClient and verifies configured skill_id matches incoming Alexa requests
    alexa_service = alexa.AlexaService(_config_service.alexa_config.get('skill_id'))

    # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
    alexa_service.add_request_handlers([ LaunchRequestHandler(), RecommendMovieIntentHandler(), HelpIntentHandler(),
                                        alexa.CancelOrStopIntentHandler(), alexa.SessionEndedRequestHandler(), alexa.IntentReflectorHandler() ])

    alexa_service.add_exception_handler(alexa.CatchAllExceptionHandler())
    return alexa_service

def handle_skill_request(event, context):
    handler = alexa_service().get_lambda_handler()
    return handler(event, context)