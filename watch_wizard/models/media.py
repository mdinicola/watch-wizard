from pydantic import BaseModel
from typing import Optional
from trakt.utils import slugify

class Availability(BaseModel):
    platform: str
    title: str

    @classmethod
    def from_plex(cls, plex_availability):
        return cls(platform = plex_availability.platform, title = plex_availability.title)

class Movie(BaseModel):
    title: str
    year: Optional[str] = None
    imdb_id: Optional[str] = None
    trakt_id: Optional[str] = None
    plex_id: Optional[str] = None
    availability: Optional[list[Availability]] = []
    slug: Optional[str] = None

    def model_post_init(self, __context):
        if self.slug is None:
            self.slug = slugify('-'.join([self.title, str(self.year)]))

    @classmethod
    def from_trakt(cls, trakt_movie):
        return cls(title = trakt_movie.title,
            year = trakt_movie.year,
            imdb_id = trakt_movie.imdb,
            trakt_id = trakt_movie.trakt,
            slug = trakt_movie.slug)

    @classmethod
    def from_plex(cls, plex_movie):
        return cls(title = plex_movie.title,
            year = plex_movie.year,
            plex_id = plex_movie.guid)

    def get_availability(self, media_service) -> None:
        results = media_service.search(query = f'{self.title} + ({self.year})', media_type = 'movie', limit = 1)
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