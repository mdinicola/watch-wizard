from trakt.utils import slugify
from handlers.trakt_handler import get_recommended_movie

class Movie:
    def __init__(self, title, year, imdb_id = None, trakt_id = None, slug = None):
        self.title = title
        self.year = year
        self.imdb_id = imdb_id
        self.trakt_id = trakt_id
        if slug is not None:
            self.slug = slug
        else:
            self.slug = slugify('-'.join([title, str(year)]))

    @classmethod
    def from_trakt_movie(cls, trakt_movie):
        return cls(title=trakt_movie.title, year=trakt_movie.year, imdb_id=trakt_movie.imdb, trakt_id=trakt_movie.trakt, slug=trakt_movie.slug)

    @staticmethod
    def get_recommendation():
        movie = get_recommended_movie()
        return Movie.from_trakt_movie(movie)

    @staticmethod
    def get_recommendation_message():
        movie = Movie.get_recommendation()
        return f'You should watch {movie.title} ({movie.year})'

