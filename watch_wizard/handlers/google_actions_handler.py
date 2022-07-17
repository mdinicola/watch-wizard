from clients.google_actions import format_response
from models.movie import Movie
import json

def handle_response(event, context):
    request_data = json.loads(event['body'])
    handler_name = request_data['handler']['name']
    
    if handler_name == 'recommend_movie':
        return recommend_movie(request_data)
    else:
        message = f'Handler name {handler_name} is not valid'
        return {
            'statusCode': 400,
            'body': json.dumps(message)
        }

def recommend_movie(request_data):
    recommendation_message = Movie.get_recommendation_message()
    response = format_response(request_data, recommendation_message)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }