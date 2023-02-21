from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer

class PlexService:
    def __init__(self, token: str, server_name: str):
        self.token = token
        self.server_name = server_name

    def authenticate(self, username: str, password: str, tfa_code: str):
        account: MyPlexAccount = MyPlexAccount(username = username, password = password, code = tfa_code)
        plex_server: PlexServer = account.resource(self.server_name).connect(ssl = True)
        self.token = plex_server._token

    def test_connection(self, token, server_name):
        account: MyPlexAccount = MyPlexAccount(token = token)
        account.resource(server_name).connect(ssl = True)