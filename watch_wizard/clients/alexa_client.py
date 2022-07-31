from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from ask_sdk_core.skill_builder import SkillBuilder
from os import environ
import ask_sdk_core.utils as ask_utils
import logging

_logger = logging.getLogger(__name__)

class AlexaClient:
    def __init__(self, skill_id):
        self._skill_builder = SkillBuilder()
        self._skill_builder.skill_id = skill_id

    def add_request_handlers(self, handlers):
        for handler in handlers:
            self._skill_builder.add_request_handler(handler)

    def add_exception_handler(self, handler):
        self._skill_builder.add_exception_handler(handler)

    def get_lambda_handler(self):
        return self._skill_builder.lambda_handler()

    def get_webservice_handler(self):
        # skip verification if testing locally
        if environ.get('AWS_SAM_LOCAL') == 'true':
            return WebserviceSkillHandler(skill=self._skill_builder.create(), verify_signature=False, verify_timestamp=False)
        else:
            return WebserviceSkillHandler(skill=self._skill_builder.create())

### Default Alexa request handlers

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # Any cleanup logic goes here.

        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
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
        return True

    def handle(self, handler_input, exception):
        _logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )