from trakt import core
from trakt import movies as TraktMovies
from models import DeviceAuthData
from services.config import TraktConfig
import logging
import time
import random

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

class TraktService:
    def __init__(self, config: TraktConfig) -> None:
        self._config: TraktConfig = config          
        self._validate_config() 
        core.CLIENT_ID = config.client_id
        core.CLIENT_SECRET = config.client_secret
        core.OAUTH_AUTH = config.oauth_token
        core.OAUTH_REFRESH = config.oauth_refresh_token
        core.OAUTH_EXPIRES_AT = config.oauth_expiry_date

    def _validate_config(self) -> None:
        if self._config.client_id is None or self._config.client_secret is None:
            raise TypeError('Trakt configuration is invalid or not set')


    def get_auth_code(self) -> dict:
        response = core.get_device_code(client_id = self._config.client_id, client_secret = self._config.client_secret)
        device_auth_data = DeviceAuthData(user_code = response['user_code'], device_code = response['device_code'], 
            verification_url = response['verification_url'], poll_interval = response['interval'])

        return {
            'device_auth_data': device_auth_data
        }

    def authenticate_device(device_code: str, poll_interval: int) -> dict:
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
                client_id = self._config.client_id, client_secret = self._config.client_secret, store = True)

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
        return random.choice(TraktMovies.get_recommended_movies())
