from typing import List

from shrillecho.types.playlist_types import Playlist, PlaylistTracks, PlaylistTrack
import json
import spotipy
import re
from shrillecho.utility.general_utility import *


class PlaylistEngine:

    def __init__(self, sp: spotipy.Spotify):
        self._sp = sp

    def load_playlist_tracks(self, playlist_id: str, load_all_tracks=True) -> List[PlaylistTrack]:
        playlist: Playlist = sp_fetch(self._sp.playlist, Playlist, playlist_id)
        return self._load_tracks(playlist) if load_all_tracks else playlist

    def sort_by_release_date(self, playlist: Playlist):
        track_uris: List[str] = [item.track.uri for item in playlist.tracks.items]
        print(f'number of uris: {len(track_uris)}')
        self._sp.playlist_reorder_items(playlist.id, range_start=0, insert_before=20, range_length=10)
        self._sp.playlist_change_details(playlist.id, description="[shrillecho] - sort test")

    # optimise this do not return a playlist object but rather an array of PlaylistTrack , making the metdata seperate
    def _load_tracks(self, playlist: Playlist) -> List[PlaylistTrack]:
        tracks: List[PlaylistTrack] = []

        playlist_tracks: PlaylistTracks = playlist.tracks

        while playlist_tracks.next:
            limit: int = playlist_tracks.limit
            offset: int = playlist_tracks.offset + limit

            playlist_tracks: PlaylistTracks = sp_fetch(self._sp.playlist_items, PlaylistTracks,
                                                       playlist.id, limit=limit, offset=offset)

            tracks.extend(playlist_tracks.items)

        # add the original fetch tracks
        tracks.extend(playlist.tracks.items)
        return tracks

    def _playlist_tracks_paginate(self, playlist_id, limit, offset) -> PlaylistTracks:
        return sp_fetch(self._sp.playlist_items, PlaylistTracks, playlist_id, limit=limit, offset=offset)

    @staticmethod
    def parse_id_from_url(url: str):
        """ Given a spotify url for a playlist, obtain the ID """
        regex = r'(?:https:\/\/open\.spotify\.com\/playlist\/)([a-zA-Z0-9]+)'
        matches = re.match(regex, url)
        if matches:
            return matches.group(1)
        else:
            print("invalid url")
