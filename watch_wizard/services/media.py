from aws_lambda_powertools import Logger
from services.trakt import TraktService
from services.plex import PlexService
from plexapi.video import Video as PlexVideo
from models.media import Movie, Availability

_logger = Logger()


class MediaService:
    def __init__(self, trakt_service: TraktService, plex_service: PlexService) -> None:
        self._trakt_service = trakt_service
        self._plex_service = plex_service

    def recommend_movie(self) -> Movie:
        trakt_movie = self._trakt_service.get_recommended_movie()
        movie: Movie = Movie.from_trakt(trakt_movie)
        movie.get_availability(self)
        return movie

    def search(self, query: str, media_type: str, limit: int) -> list[Movie]:
        results: list[PlexVideo] = self._plex_service.search_media(query, media_type, limit)
        media_list: list[Movie] = []
        if (len(results) == 0):
            return media_list

        platform_exclusions = ['netflix-basic-with-ads', 'amazon-prime-video-with-ads']
        for media in results[:limit]:
            availability_list: list[Availability] = self._plex_service.get_media_availability(media)
            availability: list[Availability] = list(filter(lambda x: x.platform not in platform_exclusions, availability_list))
            movie: Movie = Movie.from_plex(media)
            movie.availability = availability
            media_list.append(movie)
        return media_list

    def get_media_availability(self, media: Movie) -> None:
        results: list[Movie] = self.search(f'{media.title} + ({media.year})', 1)
        if results:
            media.availability = results[0].availability
