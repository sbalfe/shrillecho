import asyncio
import hashlib
from typing import List, Set

# Internal
from shrillecho.artist.spotify_artist import SpotifyArtist
from shrillecho.spotify.client import SpotifyClient
from shrillecho.track.spotify_track import SpotifyTrack


# Type definitions
from shrillecho.types.playlist_types import PlaylistTrack, SimplifiedPlaylistObject
from shrillecho.types.track_types import Track
from shrillecho.utility.cache import cached


class SpotifyPlaylist:

    @staticmethod
    async def fetch_current_user_playlists(sp: SpotifyClient) -> List[SimplifiedPlaylistObject]:
        return await sp.current_user_saved_playlists(batch=True, chunk_size=10)
    

    @staticmethod
    async def write_songs_to_playlist(sp: SpotifyClient, name: str, track_list: List[Track], user: str) -> str:
        tracks = SpotifyTrack.fetch_track_ids(track_list)
        playlist = await sp.user_playlist_create(user=user, name=name, public=False)
        limit = 50
        for i in range(0, len(tracks), limit):
            await sp.playlist_add_items(playlist['id'], tracks[i:i + limit])
        return playlist
    
    @staticmethod
    async def select_random_song_from_artists(sp: SpotifyClient, playlist_id: str, chunk_size=10) -> List[Track]:
        all_tracks: List[Track] = []
        playlist_tracks: List[PlaylistTrack] = await sp.playlist_tracks(playlist_id=playlist_id, batch=True, chunk_size=chunk_size)
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
                all_tracks.extend(SpotifyArtist.get_artist_tracks(sp, main_artist.id))
                unique_artists.add(main_artist.id)
        return all_tracks


    @staticmethod
    @cached(cache_key_prefix="like_filtered", class_type=Track, expiry=3600)
    async def removed_liked_tracks(sp, playlist_tracks, liked_tracks) -> List[Track]:
        filtered_tracks: List[Track] = await SpotifyTrack.track_difference_liked(sp=sp, playlist_tracks=playlist_tracks, 
                                                                                liked_tracks=liked_tracks)
        for track in filtered_tracks:
            track.liked = False
        return filtered_tracks
    
    @staticmethod
    @cached(cache_key_prefix="load_playlist_liked", class_type=Track, expiry=3600)
    async def load_playlist_with_likes(sp, playlist_tracks, liked_tracks) -> List[Track]: 
    
        tasks = [SpotifyTrack.is_liked(sp, track, liked_tracks=liked_tracks) for track in playlist_tracks]
        results = await asyncio.gather(*tasks)
        for track, liked in zip(playlist_tracks, results):
            track.liked = liked
        return playlist_tracks

    @staticmethod
    async def get_playlist_tracks_filtered(sp: SpotifyClient, playlist_id, get_non_liked=False) -> List[Track]:
        liked_tracks: List[Track] = await sp.current_user_saved_tracks(batch=True, chunk_size=10)
        playlist_tracks: List[Track] = await sp.playlist_tracks(playlist_id=playlist_id, batch=True, chunk_size=10)
        if get_non_liked:
            return await SpotifyPlaylist.removed_liked_tracks(sp, playlist_tracks, liked_tracks)
        return await SpotifyPlaylist.load_playlist_with_likes(sp, playlist_tracks, liked_tracks)
