from handlers.alexa import alexa_service
import json
import logging

_logger = logging.getLogger(__name__)
  
def handle_skill_request(event, context):
    handler = alexa_service().get_webservice_handler()
    response = handler.verify_request_and_dispatch(event['headers'], event['body'])
   
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }