from typing import List

import spotipy
import requests

# Internal
from shrillecho.spotify.client import SpotifyClient
from shrillecho.types.playlist_types import Playlist, SimplifiedPlaylistObject
from shrillecho.types.track_types import Track
from shrillecho.utility.archive_maybe_delete.spotify_client import SpotifyClientGlitch

class SpotifyTrack:


    @staticmethod
    def is_duplicate_track(track_a: Track, track_b: Track):
        pass

    @staticmethod
    async def fetch_all_user_public_tracks(sp: SpotifyClient, user: str) -> List[Track]:
        tracks: List[Track] = []
        playlists: List[SimplifiedPlaylistObject] = await sp.user_playlists(user=user, batch=True, chunk_size=25)
        for playlist in playlists:
            tracks.extend(await sp.playlist_tracks(playlist_id=playlist.id, batch=True, chunk_size=25))
        return tracks

    @staticmethod
    def track_difference(track_list_A: List[Track], track_list_B: List[Track]) -> List[Track]:
        """
        Computes the difference between two lists of tracks.
        """
        metadata_dict: dict = {}
        local_or_removed = 0
        for track_b in track_list_B:
           
            try:
                key = (track_b.artists[0].id, track_b.name) 
            
                if key not in metadata_dict:
                    metadata_dict[key] = set()
                metadata_dict[key].add(track_b.external_ids.isrc)
            except:
                local_or_removed +=1
                continue
           
        filtered_a = []

        x = 0
 
        for track_a in track_list_A:
            try:
                key = (track_a.artists[0].id ,track_a.name ) 
                if any(track_a.external_ids.isrc in isrc for isrc in metadata_dict.get(key, set())):
                    continue 
                if key not in metadata_dict:
                    filtered_a.append(track_a)
                    continue
                x +=1
                print(f'isrc miss: {track_a.name}')
            except:
                continue
            
        return filtered_a
    
        
    @staticmethod
    def fetch_track_ids(tracks: List[Track]) -> List[str]:
        """
            Given a list of tracks return a list of the ids only
        """

        ids = []
        for track in tracks:
            if track.id:
                ids.append(track.id)

        return ids
    

    @staticmethod
    def clean_tracks(tracks: List[Track]) -> List[Track]:
        """
            Given a list of tracks remove all tracks that dont have ISRC
        """

        local_removed_copyright = 0
        cleaned_tracks: List[Track] = []
        for track in tracks:
            if track.external_ids.isrc:
                
                cleaned_tracks.append(track)
            else:
                local_removed_copyright += 1

        print(f'local_removed_copyright: {local_removed_copyright}')
        return cleaned_tracks

    @staticmethod
    async def track_difference_liked(sp: SpotifyClient, playlist_tracks: List[Track], liked_tracks: List[Track]) -> List[Track]:
        return SpotifyTrack.track_difference(playlist_tracks, liked_tracks)
    
    @staticmethod
    async def is_liked(sp: SpotifyClient, track, liked_tracks) -> bool:
        filtered_tracks: List[Track] = SpotifyTrack.track_difference([track], liked_tracks)
        return len(filtered_tracks) == 0
    

    @staticmethod
    async def get_radio(sp: SpotifyClient, track: str) -> List[Track]:
        data = {"track": track}
        radio_playlist = requests.post("http://localhost:8002/radio", json=data)
        radio_playlist_id = radio_playlist.json()["playlist"]
        playlist_tracks: List[Track] = await sp.playlist_tracks(radio_playlist_id, batch=True, chunk_size=1)
        return playlist_tracks
