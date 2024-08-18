from datetime import datetime
from pydantic import BaseModel, PrivateAttr, SecretStr
from typing import Callable

class TraktConfig(BaseModel):
    _update_func: Callable = PrivateAttr()
    client_id: str
    client_secret: SecretStr
    oauth_token: SecretStr
    oauth_refresh_token: SecretStr
    oauth_expiry_date: int

    def __init__(self, **data):
        super().__init__(**data)
        self._update_func = data.get('update_func')

    def update(self) -> None:
        self._update_func(TraktOauthToken = self.oauth_token, 
             TraktOauthRefreshToken = self.oauth_refresh_token, 
             TraktOauthExpiryDate = self.oauth_expiry_date)


class PlexConfig(BaseModel):
    _update_func: Callable = PrivateAttr()
    username: SecretStr
    password: SecretStr
    server_name: str

    def __init__(self, **data):
        super().__init__(**data)
        self._update_func = data.get('update_func')

    def update(self) -> None:
        pass


class AlexaConfig(BaseModel):
    _update_func: Callable = PrivateAttr()
    skill_id: str

    def __init__(self, **data):
        super().__init__(**data)
        self._update_func = data.get('update_func')

    def update(self) -> None:
        pass