from aws_lambda_powertools import Logger
from trakt import core
from trakt import movies as TraktMovies
from trakt import users
from models.trakt import DeviceAuthData
from services.config import TraktConfig
import logging
import time
import random

_logger = Logger()

class TraktService:
    def __init__(self, config: TraktConfig) -> None:
        self._config: TraktConfig = config          
        self._validate_config() 

    def _validate_config(self) -> None:
        if self._config.client_id is None or self._config.client_secret is None:
            raise TypeError('Trakt configuration is invalid or not set')


    def _update_config(self, oauth_expiry_date = None) -> None:
        if core.OAUTH_TOKEN != self._config.oauth_token or core.OAUTH_REFRESH != self._config.oauth_refresh_token:
            self._config.oauth_token = core.OAUTH_TOKEN
            self._config.oauth_refresh_token = core.OAUTH_REFRESH
            if oauth_expiry_date is None:
                self._config.oauth_expiry_date = core.OAUTH_EXPIRES_AT
            else:
                self._config.oauth_expiry_date = oauth_expiry_date
            self._config.update()

    def get_auth_code(self) -> dict:
        response = core.get_device_code(client_id = self._config.client_id, client_secret = self._config.client_secret)
        device_auth_data = DeviceAuthData(user_code = response['user_code'], device_code = response['device_code'], 
            verification_url = response['verification_url'], poll_interval = response['interval'])

        return {
            'device_auth_data': device_auth_data
        }

    def authenticate_device(self, device_auth_data: DeviceAuthData) -> dict:
        poll_interval = device_auth_data.poll_interval
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
            auth_response = core.get_device_token(device_code = device_auth_data.device_code, 
                client_id = self._config.client_id, client_secret = self._config.client_secret)

            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                oauth_expiry_date = auth_data.get("created_at") + auth_data.get("expires_in")
                self._update_config(oauth_expiry_date)
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

    def connect(self):
        if core.CLIENT_ID is None:
            core.CLIENT_ID = self._config.client_id
            core.CLIENT_SECRET = self._config.client_secret
            core.OAUTH_TOKEN = self._config.oauth_token
            core.OAUTH_REFRESH = self._config.oauth_refresh_token
            core.OAUTH_EXPIRES_AT = self._config.oauth_expiry_date
        users.get_user_settings()
        self._update_config()

    def test_connection(self) -> bool:
        try:
            self.connect()
            return True
        except Exception as e:
            _logger.error(e)
            return False

    def get_recommended_movie(self):
        self.connect()
        return random.choice(TraktMovies.get_recommended_movies())
