from __future__ import annotations
from services.aws_secrets_manager import SecretsManagerService, SecretsManagerSecret
import os
import logging
import json

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_CONFIG_SECRET_NAME_KEY = 'ServiceSecretName'

class ConfigService:
    _secrets_manager_service = SecretsManagerService()

    def __init__(self, config: dict, trakt_config: TraktConfig, plex_config: PlexConfig, alexa_config: AlexaConfig) -> None:
            self.config = config
            self.trakt_config = trakt_config
            self.plex_config = plex_config
            self.alexa_config = alexa_config
            self.trakt_config._config_service = self.plex_config._config_service = self.alexa_config._config_service = self

    @classmethod
    def load_config(cls):
        config = {
             'secrets_manager_endpoint': ConfigService._secrets_manager_service.secrets_manager_endpoint
        }

        config_secret: SecretsManagerSecret = ConfigService._secrets_manager_service.get_secret(os.environ[_CONFIG_SECRET_NAME_KEY])

        trakt_config = TraktConfig(
            client_id = config_secret.get_value('TraktClientId'),
            client_secret = config_secret.get_value('TraktClientSecret'),
            oauth_token = config_secret.get_value('TraktOauthToken'),
            oauth_refresh_token = config_secret.get_value('TraktOauthRefreshToken'),
            oauth_expiry_date = config_secret.get_value('TraktOauthExpiryDate')
        )
        
        plex_config = PlexConfig(
             username = config_secret.get_value('PlexUsername'),
             password = config_secret.get_value('PlexPassword'),
             server_name = config_secret.get_value('PlexServerName')
        )
        
        alexa_config = AlexaConfig(
             skill_id = config_secret.get_value('AlexaSkillId')
        )
        return cls(config, trakt_config, plex_config, alexa_config)

    def update(self):
        pass

class TraktConfig:
    def __init__(self, client_id: str, client_secret: str, oauth_token: str = None, 
        oauth_refresh_token: str = None, oauth_expiry_date: str = None) -> None:
            self._config_service = None
            self.client_id = client_id
            self.client_secret = client_secret
            self.oauth_token = oauth_token
            self.oauth_refresh_token = oauth_refresh_token
            self.oauth_expiry_date = oauth_expiry_date

    def set_config_service(self, config_service: ConfigService) -> None:
        self._config_service = config_service

    def update(self) -> None:
        self._config_service.update_trakt_config

    def serialize(self) -> dict:
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'oauth_token': self.oauth_token,
            'oauth_refresh_token': self.oauth_refresh_token,
            'oauth_expiry_date': self.oauth_expiry_date
        }

class PlexConfig:
    def __init__(self, username: str, password: str, server_name: str) -> None:
            self._config_service = None
            self.username = username
            self.password = password
            self.server_name = server_name

    def set_config_service(self, config_service: ConfigService) -> None:
        self._config_service = config_service

    def update(self) -> None:
        self._config_service.update_plex_config

    def serialize(self) -> dict:
        return {
            'username': self.username,
            #'password': self.password,
            'server_name': self.server_name
        }

class AlexaConfig:
    def __init__(self, skill_id: str) -> None:
            self._config_service = None
            self.skill_id = skill_id

    def set_config_service(self, config_service: ConfigService) -> None:
        self._config_service = config_service

    def update() -> None:
        self._config_service.update_alexa_config

    def serialize(self) -> dict:
        return {
            'skill_id': self.skill_id
        }