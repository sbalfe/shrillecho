import os
from typing import List

from shrillecho.types.playlists import Playlist, PlaylistTracks, PlaylistTrack
import json
import spotipy
import requests
import re
from shrillecho.utility.general import json_debug


class PlaylistEngine:

    def __init__(self, sp: spotipy.Spotify):
        self.__sp = sp

    def load_playlist(self, playlist_id: str, load_all_tracks=True) -> Playlist:
        playlist = Playlist.from_json(json.dumps(self.__sp.playlist(playlist_id)))
        return self.__load_tracks(playlist) if load_all_tracks else playlist

    def sort_by_release_date(self, playlist: Playlist):
        track_uris: List[str] = [item.track.uri for item in playlist.tracks.items]
        print(f'number of uris: {len(track_uris)}')
        self.__sp.playlist_reorder_items(playlist.id, range_start=0, insert_before=20, range_length=10)
        self.__sp.playlist_change_details(playlist.id, description="[shrillecho] - sort test")

    def __load_tracks(self, playlist: Playlist) -> Playlist:
        tracks: List[PlaylistTrack] = []
        playlist_tracks: PlaylistTracks = playlist.tracks

        while playlist_tracks.next:

            limit: int = playlist_tracks.limit
            offset: int = playlist_tracks.offset + limit

            playlist_tracks: PlaylistTracks = self.__playlist_tracks_paginate(playlist.id, limit, offset)
            for playlist_track in playlist_tracks.items:
                tracks.append(playlist_track)
            print(f'tracks loaded: {len(tracks) + len(playlist_tracks.items)}')

        playlist.tracks.items.extend(tracks)

        return playlist

    def __playlist_tracks_paginate(self, playlist_id, limit, offset) -> PlaylistTracks:
        return PlaylistTracks.from_json(json.dumps(self.__sp.playlist_items(playlist_id, limit=limit, offset=offset)))

    @staticmethod
    def parse_id_from_url(url: str):
        regex = r'(?:https:\/\/open\.spotify\.com\/playlist\/)([a-zA-Z0-9]+)'
        matches = re.match(regex, url)
        if matches:
            return matches.group(1)
        else:
            print("invalid url")











