import asyncio
from dataclasses import asdict, dataclass
import math
import random
import time
from typing import List, Optional, Type, Union
from annotated_types import T
from fastclasses_json import dataclass_json
import httpx
import json
import os

import requests

from shrillecho.auth.local_auth import authenticate_local
from shrillecho.auth.oauth import ClientCredentials, OAuthCredentials
from shrillecho.spotify.task_scheduler import TaskScheduler
from shrillecho.types.album_types import AlbumTracks, ArtistAlbums, SeveralAlbums, SimplifiedAlbum, SimplifiedTrack
from shrillecho.types.artist_types import Artist, FollowedArtists, SeveralArtists
from shrillecho.types.playlist_types import Playlist, PlaylistTrack, PlaylistTracks, SimplifiedPlaylistObject, UserPlaylists
from shrillecho.types.soundcloud_types import User
from shrillecho.types.track_types import Recc, SavedTrack, SavedTracks, SeveralTracks, Track
from shrillecho.utility.archive_maybe_delete.spotify_client import SpotifyClientGlitch
from shrillecho.utility.general_utility import get_id, sp_fetch
import spotipy
# from shrillecho.auth.local_auth import authenticate_local
from shrillecho.utility.archive_maybe_delete.old_cache import Cache
from shrillecho.utility.cache import cached, mongo_client, redis_client
import redis

@dataclass
class SpotifyAuthContext:
    client_id: str
    client_secret: str
    scope: str
    redirect_uri: str

class SpotifyClient:

    __spotify_api = "https://api.spotify.com/v1/"

    def __init__(self, auth=None, auth_flow: Union[OAuthCredentials | ClientCredentials] = None):
        self.auth = auth
        self.auth_flow = auth_flow
        self.access_token = None
        if auth_flow:
            self.access_token = auth_flow.get_access_token()
        else:
            self.access_token = self.auth
        self.temp_spotipy: spotipy.Spotify = spotipy.Spotify(auth=self.access_token)
        self.http_client: httpx.AsyncClient = httpx.AsyncClient()
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.batch_errors = 0
        self.rate_lock = asyncio.Event()
        glitch = SpotifyClientGlitch()
        self.glitched_token = glitch.access_token
        self.task_scheduler = TaskScheduler()

        self.batch_param_map = {}
        self.batch_param_map[SavedTracks] = ()
        # self.glitched_client_token = glitch.client_token
      
    
    class ShrillechoException(Exception):
        def __init__(self, message, error_code=None, retry_after: int = None):
            super().__init__(message)
            self.error_code = error_code
            self.retry_after = retry_after


    def create_get_routine(self, url, resp_type):
        return (self._get, (url, resp_type))
       

    async def _request(self,
                       method: str, 
                       endpoint: str, 
                       response_type = None,
                       params: Optional[dict] = None, 
                       body: Optional[dict] = None):
        headers = {"authorization" : f"Bearer {self.access_token}"}
        while self.rate_lock.is_set():
            await asyncio.sleep(1)

        # print(f"endpoint: {self.__spotify_api}{endpoint}")
        response = await self.http_client.request(method, f"{self.__spotify_api}{endpoint}", params=params, headers=headers, json=body)
        if response.status_code > 300:
            retry_after = None
            if response.status_code == 429:
                self.rate_lock.set()
                retry_after = int(response.headers.get('Retry-After'))
                print(f"sleeping setting lock: {retry_after} seconds")
                await asyncio.sleep(retry_after)
                self.rate_lock.clear()
           
            print(response.text)
            raise SpotifyClient.ShrillechoException("Spotify Client Error", error_code=response.status_code, 
                                                    retry_after=retry_after)
        if response_type:
            return response_type.from_json(json.dumps(response.json()))
        else:
            return response.json()
        
    async def _get(self, endpoint: str, response_type=None, params: Optional[dict]=None):
        return await self._request(method="GET", endpoint=endpoint, params=params, response_type=response_type)
    
    async def _post(self, endpoint: str, body: dict, params: Optional[dict]=None):
        await self._request(method="POST", endpoint=endpoint, params=params, body=body)

    ############# Shrillecho Implemented Methods #############

    async def me(self) -> SavedTracks:
        return await self._get("me", response_type=User)
    
    async def track(self, track: str) -> Track:
        return await self._get(f"tracks/{get_id("track", track)}", response_type=Track)
    
    @cached(cache_key_prefix="artist_related", class_type=Artist, expiry=1000)
    async def artist_related(self, artist: str) -> List[Artist]:
        artist_id = get_id("artist", artist)
        several_artists: SeveralArtists = await self._get(f"artists/{artist_id}/related-artists", response_type=SeveralArtists)
        return several_artists.artists

    
    async def recccs(self) -> Recc:
        return await self._get("recommendations?limit=50&seed_tracks=5m4Lh4bgiYKSj2MlDcrnxh", response_type=Recc)
    
    async def artists(self, artists: List[str]) -> SeveralArtists:
        artist_ids = [get_id("artist", a) for a in artists]
        return await self._get("artists?ids=" + ",".join(artist_ids), response_type=SeveralArtists)
    

    ################## Spotipy Methods ####################

    async def followed_artists(self):
        self.temp_spotipy.current_user_followed_artists()
        return sp_fetch(self.temp_spotipy.current_user_following_artists)

    @cached(cache_key_prefix="playlist", class_type=Playlist, expiry=3600)
    async def playlist(self, playlist_id: str) -> Playlist:
        return sp_fetch(self.temp_spotipy.playlist, Playlist, get_id("playlist", playlist_id))
        
    @cached(cache_key_prefix="artist_related", class_type=SeveralArtists, expiry=3600)
    async def artist_related_artists(self, artist: str) -> List[Artist]:
        
        return sp_fetch(self.temp_spotipy.artist_related_artists, SeveralArtists, artist)
       
    @cached(cache_key_prefix="artist", class_type=Artist, expiry=3600)
    async def artist(self, artist_id: str) -> Artist:
        return sp_fetch(self.temp_spotipy.artist, Artist, get_id("artist", artist_id))
        
    async def artist_albums_single(self, artist, limit=50, offset=None) -> ArtistAlbums:
        return sp_fetch(self.temp_spotipy.artist_albums,ArtistAlbums,artist, limit=limit, offset=offset)
    
    async def albums(self, albums) -> SeveralAlbums:
        return sp_fetch(self.temp_spotipy.albums, SeveralAlbums, albums)
    
    async def tracks(self, tracks) -> SeveralTracks:
        return sp_fetch(self.temp_spotipy.tracks, SeveralTracks, tracks)

    async def user_playlist_create(self, user:str , name:str, public: bool):
        return self.temp_spotipy.user_playlist_create(user=user, name=name, public=public)

    async def playlist_add_items(self, playlist_id: str, tracks) -> None:
        self.temp_spotipy.playlist_add_items(playlist_id, tracks)

    async def current_user_unfollow_playlist(self, playlist_uri) -> None:
        self.temp_spotipy.current_user_unfollow_playlist(playlist_uri)

    async def reccomendations(self, limit, seed_artists=None,seed_genres=None,seed_tracks=None,country=None, track_list=True) -> Recc | List[Track]:

        reccs:  Recc = sp_fetch(self.temp_spotipy.recommendations, 
                              Recc, 
                              limit=limit, 
                              seed_tracks=seed_tracks, 
                              seed_artists=seed_artists, seed_genres=seed_genres)
        if track_list:
            return reccs.tracks
    
        return reccs 

                
    async def current_user_followed_artists(self, limit: int = 20, after=None) -> FollowedArtists :
        return sp_fetch(self.temp_spotipy.current_user_followed_artists, FollowedArtists, limit=limit, after=after)

    ################### BATCHING METHODS ############################
        
    @staticmethod
    def generate_pagination_batch_urls(ep_path: str, initial_item , query_params = None) -> List[str]:
        urls = []
        limit = 50
        pages = math.ceil(initial_item.total / limit)
        for page in range(0, pages):
            urls.append(f"{ep_path}?limit=50&offset={limit * page}")
        return urls
    
    async def batch_pagination_tasks(self, class_type, batch_size=5, *args, **kwargs):
        """
            Utilises the task scheduler to batch paginated pages, only works with endpoints
            that have the items, total, next, limit, offset attributes i.e most pagination endpoints

            NOTE: This unpacks by default the results and expands `tracks` attribute to track, consider making this optional to a granular level
        """
        if class_type == SavedTracks:
            ep_path = "me/tracks"
            initial_item = await self._get(f"me/tracks?offset={0}&limit={50}", response_type=SavedTracks)

        elif class_type == PlaylistTracks:
            playlist_id = kwargs.get('playlist_id')
            ep_path = f"playlists/{playlist_id}/tracks"
            initial_item = await self._get(f"playlists/{playlist_id}/tracks?offset={0}&limit={50}", response_type=PlaylistTracks)

        elif class_type == UserPlaylists:
            
            if kwargs.get('user_id'):
                user = kwargs.get('user_id')
                ep_path = f"users/{user}/playlists"
                user = kwargs.get('user_id')
                initial_item = await self._get(f"users/{user}/playlists?offset={0}&limit={50}", response_type=UserPlaylists)
            else:
                ep_path = "me/playlists"
                initial_item = await self._get(f"me/playlists/tracks?offset={0}&limit={50}", response_type=UserPlaylists)

        elif class_type == AlbumTracks:
            ep_path = f"albums/{kwargs.get('album_id')}/tracks"
            initial_item = await self._get(f"me/tracks?offset={0}&limit={50}", response_type=AlbumTracks)

        elif class_type == ArtistAlbums:
            artist = kwargs.get("artist_id")
    
            ep_path = f"artists/{artist}/albums"
            initial_item = await self._get(f"artists/{artist}/albums?offset={0}&limit={50}", response_type=ArtistAlbums)

        urls = SpotifyClient.generate_pagination_batch_urls(ep_path=ep_path, 
                                                                  initial_item=initial_item )
        tasks = [
            self.create_get_routine(url, class_type) for url in urls
        ]

        self.task_scheduler.load_tasks(tasks)

        return await self.task_scheduler.execute_tasks(batch_size=batch_size, unpack=True)

    @cached(cache_key_prefix="saved_tracks_0", class_type=Track)
    async def current_user_saved_tracks(self) -> List[Track]:
        """
            LIKED SONGS
        """
        return await self.batch_pagination_tasks(class_type=SavedTracks, batch_size=5)
    
    @cached(cache_key_prefix="my_playlists", class_type=SimplifiedPlaylistObject)
    async def current_user_saved_playlists(self) -> List[SimplifiedPlaylistObject]:
        """
            CURRENT USER PLAYLISTS 
        """
        return await self.batch_pagination_tasks(class_type=UserPlaylists, batch_size=5)
    
    @cached(cache_key_prefix="user_playlist", class_type=SimplifiedPlaylistObject)
    async def user_playlists(self, user: str):
        """
            SPECIFIC USER PLAYLISTS
        """
        return await self.batch_pagination_tasks(class_type=UserPlaylists, batch_size=5, user_id=user)
    
    @cached(cache_key_prefix="playlist_tracks", class_type=Track)
    async def playlist_tracks(self, playlist_id: str):
        """
            TRACKS FROM A PLAYLIST

        """
        return await self.batch_pagination_tasks(class_type=PlaylistTracks, batch_size=5, playlist_id=get_id("playlist", playlist_id))
    
    @cached(cache_key_prefix="album_tracks", class_type=SimplifiedTrack)
    async def album_tracks(self, album: str):
        """
            TRACKS FROM AN ALBUM
        """
        return await self.batch_pagination_tasks(class_type=AlbumTracks, batch_size=5, album_id=album)
    
    @cached(cache_key_prefix="artist_albums", class_type=SimplifiedAlbum)
    async def artist_albums(self,artist: str):
        """
            ALBUMS FROM AN ARTIST
        """
        
        return await self.batch_pagination_tasks(class_type=ArtistAlbums, batch_size=5, artist_id=artist)


