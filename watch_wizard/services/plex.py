from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.video import Video as PlexVideo
from plexapi.media import Availability as PlexAvailability
from models import Availability
from utils import distinct
from typing import List
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

class PlexService:
    def __init__(self, config: dict) -> None:
        self._username = config.get('username')
        self._password = config.get('password')
        self._server_name = config.get('server_name')
        self.account = None
        self.server = None

    def connect(self) -> None:
        if self.account:
            return
        self.account = MyPlexAccount(self._username, self._password)
        self.server: PlexServer = self.account.resource(self._server_name).connect(ssl = True)

    def test_connection(self) -> bool:
        try:
            self.connect()
            if self.server and self.server._token:
                return True
        except Exception as e:
            _logger.error(e)
        return False
    
    def search_media(self, query: str, media_type: str, limit: int = 1) -> List[PlexVideo]:
        self.connect()
        results: List[PlexVideo] = self.account.searchDiscover(query, limit, media_type)
        return results

    def get_plex_availability(self, media: PlexVideo) -> Availability:
        plex_results = self.server.search(f'{media.title}')
        if plex_results:
            return Availability({
                'platform': 'plex',
                'title': 'Plex'
            })
        return None
    
    def get_media_availability(self, media: PlexVideo) -> List[Availability]:
        self.connect()
        availability: List[Availability] = []

        # Check if media is available in Plex library
        plex_availability = self.get_plex_availability((media))
        if plex_availability:
            availability.append(plex_availability)

        # Check if media is available on any streaming services
        streaming_services: List[PlexAvailability] = media.streamingServices()
        if (len(streaming_services) > 0):
            subscription_streaming_services: List[PlexAvailability] = list(filter(lambda x: x.offerType == "subscription", streaming_services))
            distinct_streaming_services = distinct(subscription_streaming_services, 'platform')
            subscription_availability: List[Availability] = list(map(Availability.from_plex, distinct_streaming_services))
            availability.extend(subscription_availability)

        return availability
        