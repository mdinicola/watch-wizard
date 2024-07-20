from aws_lambda_powertools import Logger
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.video import Video as PlexVideo
from plexapi.media import Availability as PlexAvailability
from models.media import Availability
from services.config import PlexConfig
from utils import distinct

_logger = Logger()

class PlexService:
    def __init__(self, config: PlexConfig) -> None:
        self._config = config
        self.account = None
        self.server = None

    def connect(self) -> None:
        if self.account:
            return
        self.account = MyPlexAccount(self._config.username, self._config.password)
        self.server: PlexServer = self.account.resource(self._config.server_name).connect(ssl = True)

    def test_connection(self) -> bool:
        try:
            self.connect()
            if self.server and self.server._token:
                return True
        except Exception as e:
            _logger.error(e)
        return False
    
    def search_media(self, query: str, media_type: str, limit: int = 1) -> list[PlexVideo]:
        self.connect()
        results: list[PlexVideo] = self.account.searchDiscover(query, limit, media_type)
        return results

    def get_plex_availability(self, media: PlexVideo) -> Availability:
        plex_results = self.server.search(f'{media.title}')
        if plex_results:
            return Availability({
                'platform': 'plex',
                'title': 'Plex'
            })
        return None
    
    def get_media_availability(self, media: PlexVideo) -> list[Availability]:
        self.connect()
        availability: list[Availability] = []

        # Check if media is available in Plex library
        plex_availability = self.get_plex_availability((media))
        if plex_availability:
            availability.append(plex_availability)

        # Check if media is available on any streaming services
        streaming_services: list[PlexAvailability] = media.streamingServices()
        if (len(streaming_services) > 0):
            subscription_streaming_services: list[PlexAvailability] = list(filter(lambda x: x.offerType == "subscription", streaming_services))
            distinct_streaming_services = distinct(subscription_streaming_services, 'platform')
            subscription_availability: list[Availability] = list(map(Availability.from_plex, distinct_streaming_services))
            availability.extend(subscription_availability)

        return availability
        