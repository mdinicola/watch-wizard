import random
import json
from plexapi.media import Availability
from plexapi.video import Movie, Show
from plexapi.server import PlexServer

def distinct(sequence):
    seen = set()
    for s in sequence:
        if not s.platform in seen:
            seen.add(s.platform)
            yield s
    return seen


#baseurl = 'https://192-168-50-156.041fe5099047488aa91c8e5a892c9e63.plex.direct:32400'
#baseurl = 'https://162-218-124-125.041fe5099047488aa91c8e5a892c9e63.plex.direct:55324'
#token = 'fp31xDfSt6Gw3vDQS8s3'
# my_plex = MyPlexAccount('wakkito123@gmail.com', '9^oqwZqlnI44')
#plex = PlexServer(baseurl, token)
#my_plex = plex.myPlexAccount()

movies = my_plex.searchDiscover('Your Place or Mine', 1, 'movie')
movie: Movie = movies[0] if movies else None
print(movie.title + ' ' + str(movie.year) + ' ')
streaming_services = movie.streamingServices()
subscription_streaming_services = list(filter(lambda x: x.offerType == "subscription", streaming_services))
for x in subscription_streaming_services:
    print(x.platform)
for x in distinct(subscription_streaming_services):
    print(x.title + ' ' + x.quality + ' ' + x.offerType)

# def lambda_handler(event, context):
#     baseurl = 'https://192-168-50-177.3cc185390cc84758879eb49396024277.plex.direct:32400'
#     token = '1pyD_LZYNzA2daKMhhKp'
#     plex = PlexServer(baseurl, token)

#     #movies_4k_library = plex.library.section('Movies 4k')
#     #movies_1080p_library = plex.library.section('Movies')

#     #movies_4k = movies_4k_library.search(None, genre='Comedy', unwatched=True)
#     #movies_1080p = movies_1080p_library.search(None, genre='Comedy', unwatched=True)

#     movies = list(set(movies_4k) - set(movies_1080p))

#     # for movie in movies:
#     #     print(movie.title)

#     movie = random.choice(movies)
#     print(movie.title)

#     return {
#         "statusCode": 200,
#         "body": json.dumps(case_data, cls=CaseInfoEncoder)
#     }


# import random

# # from plexapi.myplex import MyPlexAccount
# # account = MyPlexAccount('m4cola', '9^oqwZqlnI44')
# # plex = account.resource('MIKE-PC').connect()  # returns a PlexServer instance

# # print(plex._baseurl)
# # print(plex._token)

# from plexapi.server import PlexServer
# baseurl = 'https://192-168-50-177.3cc185390cc84758879eb49396024277.plex.direct:32400'
# token = '1pyD_LZYNzA2daKMhhKp'
# plex = PlexServer(baseurl, token)

# movies_4k_library = plex.library.section('Movies 4k')
# movies_1080p_library = plex.library.section('Movies')

# movies_4k = movies_4k_library.search(None, genre='Comedy', unwatched=True)
# movies_1080p = movies_1080p_library.search(None, genre='Comedy', unwatched=True)

# movies = list(set(movies_4k) - set(movies_1080p))

# # for movie in movies:
# #     print(movie.title)

# movie = random.choice(movies)
# print(movie.title)

# # List genres
# # library = plex.library.section('TV Shows')
# # field = 'genre'  # Available filter field from listFilters()
# # availableChoices = [f.title for f in library.listFilterChoices(field)]
# # print("Available choices for %s:" % field, availableChoices)
