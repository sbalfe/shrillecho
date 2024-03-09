""" This file will contain various features of shrillecho that are to be sorted into classes later """
from dataclasses import asdict

import spotipy
from shrillecho.playlist.playlist_engine import PlaylistEngine
from shrillecho.types.albums import ArtistAlbums, AlbumTracks, SimplifiedTrack, SeveralAlbums
from shrillecho.types.artists import Artist, SeveralArtists
from shrillecho.types.playlists import Playlist, PlaylistTrack, PlaylistTracks, SimplifiedPlaylistObject, UserPlaylist
from typing import List, Set
import json
from shrillecho.types.tracks import Track, SavedTrack, SavedTracks, SeveralTracks, Recc
from typing import Type, TypeVar, Callable, Any
from shrillecho.utility.general_utility import *
import httpx
import math
import asyncio
import time
from shrillecho.utility.async_spotify import *
from shrillecho.utility.mongo import Mongo
import re
import requests

""" Mongo Master Object """
mongo_client = Mongo('localhost', '27017', 'shrillecho')

""" Look at a users artists from a specific playlist, pick random songs from them """

"""
 Take a playlist, fetch all tracks from all artists on that playlist
"""

async def select_random_song_from_artists(sp: spotipy.Spotify, playlist_id: str) -> List[Track]:
    all_tracks: List[Track] = []

    artists = set()
    pl_engine = PlaylistEngine(sp)
    playlist_tracks: List[PlaylistTrack] = await fetch_async(sp, PlaylistTracks, playlist_id, chunk_size=50)

    unique_artists = set()
    for pl_track in playlist_tracks:

        main_artist = None
        if 'Remix' in pl_track.track.name:
            for artist in pl_track.track.artists:
                if artist.name in pl_track.track.name:
                    main_artist = artist
            if not main_artist:
                main_artist = pl_track.track.artists[0]
        else:
            main_artist = pl_track.track.artists[0]

        if main_artist.id not in unique_artists:
            all_tracks.extend(get_all_artists_song(sp, main_artist.id, main_artist.name))
            unique_artists.add(main_artist.id)

    for track in all_tracks:
        mongo_client.write_collection('random-tracks', asdict(track))
    return all_tracks


""" Given an artist id, return all their songs 

TODO:
    - Consider removing duplicate using ISRC set
"""


def get_all_artists_song(sp: spotipy.Spotify, artist_id: str, artist_name: str) -> List[Track]:
    all_tracks: set[Track] = set()
    artist_albums: ArtistAlbums = sp_fetch(sp.artist_albums, ArtistAlbums, artist_id,
                                           album_type='album,single')
    tracks_to_fetch = set()
    albums_to_fetch = set()

    for album in artist_albums.items:
        albums_to_fetch.add(album.id)

    chunk_size = 50  
    for i in range(0, len(albums_to_fetch), chunk_size):
        chunk = list(albums_to_fetch)[i:i + chunk_size]
        albums:SeveralAlbums = sp_fetch(sp.albums, SeveralAlbums, chunk)

        for album_item in albums.albums:
            for track in album_item.tracks.items:
                tracks_to_fetch.add(track.id)

    all_fetched_tracks = []
    for i in range(0, len(tracks_to_fetch), chunk_size):
        chunk = list(tracks_to_fetch)[i:i + chunk_size]
        tracks: SeveralTracks = sp_fetch(sp.tracks, SeveralTracks, chunk)
        all_fetched_tracks.extend(tracks.tracks)

    print(artist_name)
    print(len(all_fetched_tracks))
    return all_fetched_tracks


"""
    Extract uri from link via regex
"""

def get_uri(track_link: str):
    url = "https://open.spotify.com/track/6iIdZjJVTkYD3CcqIdrCFF?si=e4644a10581d4d7c"
    pattern = r"https:\/\/open\.spotify\.com\/track\/([a-zA-Z0-9]+)"

    match = re.search(pattern, url)
    if match:
        uri = match.group(1)
        return uri
    else:
        print("No URI found.")

"""
    Given a song get the radio of tracks associated with it, return a playlist link to it

"""

def radio_track(sp: spotipy.Spotify, track_link: str):
    
    recc: Recc = sp_fetch(sp.recommendations, Recc, limit=100, seed_tracks=[get_uri(track_link)])
    
    uris = []
    for t in recc.tracks:
        artist: Artist = sp_fetch(sp.artist, Artist, t.artists[0].id)
       
       
        phonk = False
        for g in artist.genres:
            if 'phonk' in str.lower(g):
                phonk = True 
            else:
                print(g)
        
        if not phonk:
            uris.append(t.uri)

    playlist = write_songs_to_playlist(sp, 'reccs', uris)

    # return playlist['external_urls']['spotify']

    return None

"""
given track uri fetch and check if its valid
"""

def fetch_track(sp: spotipy.Spotify, uri):
    try:
        track: Track = sp_fetch(sp.track, Track, uri)
    except:
        print(f'fake uri: {uri}')


def parse_id_from_url(url: str):
        """ Given a spotify url for a playlist, obtain the ID """
        regex = r'(?:https:\/\/open\.spotify\.com\/playlist\/)([a-zA-Z0-9]+)'
        matches = re.match(regex, url)
        if matches:
            return matches.group(1)
        else:
            return False

async def fetch_playlist(sp: spotipy.Spotify, uri) -> List[PlaylistTrack]:

    # parsed_id = parse_id_from_url(uri)


    playlist_tracks: List[PlaylistTrack] = await fetch_async(sp, PlaylistTracks, uri, chunk_size=50)

    return playlist_tracks


"""
Given a song (uri) and a user, return a boolean saying whether they have liked it or not

TODO
    - support a list and a single uri
"""


def is_liked(sp: spotipy.Spotify, uris: List[str]):
    return sp.current_user_saved_tracks_contains(tracks=uris)[0]


""" fetch all saved tracks for current user """


async def fetch_liked_tracks(sp: spotipy.Spotify) -> List[Track]:
    return await fetch_async(sp, SavedTracks, chunk_size=50)



"""
Play a specific uri on the first device ID listed.

uri = spotify:track:xyz
"""
def play_track(sp: spotipy.Spotify, uri: str):
    device_id = sp.devices()['devices'][0]['id']


    sp.start_playback(device_id=device_id, uris=[uri])


"""
    Make a new playlist and add tracks
"""


def write_songs_to_playlist(sp, name: str, tracks) -> str:
    playlist = sp.user_playlist_create(user='alcct3q9gddtkpcyidgx1z9yf', name=name, public=False)
    limit = 50
    for i in range(0, len(tracks), limit):
        sp.playlist_add_items(playlist['id'], list(tracks)[i:i + limit])
    return playlist


"""
    Return all tracks from A , based on the difference  with B
    or example if A has tracks [1,2,3] and B has tracks [1], return [2,3] 
"""

def track_difference(track_list_A: List[Track], track_list_B: List[Track]) -> List[Track]:

    # create a set of isrcs from B
    isrcs_b = {track.external_ids.isrc for track in track_list_B}

    # use the set to do O(1) lookup for isrc.
    filtered_a = [track for track in track_list_A if track.external_ids.isrc not in isrcs_b]
    return filtered_a

"""
    Given a list of tracks return a list of the uris only
"""

def fetch_track_uris(tracks: List[Track]) -> List[str]:
    uris: List[str] = []
    for track in tracks:
        uris.append(track.uri)
    return uris

"""
    Fetch all related artists

"""

def fetch_related_artists(sp: spotipy.Spotify, artist: str) -> List[Artist]:


    related : SeveralArtists = sp_fetch(sp.artist_related_artists, SeveralArtists, artist) 



"""
    Fetch all playlists of the current user

"""

async def fetch_current_user_playlists(sp: spotipy.Spotify) -> List[SimplifiedPlaylistObject]:

    playlists: List[SimplifiedPlaylistObject] = await fetch_async(sp, UserPlaylist)
    # for idx, item in enumerate(playlists):
    #     print(f'sgsfgfs{idx}. {item.name}')
     
    for item in playlists:
        if item.name == 'cringe chat':
            print(len(item.images))
          
    print(len(playlists))
    return playlists


      