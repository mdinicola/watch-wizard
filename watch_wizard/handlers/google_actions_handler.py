from clients.google_actions import format_response
from models.movie import Movie
import json

def recommend_movie_and_speak(event, context):
    request_data = json.loads(event['body'])

    recommendation_message = Movie.get_recommendation_message()
    response = format_response(request_data, recommendation_message)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }