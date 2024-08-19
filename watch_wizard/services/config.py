from aws_lambda_powertools import Logger
from services.aws_secrets_manager import SecretsManagerService
from models.secret import Secret
from models.config import TraktConfig, PlexConfig, AlexaConfig
import os

_logger = Logger()

_CONFIG_SECRET_NAME_KEY = 'ServiceSecretName'


class ConfigService:
    def __init__(self) -> None:
        secrets_manager_service = SecretsManagerService()
        config_secret: Secret = secrets_manager_service.get_secret(secret_name=os.environ[_CONFIG_SECRET_NAME_KEY])

        self.trakt_config = TraktConfig(
            client_id=config_secret.get_value('TraktClientId'),
            client_secret=config_secret.get_value('TraktClientSecret'),
            oauth_token=config_secret.get_value('TraktOauthToken'),
            oauth_refresh_token=config_secret.get_value('TraktOauthRefreshToken'),
            oauth_expiry_date=config_secret.get_value('TraktOauthExpiryDate'),
            update_func=config_secret.set_values
        )

        self.plex_config = PlexConfig(
            username=config_secret.get_value('PlexUsername'),
            password=config_secret.get_value('PlexPassword'),
            server_name=config_secret.get_value('PlexServerName'),
            update_func=config_secret.set_values
        )

        self.alexa_config = AlexaConfig(
            skill_id=config_secret.get_value('AlexaSkillId'),
            update_func=config_secret.set_values
        )

    def to_json(self) -> dict:
        return {
            'trakt_config': self.trakt_config,
            'plex_config': self.plex_config,
            'alexa_config': self.alexa_config
        }
