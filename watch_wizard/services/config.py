from services.aws_secrets_manager import SecretsManagerService, SecretsManagerSecret
import os
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_CONFIG_SECRET_NAME_KEY = 'ServiceSecretName'

class ConfigService:
    _secrets_manager_service = SecretsManagerService()

    def __init__(self) -> None:
        config_secret: SecretsManagerSecret = ConfigService._secrets_manager_service.get_secret(os.environ[_CONFIG_SECRET_NAME_KEY])

        self.trakt_config = TraktConfig(config_secret)
        self.plex_config = PlexConfig(config_secret)
        self.alexa_config = AlexaConfig(config_secret)

    def to_json(self) -> dict:
        return {
            'trakt_config': self.trakt_config,
            'plex_config': self.plex_config,
            'alexa_config': self.alexa_config
        }

class TraktConfig:
    def __init__(self, config_secret: SecretsManagerSecret) -> None:
        self._config_secret = config_secret            
        self.client_id = config_secret.get_value('TraktClientId')
        self.client_secret = config_secret.get_value('TraktClientSecret')
        self.oauth_token = config_secret.get_value('TraktOauthToken')
        self.oauth_refresh_token = config_secret.get_value('TraktOauthRefreshToken')
        self.oauth_expiry_date = config_secret.get_value('TraktOauthExpiryDate')

    def update(self) -> None:
        self._config_secret.put_values(TraktOauthToken = self.oauth_token, 
            TraktOauthRefreshToken = self.oauth_refresh_token, TraktOauthExpiryDate = self.oauth_expiry_date)

    def to_json(self) -> dict:
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'oauth_token': self.oauth_token,
            'oauth_refresh_token': self.oauth_refresh_token,
            'oauth_expiry_date': self.oauth_expiry_date
        }

class PlexConfig:
    def __init__(self, config_secret: SecretsManagerSecret) -> None:
        self._config_secret = config_secret
        self.username = config_secret.get_value('PlexUsername')
        self.password = config_secret.get_value('PlexPassword')
        self.server_name = config_secret.get_value('PlexServerName')

    def update(self) -> None:
        pass

    def to_json(self) -> dict:
        return {
            'username': self.username,
            'password': self.password,
            'server_name': self.server_name
        }

class AlexaConfig:
    def __init__(self, config_secret: SecretsManagerSecret) -> None:
        self._config_secret = config_secret
        self.skill_id = config_secret.get_value('AlexaSkillId')

    def update() -> None:
        pass

    def to_json(self) -> dict:
        return {
            'skill_id': self.skill_id
        }