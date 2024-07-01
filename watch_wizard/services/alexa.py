from services.config import AlexaConfig
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from ask_sdk_core.skill_builder import SkillBuilder
import os
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

class AlexaService:
    def __init__(self, config: AlexaConfig) -> None:
        self._config = config
        self._skill_builder = SkillBuilder()
        self._skill_builder.skill_id = config.skill_id

    def add_request_handlers(self, handlers) -> None:
        for handler in handlers:
            self._skill_builder.add_request_handler(handler)

    def add_exception_handler(self, handler) -> None:
        self._skill_builder.add_exception_handler(handler)

    def get_lambda_handler(self):
        return self._skill_builder.lambda_handler()

    def get_webservice_handler(self) -> WebserviceSkillHandler:
        # skip verification if testing locally
        if os.environ.get('AWS_SAM_LOCAL') == 'true':
            return WebserviceSkillHandler(skill=self._skill_builder.create(), verify_signature=False, verify_timestamp=False)
        else:
            return WebserviceSkillHandler(skill=self._skill_builder.create())