from trakt.utils import slugify
from services.trakt import TraktService
from services.plex import PlexService

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
            availability = list(map(Availability.from_plex, self.plex_service.get_availability(media)))
            availability = list(filter(lambda x: x.platform not in platform_exclusions, availability))
            movie = Movie.from_plex(media)
            movie.availability = availability
            media_list.append(movie)
        return media_list
    
    def get_availability(self, media, media_type):
        results = self.search(f'{media.title} + ({media.year})', media_type, 1)
        if results:
            media.availability = results[0].availability

class Movie:
    def __init__(self, data: dict):
        self.title = data.get('title')
        self.year = data.get('year')
        self.imdb_id = data.get('imdb_id', None)
        self.trakt_id = data.get('trakt_id', None)
        self.plex_id = data.get('plex_id', None)
        self.availability = data.get('availability', [])
        slug = data.get('slug', None)
        if slug is not None:
            self.slug = slug
        else:
            self.slug = slugify('-'.join([self.title, str(self.year)]))

    @classmethod
    def from_trakt(cls, trakt_movie):
        data = {
            'title': trakt_movie.title,
            'year': trakt_movie.year,
            'imdb_id': trakt_movie.imdb,
            'trakt_id': trakt_movie.trakt,
            'slug': trakt_movie.slug
        }
        return cls(data)

    @classmethod
    def from_plex(cls, plex_movie):
        data = {
            'title': plex_movie.title,
            'year': plex_movie.year,
            'plex_id': plex_movie.guid
        }
        return cls(data)

    def get_availability(self, media_service: MediaService):
        results = media_service.search(f'{self.title} + ({self.year})', 'movie', 1)
        if results:
            self.availability = results[0].availability

    def recommendation_message(self):
        message = f'You should watch: {self.title} ({self.year}).  {self.availability_message()}'
        return message
    
    def availability_message(self):
        message = ''
        if self.availability:
            message += f'It is available on: {", ".join(x.title for x in self.availability)}'
        else:
            message += 'It is not available in your library or on any streaming services'
        return message

class Availability:
    def __init__(self, data: dict):
        self.platform = data.get('platform')
        self.title = data.get('title')

    @classmethod
    def from_plex(cls, plex_availability):
        data = {
            'platform': plex_availability.platform,
            'title': plex_availability.title
        }
        return cls(data)


