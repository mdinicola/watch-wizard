from services.trakt import TraktService
from services.plex import PlexService
from plexapi.video import Video as PlexVideo
from models import Movie, Availability
from typing import List

class MediaService:
    def __init__(self, trakt_config: dict, plex_config: dict, secrets_manager_endpoint: str) -> None:
        self.trakt_service = TraktService(trakt_config.get('secret_name'), secrets_manager_endpoint)
        self.plex_service = PlexService(plex_config)

    def recommend_movie(self) -> Movie:
        trakt_movie = self.trakt_service.get_recommended_movie()
        movie: Movie = Movie.from_trakt(trakt_movie)
        movie.get_availability(movie)
        return movie
    
    def search(self, query: str, media_type: str, limit: int) -> List[Movie]:
        results: List[PlexVideo] = self.plex_service.search_media(query, media_type, limit)
        media_list: List[Movie] = []
        if (len(results) == 0):
            return media_list

        platform_exclusions = ['netflix-basic-with-ads']
        for media in results:
            availability_list: List[Availability] = self.plex_service.get_availability(media)
            availability: List[Availability] = list(filter(lambda x: x.platform not in platform_exclusions, availability_list))
            movie: Movie = Movie.from_plex(media)
            movie.availability = availability
            media_list.append(movie)
        return media_list
    
    def get_availability(self, media: Movie) -> None:
        results: List[Movie] = self.search(f'{media.title} + ({media.year})', 1)
        if results:
            media.availability = results[0].availability


