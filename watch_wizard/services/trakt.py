from trakt import core
from trakt import movies as trakt_movies
from services.movies import Movie
from dataclasses import dataclass
import logging
import time
import random

_logger = logging.getLogger(__name__)

@dataclass
class DeviceAuthData:
    user_code: str
    device_code: str
    verification_url: str
    poll_interval: int

class TraktService:
    def __init__(self, aws_secret_name, aws_secrets_manager_endpoint = ''):
        core.CONFIG_TYPE = 'AWS_SECRETS_MANAGER'
        core.CONFIG_SECRET_NAME = aws_secret_name
        if aws_secrets_manager_endpoint != '':
            core.AWS_SECRETS_MANAGER_ENDPOINT = aws_secrets_manager_endpoint
        core.load_config()

    @staticmethod
    def get_auth_code(client_id: str, client_secret: str):
        response = core.get_device_code(client_id = client_id, client_secret = client_secret)
        device_auth_data = DeviceAuthData(user_code = response['user_code'], device_code = response['device_code'], 
            verification_url = response['verification_url'], poll_interval = response['interval'])

        return {
            'device_auth_data': device_auth_data
        }

    @staticmethod
    def authenticate_device(device_code: str, poll_interval: int, aws_secret_name: str, aws_secrets_manager_endpoint = ''):

        core.CONFIG_TYPE = 'AWS_SECRETS_MANAGER'
        core.CONFIG_SECRET_NAME = aws_secret_name
        if aws_secrets_manager_endpoint != '':
            core.AWS_SECRETS_MANAGER_ENDPOINT = aws_secrets_manager_endpoint
        
        core.load_config()

        success_message = "You've been successfully authenticated."

        error_messages = {
            404: 'Invalid device_code',
            409: 'You already approved this code',
            410: 'The tokens have expired, restart the process',
            418: 'You explicitly denied this code',
        }

        response = {
            'message': 'Something went wrong.  Please try again',
            'status_code': 500
        }

        while True:
            auth_response = core.get_device_token(device_code = device_code, 
                client_id = core.CLIENT_ID, client_secret = core.CLIENT_SECRET, store = True)

            if auth_response.status_code == 200:
                response['message'] = success_message
                response['status_code'] = 200
                break

            elif auth_response.status_code == 429:  # slow down
                poll_interval *= 2

            elif auth_response.status_code != 400:  # not pending
                response['message'] = error_messages.get(auth_response.status_code, auth_response.reason)
                response['status_code'] = auth_response.status_code
                break

            time.sleep(poll_interval)

        return response

    def get_recommended_movie(self):
        trakt_movie = random.choice(trakt_movies.get_recommended_movies())
        return Movie.from_trakt(trakt_movie)