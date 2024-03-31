import spotipy

class SpotifyPlayer:

    @staticmethod
    def play_track(sp: spotipy.Spotify, uri: str):

        """
            Play a specific uri on the first device ID listed.
        """

        uri = f'spotify:track:{uri}'

        device_id = sp.devices()['devices'][0]['id']
        sp.start_playback(device_id=device_id, uris=[uri])