from services.trakt import TraktService
from services.plex import PlexService
from models import Movie
from models import Availability

class MediaService:
    def __init__(self, trakt_config: dict, plex_config: dict, secrets_manager_endpoint: str):
        self.trakt_service = TraktService(trakt_config.get('secret_name'), secrets_manager_endpoint)
        self.plex_service = PlexService(plex_config)

    def recommend_movie(self):
        trakt_movie = self.trakt_service.get_recommended_movie()
        movie = Movie.from_trakt(trakt_movie)
        movie.get_availability(self)
        return movie
    
    def search(self, query: str, media_type: str, limit: int):
        results = self.plex_service.search_media(query, media_type, limit)
        media_list = []
        if (len(results) == 0):
            return media_list

        platform_exclusions = ['netflix-basic-with-ads']
        for media in results:
            availability_list = list(map(Availability.from_plex, self.plex_service.get_availability(media)))
            availability = list(filter(lambda x: x.platform not in platform_exclusions, availability_list))
            movie = Movie.from_plex(media)
            movie.availability = availability
            media_list.append(movie)
        return media_list
    
    def get_availability(self, media, media_type):
        results = self.search(f'{media.title} + ({media.year})', media_type, 1)
        if results:
            media.availability = results[0].availability


