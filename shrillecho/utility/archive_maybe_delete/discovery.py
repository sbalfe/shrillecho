import re

import spotipy
from pymongo import MongoClient

import shrillecho.utility.archive_maybe_delete.spotify_client as sp_client
import shrillecho.utility.archive_maybe_delete.general as general

from shrillecho.utility.archive_maybe_delete.cache import Cache
from shrillecho.utility.archive_maybe_delete.playlist import Playlist
from shrillecho.types.playlist_types import Playlist as Playlist_t

database = "shrillecho-app"
collection = "cache"

client = MongoClient("mongodb://localhost:27017/")
db = client[database]
collection = db[collection]  



class EveryNoiseSeed:
    __track_uri_regex = r'trackid="([\w]+)"'
    __every_noise_radio_url = 'https://everynoise.com/research.cgi?mode=radio&name=spotify:track'

    def __init__(self, sp: spotipy.Spotify, client: sp_client.SpotifyClient, driver, seed_track: str):
        self.__active_pl = None
        general.log("Setting up every noise seed")
        self.new_isrcs = None
        self.__driver = driver
        self.__seed_track = seed_track
        self.__track_name = ''
        self.__track_artist = ''
        self.__filtered_isrcs = set()
        self.__sp = sp
        self.client = client
        self.__cache = Cache('track_isrcs',  self.__cache_reader, self.__cache_writer)
        self.__fetch_track_data()
        self.__fetched_isrcs = set()

    def __cache_writer(self, cache, *args):
        playlist_uri = args[0]
        pl: Playlist_t = Playlist(self.__sp, Playlist_t(playlist_uri))
        self.__fetched_isrcs = pl.get_all_isrcs()
        for isrc in self.__fetched_isrcs:
            cache.write(f'{isrc[0]},{isrc[1]}\n')

    def __cache_reader(self, cache):
        for isrc in cache:
            try:
                print(isrc)
                values = isrc.split(',')
                self.__fetched_isrcs.add((values[0], values[1]))
            except:
                print("failed")

    def __fetch_track_data(self):
        track_data = self.__sp.track(self.__seed_track)
        self.__track_name = track_data['name']
        self.__track_artist = track_data['artists'][0]['name']

    def __scrape(self):
        url = f'{self.__every_noise_radio_url}:{self.__seed_track}'
        self.__driver.get(url)
        matches = set(re.findall(self.__track_uri_regex, self.__driver.page_source))
        tracks = set()
        for match in matches:
            tracks.add(match) # adds the uris

        return general.convert_uris_to_isrcs(tracks, self.client)

    # Todo make it accept a list of playlists
    def filter_playlists(self, playlists: list[str]):
        for playlist_uri in playlists:

            if self.__cache.fetch(f'{playlist_uri}_isrc.txt', playlist_uri):
                print("cache hit, reading")
            else:
                print("cache miss, writing")

            self.__filtered_isrcs.update(self.__fetched_isrcs)

    def write_playlist(self, scrape_depth=2):

        # Collect 10 iterations of every noise
        scraped_tracks = set()
        for i in range(0, scrape_depth):
            scraped_tracks.update(self.__scrape())

        # Remove the isrcs we do not want to see
        scraped_tracks.difference_update(self.__filtered_isrcs)

        # # Convert the isrc back
        # tracks_u = general.convert_isrcs_to_uris(self.__sp, scraped_isrcs)
        general.write_songs_to_playlist(self.__sp, f'EN seed: {self.__track_name} - {self.__track_artist}')
