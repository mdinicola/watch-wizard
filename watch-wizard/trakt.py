from secretsmanager import SecretsManagerSecret
import json
import boto3

def lambda_handler(event, context):
    SERVICE_NAME = 'WatchWizard'
    SECRET_NAME = f'apps/{SERVICE_NAME}'
    TRAKT_CLIENT_ID_KEY = 'TraktClientId'
    TRAKT_CLIENT_SECRET_KEY = 'TraktClientSecret'

    secret = SecretsManagerSecret(boto3.client('secretsmanager'), SECRET_NAME)
    trakt_client_id = secret.get_value(TRAKT_CLIENT_ID_KEY)
    trakt_client_secret = secret.get_value(TRAKT_CLIENT_SECRET_KEY)

    response = {
        "CLIENT_ID": trakt_client_id,
        "CLIENT_SECRET": trakt_client_secret
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }
