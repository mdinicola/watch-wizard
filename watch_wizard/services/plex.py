from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import logging

_logger = logging.getLogger(__name__)

class PlexService:
    def __init__(self, config: dict):
        self._username = config.get('username')
        self._password = config.get('password')
        self._server_name = config.get('server_name')
        self.account = None
        self.server = None

    def connect(self):
        if self.account:
            return
        self.account : MyPlexAccount = MyPlexAccount(self._username, self._password)
        self.server: PlexServer = self.account.resource(self._server_name).connect(ssl = True)

    def test_connection(self):
        try:
            self.connect()
            if self.server and self.server._token:
                return True
        except Exception as e:
            _logger.error(e)
        return False