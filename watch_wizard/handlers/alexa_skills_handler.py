from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from clients.aws_secrets_manager import SecretsManagerSecret
from handlers import movies_handler

from os import environ
import ask_sdk_core.utils as ask_utils
import boto3
import json
import logging

_logger = logging.getLogger(__name__)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to the Watch Wizard. You can say 'recommend a movie'?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class RecommendMovieIntentHandler(AbstractRequestHandler):
    """Handler for Recommend Movie Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RecommendMovieIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can ask me to recommend a movie"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        _logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

_AWS_SECRET_NAME = environ['ServiceSecretName']
_ALEXA_SKILL_ID_KEY = 'AlexaSkillId'
secret = SecretsManagerSecret(client = boto3.client('secretsmanager'), secret_name = _AWS_SECRET_NAME)

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

_skill_builder = SkillBuilder()

_skill_builder.add_request_handler(LaunchRequestHandler())
_skill_builder.add_request_handler(RecommendMovieIntentHandler())
_skill_builder.add_request_handler(HelpIntentHandler())
_skill_builder.add_request_handler(CancelOrStopIntentHandler())
_skill_builder.add_request_handler(SessionEndedRequestHandler())
_skill_builder.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

_skill_builder.add_exception_handler(CatchAllExceptionHandler())

def set_skill_id():
    skill_id = secret.get_value(_ALEXA_SKILL_ID_KEY)
    # SkillBuilder will verify the skill id matches the request from Alexa before routing to handlers
    _skill_builder.skill_id = skill_id

def handle_skill_request(event, context):
    set_skill_id()
    handler = _skill_builder.lambda_handler()
    return handler(event, context)

def handle_api_request(event, context):
    set_skill_id()
    # skip verification if testing locally
    if environ.get('AWS_SAM_LOCAL') == 'true':
        webservice_handler = WebserviceSkillHandler(skill=_skill_builder.create(), verify_signature=False, verify_timestamp=False)
    else:
        webservice_handler = WebserviceSkillHandler(skill=_skill_builder.create())

    response = webservice_handler.verify_request_and_dispatch(event['headers'], event['body'])
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }