from ask_sdk_core.dispatch_components import AbstractRequestHandler
from services.aws_secrets_manager import SecretsManagerService
from services.trakt import TraktService
from services.movies import MovieService
from services.alexa import AlexaService, IntentReflectorHandler, CancelOrStopIntentHandler, SessionEndedRequestHandler, CatchAllExceptionHandler
import ask_sdk_core.utils as ask_utils
import os
import boto3
import json
import logging

_logger = logging.getLogger(__name__)

AWS_SECRET_NAME = os.environ['TraktSecretName']
AWS_SECRETS_MANAGER_ENDPOINT = os.environ['SecretsManagerEndpoint']

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
        trakt_client = TraktService(AWS_SECRET_NAME, AWS_SECRETS_MANAGER_ENDPOINT)
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

_AWS_SECRET_NAME = os.environ['ServiceSecretName']
_ALEXA_SKILL_ID_KEY = 'ALEXA_SKILL_ID'

# Configures and returns an AlexaClient
def alexa_client():
    secret = SecretsManagerService(client = SecretsManagerService.get_client(), secret_name = _AWS_SECRET_NAME)
    skill_id = secret.get_value(_ALEXA_SKILL_ID_KEY)

    # Creates AlexaClient and verifies configured skill_id matches incoming Alexa requests
    alexa_client = AlexaService(skill_id)

    # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
    alexa_client.add_request_handlers([ LaunchRequestHandler(), RecommendMovieIntentHandler(), HelpIntentHandler(),
                                        CancelOrStopIntentHandler(), SessionEndedRequestHandler(), IntentReflectorHandler() ])

    alexa_client.add_exception_handler(CatchAllExceptionHandler())
    return alexa_client

def handle_skill_request(event, context):
    handler = alexa_client().get_lambda_handler()
    return handler(event, context)