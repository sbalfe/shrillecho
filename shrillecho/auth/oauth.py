import spotipy
from spotipy import SpotifyOAuth
import os


def authenticate():
    client_id = str(os.environ.get("SPOTIPY_CLIENT_ID"))
    client_secret = str(os.environ.get("SPOTIPY_CLIENT_SECRET"))
    scope = os.environ.get("SCOPE")
    redirect_uri = os.environ.get("REDIRECT_URI")

    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id,
                                                     client_secret,
                                                     redirect_uri=redirect_uri,
                                                     scope=scope))
