from ask_sdk_core.dispatch_components import AbstractRequestHandler
from clients.aws_secrets_manager import SecretsManagerSecret
from handlers import movies_handler
from os import environ

import ask_sdk_core.utils as ask_utils
from clients.alexa_client import AlexaClient, IntentReflectorHandler, CancelOrStopIntentHandler, SessionEndedRequestHandler, CatchAllExceptionHandler
import boto3
import json
import logging

_logger = logging.getLogger(__name__)

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
        movie = movies_handler.recommend_movie()
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

_AWS_SECRET_NAME = environ['ServiceSecretName']
_ALEXA_SKILL_ID_KEY = 'ALEXA_SKILL_ID'
_secretsmanager_client = boto3.client('secretsmanager')

# Configures and returns an AlexaClient
def alexa_client():
    secret = SecretsManagerSecret(_secretsmanager_client, secret_name = _AWS_SECRET_NAME)
    skill_id = secret.get_value(_ALEXA_SKILL_ID_KEY)

    # Creates AlexaClient and verifies configured skill_id matches incoming Alexa requests
    alexa_client = AlexaClient(skill_id)

    # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
    alexa_client.add_request_handlers([ LaunchRequestHandler(), RecommendMovieIntentHandler(), HelpIntentHandler(),
                                        CancelOrStopIntentHandler(), SessionEndedRequestHandler(), IntentReflectorHandler() ])

    alexa_client.add_exception_handler(CatchAllExceptionHandler())
    return alexa_client

def handle_skill_request(event, context):
    handler = alexa_client().get_lambda_handler()
    return handler(event, context)

def handle_api_request(event, context):
    handler = alexa_client().get_webservice_handler()
    response = handler.verify_request_and_dispatch(event['headers'], event['body'])
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }