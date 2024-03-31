
from dataclasses import dataclass


@dataclass
class SpotifyAuth:
    client_id: str
    client_secret: str
    scope: str
    redirect_uri: str
