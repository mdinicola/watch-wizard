from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.video import Video, Movie, Show
from utils import distinct
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
    
    def search_media(self, query: str, media_type: str, limit: int = 1):
        self.connect()
        results = self.account.searchDiscover(query, limit, media_type)
        return results

    def get_availability(self, media: Video):
        self.connect()
        streaming_services = media.streamingServices()
        if (len(streaming_services) == 0):
            return []
        subscription_streaming_services = list(filter(lambda x: x.offerType == "subscription", streaming_services))
        return distinct(subscription_streaming_services, 'platform')
        