from aws_lambda_powertools import Logger
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from services.config import ConfigService
from services.trakt import TraktService
from services.plex import PlexService
from services.media import MediaService, Movie
import ask_sdk_core.utils as ask_utils

logger = Logger()

config_service = ConfigService()
trakt_service = TraktService(config_service.trakt_config)
plex_service = PlexService(config_service.plex_config)
media_service = MediaService(trakt_service, plex_service)


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


class MovieRecommendationIntentHandler(AbstractRequestHandler):
    """Handler for Movie Recommendation Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("MovieRecommendationIntent")(handler_input)

    def handle(self, handler_input):
        movie: Movie = media_service.recommend_movie()
        message = movie.recommendation_message()
        speak_output = message

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class MovieAvailabilityIntentHandler(AbstractRequestHandler):
    """Handler for Movie Availability Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("MovieAvailabilityIntent")(handler_input)

    def handle(self, handler_input):
        movie_title_slot_value = ask_utils.get_slot_value_v2(handler_input, 'movieTitle')
        movie_title_slot_values = list(map(lambda x: x.value, ask_utils.get_simple_slot_values(movie_title_slot_value)))
        movie_title = movie_title_slot_values[0]

        year_slot_value = ask_utils.get_slot_value_v2(handler_input, 'year')
        if year_slot_value is not None:
            year_slot_values = list(map(lambda x: x.value, ask_utils.get_simple_slot_values(year_slot_value)))
            year = year_slot_values[0]
            movie_title += f' ({year})'

        movie_list = media_service.search(movie_title, 'movie', 1)
        if movie_list:
            movie: Movie = movie_list[0]
            message = f'Found movie: {movie.title} ({movie.year}).  {movie.availability_message()}'
        else:
            message = f'I was unable to find movie: {movie_title}'

        speak_output = message

        return (
            handler_input.response_builder
            .speak(speak_output)
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


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input)
                or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

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
        logger.exception(exception)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )
