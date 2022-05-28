import logging

_logger = logging.getLogger(__name__)

def format_google_actions_response(request_data: dict, message: str):
    response = {}
    response['session'] = {}
    response['session']['id'] = request_data['session']['id']
    response['session']['params'] = request_data['session']['params']
    response['prompt'] = {}
    response['prompt']['override'] = False
    response['prompt']['firstSimple'] = {}
    response['prompt']['firstSimple']['speech'] = message
    response['prompt']['firstSimple']['text'] = message
    return response