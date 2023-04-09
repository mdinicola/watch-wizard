from dataclasses import dataclass
from trakt.utils import slugify


class Movie:
    def __init__(self, data: dict) -> None:
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

    def get_availability(self, media_service) -> None:
        results = media_service.search(f'{self.title} + ({self.year})', 'movie', 1)
        if results:
            self.availability = results[0].availability

    def recommendation_message(self) -> str:
        message = f'You should watch: {self.title} ({self.year}).  {self.availability_message()}'
        return message
    
    def availability_message(self) -> str:
        message = ''
        if self.availability:
            message += f'It is available on: {", ".join(x.title for x in self.availability)}'
        else:
            message += 'It is not available in your library or on any streaming services'
        return message

class Availability:
    def __init__(self, data: dict) -> None:
        self.platform = data.get('platform')
        self.title = data.get('title')

    @classmethod
    def from_plex(cls, plex_availability):
        data = {
            'platform': plex_availability.platform,
            'title': plex_availability.title
        }
        return cls(data)
    
@dataclass
class DeviceAuthData:
    user_code: str
    device_code: str
    verification_url: str
    poll_interval: int