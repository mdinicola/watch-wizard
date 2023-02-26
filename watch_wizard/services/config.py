from services.aws_secrets_manager import SecretsManagerService
import os
import logging

_logger = logging.getLogger(__name__)
_TRAKT_SECRET_NAME_KEY = 'TraktSecretName'
_APP_SECRET_NAME_KEY = 'ServiceSecretName'
_ALEXA_SKILL_ID_KEY = 'AlexaSkillId'

class ConfigService:
    _secrets_manager_service = SecretsManagerService()

    def __init__(self, config: dict, trakt_config: dict, plex_config: dict, alexa_config: dict):
            self.config = config
            self.trakt_config = trakt_config
            self.plex_config = plex_config
            self.alexa_config = alexa_config

    @classmethod
    def load_config(cls):
        config = {
             'secrets_manager_endpoint': ConfigService._secrets_manager_service.secrets_manager_endpoint
        }

        app_secret_name = os.environ[_APP_SECRET_NAME_KEY]
        app_secret = ConfigService._secrets_manager_service.get_secret(app_secret_name)

        trakt_secret_name = os.environ[_TRAKT_SECRET_NAME_KEY]
        trakt_secret = ConfigService._secrets_manager_service.get_secret(trakt_secret_name)
        trakt_config = {
            'secret_name': trakt_secret_name,
            'client_id': trakt_secret.get_value('CLIENT_ID'),
            'client_secret': trakt_secret.get_value('CLIENT_SECRET'),
            'oauth_token': trakt_secret.get_value('OAUTH_TOKEN'),
            'oauth_refresh': trakt_secret.get_value('OAUTH_REFRESH'),
            'oauth_expires_at': trakt_secret.get_value('OAUTH_EXPIRES_AT')
        }
        
        plex_config = {
             'username': app_secret.get_value('PlexUsername'),
             'password': app_secret.get_value('PlexPassword'),
             'server_name': app_secret.get_value('PlexServerName')
        }
        
        alexa_config = {
             'skill_id': os.environ[_ALEXA_SKILL_ID_KEY]
        }
        return cls(config, trakt_config, plex_config, alexa_config)