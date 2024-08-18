from datetime import datetime
from pydantic import BaseModel, PrivateAttr
from typing import Callable

class TraktConfig(BaseModel):
    _update_func: Callable = PrivateAttr()
    client_id: str
    client_secret: str
    oauth_token: str
    oauth_refresh_token: str
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
    username: str
    password: str
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