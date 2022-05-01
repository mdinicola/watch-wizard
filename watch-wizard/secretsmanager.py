import json
import logging

class SecretsManagerSecret:
    _logger = logging.getLogger(__name__)

    def __init__(self, client, logger, secret_name):
        self._client = client
        self.secret_name = secret_name
        self._logger = logger
        self._secret = None

    def _get_secret(self):
        if self.secret_name is None:
            raise ValueError

        try:
            data = { 'SecretId': self.secret_name }
            response = self._client.get_secret_value(**data)
            if 'SecretString' in response:
                self._secret = json.loads(response.get('SecretString'))
            else:
                self._logger.exception(f'Missing SecretString in secret {self.secret_name}')
                raise KeyError
        except Exception as e:
            self._logger.exception(f'Could not get secret value for {self.secret_name} with error {e}')
            raise

    def get_value(self, key):
        if self._secret is None:
            self._get_secret()
        
        if key not in self._secret:
            self._logger.exception(f'Could not find key {key} in secret {self.secret_name}')
            raise KeyError
        return self._secret.get(key)

    def put_values(self, **kwargs):
        if self._secret is None:
            self._get_secret()
        try:
            for key, value in kwargs.items():
                self._secret[key] = value
            data = { 'SecretId': self.secret_name, 'SecretString': json.dumps(self._secret) }
            response = self._client.put_secret_value(**data)
            self._logger.info(f'Successfully updated secret {response["Name"]}.  New version id is {response["VersionId"]}')
        except Exception as e:
            self._logger.exception(f'Could not get secret value for {self.secret_name} with error {e}')
            raise

