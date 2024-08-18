from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters
from models.secret import Secret
import os
import boto3

_logger = Logger()

class SecretsManagerService:
    def __init__(self, provider = None):
        self._provider = provider
        if self._provider is None:
            secretsManagerEndpoint = os.environ.get('SecretsManagerEndpoint')
            if secretsManagerEndpoint != '':
                boto3_client = boto3.client('secretsmanager', endpoint_url = secretsManagerEndpoint)
            else:
                boto3_client = boto3.client('secretsmanager')
            self._provider = parameters.SecretsProvider(boto3_client = boto3_client)

    def get_secret(self, secret_name) -> Secret:
        secret = Secret(name = secret_name)
        secret.set_provider(self._provider)
        return secret

