from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parameters import SecretsProvider
from pydantic import BaseModel, PrivateAttr

_logger = Logger()


class Secret(BaseModel):
    name: str
    _provider: SecretsProvider = PrivateAttr()
    _values: dict = PrivateAttr()

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self._provider = None
        self._values = None

    def set_provider(self, provider: SecretsProvider):
        self._provider = provider

    def _fetch_secret(self):
        try:
            self._values = self._provider.get(name=self.name, transform='json')
            return self._values
        except Exception:
            _logger.error(f'Error getting secret "{self.name}"')
            raise

    def get_value(self, key, default_value=None):
        if self._values is None:
            self._fetch_secret()

        try:
            return self._values.get(key, default_value)
        except Exception:
            _logger.error(f'Error getting secret value for "{key}"')
            raise

    def set_values(self, **kwargs):
        if self._values is None:
            self._fetch_secret()
        try:
            for key, value in kwargs.items():
                self._values[key] = value
            self._provider.set(name=self.name, value=self._values)
        except Exception:
            _logger.error(f'Error setting secret values for "{self.name}"')
            raise
