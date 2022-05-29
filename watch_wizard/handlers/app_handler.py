from clients.google_assistant import format_google_actions_response
from handlers.trakt_handler import recommend_movie as trakt_recommend_movie
import json

def recommend_movie(event, context):
    movie = trakt_recommend_movie()
    message = f'You should watch {movie.title} ({movie.year})'
    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }

def recommend_movie_and_speak(event, context):
    movie = trakt_recommend_movie()
    message = f'You should watch {movie.title} ({movie.year})'
    request_data = json.loads(event['body'])
    response = format_google_actions_response(request_data, message)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }