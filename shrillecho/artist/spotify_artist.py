import asyncio
from datetime import datetime
import json
import math
import time
import requests
import spotipy
from shrillecho.spotify.client import SpotifyClient
from shrillecho.spotify.task_scheduler import TaskScheduler
from shrillecho.types.album_types import Album, ArtistAlbums, SeveralAlbums, SimplifiedAlbum, SimplifiedTrack
from shrillecho.types.artist_types import Artist, FollowerCount, SeveralArtists
from shrillecho.types.base_types import Followers
from shrillecho.types.track_types import SeveralTracks, Track
from shrillecho.user.user import SpotifyUserUtil
from shrillecho.utility.cache import cached
from shrillecho.utility.general_utility import get_id, is_earlier, sp_fetch
from typing import List



class SpotifyArtist:

    @staticmethod
    @cached(cache_key_prefix="followers", class_type=FollowerCount, expiry=3600)
    async def followers(sp: SpotifyClient, artist: str) -> int:
        artist_id = get_id("artist", artist)
        data = {"artist": artist_id}
        followers_call = requests.post("http://localhost:8002/ml", json=data)
        followers = followers_call.json()
        return FollowerCount.from_json(json.dumps(followers))


    @staticmethod
    async def get_artist_tracks(sp: SpotifyClient, artist_id: str) -> List[Track]:
        artist_id = get_id("artist", artist_id)
        
        """ Given an artist id, return all unique their songs """
     
        # first get all albums
        artist_albums: List[SimplifiedAlbum] = await sp.artist_albums(artist=artist_id)
        print(len(artist_albums))

        # second get all tracks from each album
        album_tracks: List[SimplifiedTrack] = []
        for album in artist_albums:
            album_tracks.extend(await sp.album_tracks(album=album.id))
    
        # finally get all full expanded tracks from simplified tracks
        track_ids = []
        for item in album_tracks:
            track_ids.append(item.id)

        tracks: List[Track] = []
        for i in range(0, len(track_ids), 50):
            chunk = track_ids[i:i + 50]
            more_tracks: SeveralTracks = await sp.tracks(chunk)
            print(more_tracks.tracks)
            tracks.extend(more_tracks.tracks)

        return set(tracks)
    
    @staticmethod
    async def get_artist_albums(sp: SpotifyClient, artist_id: str, simple=False) -> List[Album] | List[SimplifiedAlbum]:
        
        """ Given an artist id, return all albums expanded """
        
        artist_albums: List[SimplifiedAlbum] = await sp.artist_albums(artist=artist_id)

        if simple:
            return artist_albums

        album_ids = []
    
        for album in artist_albums:
            album_ids.append(album.id)
        
        albums: List[Album] = []
        for i in range(0, len(album_ids), 20):
            chunk = album_ids[i:i + 20]
            more_albums: SeveralAlbums = await sp.albums(chunk)
            albums.extend(more_albums.albums)
        
        return albums
    
    @staticmethod
    async def get_artist_new_releases(sp: SpotifyClient, artist_id: str, earliest_date: str ='2024-03-01' ) -> List[SimplifiedAlbum]:
        albums: List[SimplifiedAlbum] = []
        artist_albums: ArtistAlbums = await sp.artist_albums_single(artist=artist_id, offset=0)
        albums.extend(artist_albums.items)
        next = artist_albums.next
        while next != None:
            offset: int = artist_albums.offset + 50
            artist_albums: ArtistAlbums = await sp.artist_albums_single(artist=artist_id, offset=offset)
            if len(artist_albums.items) == 0:
                break
            last_album = artist_albums.items[-1]
            next = artist_albums.next
            if is_earlier(last_album.release_date, earliest_date):
                break
            albums.extend(artist_albums.items)
        
        return albums
    
    @staticmethod
    async def get_followed_new_releases(sp: SpotifyClient) -> List[SimplifiedAlbum]:
        followed_artists: List[Artist] = await SpotifyUserUtil.get_followed_artists(sp)

        ids = [artist.id for artist in followed_artists]

        task_scheduluer = TaskScheduler()

        tasks = [
            (SpotifyArtist.get_artist_new_releases, (sp, artist_id,)) for artist_id in ids
        ]
    
        task_scheduluer.load_tasks(tasks)
   
        return await task_scheduluer.execute_tasks(batch_size=8)
     

    @staticmethod
    async def most_obscure_artists(sp: SpotifyClient, artist: str, artists: List[Artist], depth: int = 0) -> List[Artist]:
        

        if depth == 10:
            return artists

        artist_id = get_id("artist", artist)

        related_artists: List[Artist] = await sp.artist_related(artist=artist_id)
        
        most_obscure = math.inf
        most_obscure_artist = None

        for artist in related_artists:
            followers: FollowerCount = await SpotifyArtist.followers(sp, artist=artist.id)
            follower_count = followers.followers

            if follower_count < most_obscure and artist not in artists:
                most_obscure = follower_count 
                most_obscure_artist = artist


        artists.append(most_obscure_artist)
        depth += 1

        return await SpotifyArtist.most_obscure_artists(sp, most_obscure_artist.id, artists, depth)

    @staticmethod
    async def get_playlist_artists(sp: SpotifyClient, playlist: str) -> List[Artist]:

        playlist_id = get_id("playlist", playlist)
        playlist_tracks: List[Track] = await sp.playlist_tracks(playlist_id=playlist_id)

        artist_ids = set()

        for track in playlist_tracks:
            if track.artists[0].id and track.external_ids.isrc:
                artist_ids.add(track.artists[0].id)

        artist_ids = list(artist_ids)

        artists: List[Artist] = []
        for i in range(0, len(artist_ids), 50):
            chunk = artist_ids[i:i + 50]
            sev_artists: SeveralArtists = await sp.artists(chunk)
            artists.extend(sev_artists.artists)
        
        return artists
        




    