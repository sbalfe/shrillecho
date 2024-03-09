from dataclasses import dataclass
from typing import List, Optional

from .base_types import (
    ExternalUrls, Followers, ExternalIds, Copyright, ExplicitContent, Image, Restrictions
)
from .tracks import Track


# @dataclass
# class AddedBy:
#     external_urls: ExternalUrls
#     followers: Followers
#     href: str
#     id: str
#     type: str
#     uri: str
#
#
# @dataclass
# class ArtistForAlbum:
#     external_urls: ExternalUrls
#     href: str
#     id: str
#     name: str
#     type: str
#     uri: str
#
#
# @dataclass
# class LinkedFrom:
#     external_urls: ExternalUrls
#     href: str
#     id: str
#     type: str
#     uri: str
#
#
# @dataclass
# class Owner:
#     external_urls: ExternalUrls
#     followers: Followers
#     href: str
#     id: str
#     type: str
#     uri: str
#     display_name: Optional[str] = None


# @dataclass
# class Artist:
#     external_urls: ExternalUrls
#     followers: Followers
#     genres: Optional[List[str]]
#     href: str
#     id: str
#     images: List[Image]
#     name: str
#     popularity: int
#     type: str
#     uri: str


# @dataclass
# class SimplifiedTrack:
#     """ track object without its album basically (at least for now)"""
#     artists: List[Artist]
#     available_markets: List[str]
#     disc_number: int
#     duration_ms: int
#     explicit: bool
#     external_urls: ExternalUrls
#     href: str
#     id: str
#     is_playable: bool
#     linked_from: LinkedFrom
#     restrictions: Restrictions
#     name: str
#     preview_url: str
#     track_number: int
#     type: str
#     uri: str
#     is_local: bool


# @dataclass
# class AlbumTracks:
#     """ https://developer.spotify.com/documentation/web-api/reference/get-an-album tracks object """
#     href: str
#     limit: int
#     next: str
#     offset: int
#     previous: str
#     total: int
#     items: List[SimplifiedTrack]


# @dataclass
# class Album:
#     """" Get album - https://developer.spotify.com/documentation/web-api/reference/get-an-album """
#     album_type: str
#     total_tracks: int
#     available_markets: List[str]
#     external_urls: ExternalUrls
#     href: str
#     id: str
#     images: List[Image]
#     name: str
#     release_date: str
#     release_date_precision: str
#     restrictions: Restrictions
#     type: str
#     uri: str
#     artists: List[Artist]
#     tracks: AlbumTracks
#     copyrights: List[Copyright]
#     external_ids: ExternalIds
#     genres: List[str]
#     label: str
#     popularity: int


# @dataclass
# class SeveralAlbums:
#     """ Get several albums - https://developer.spotify.com/documentation/web-api/reference/get-multiple-albums"""
#     albums: List[Album]


# @dataclass
# class SimpleArtist:
#     external_urls: ExternalUrls
#     href: str
#     id: str
#     name: str
#     type: str
#     uri: str

#
# @dataclass
# class Track:
#     """ Get track - https://developer.spotify.com/documentation/web-api/reference/get-track """
#     album: Album
#     artists: List[Artist]
#     available_markets: List[str]
#     disc_number: int
#     duration_ms: int
#     explicit: bool
#     external_urls: ExternalUrls
#     external_ids: ExternalIds
#     href: str
#     id: str
#     is_playable: bool
#     linked_from: LinkedFrom
#     restrictions: Restrictions
#     name: str
#     preview_url: str
#     track_number: int
#     type: str
#     uri: str
#     is_local: bool


# @dataclass
# class PlaylistTrack:
#     added_at: str
#     added_by: AddedBy
#     is_local: bool
#     track: Track
#
#
# @dataclass
# class PlaylistTracks:
#     href: str
#     limit: int
#     next: str
#     offset: int
#     previous: str
#     total: int
#     items: List[PlaylistTrack]
#
#
# @dataclass
# class Playlist:
#     """ Get playlist - https://developer.spotify.com/documentation/web-api/reference/get-playlist """
#     collaborative: bool
#     description: str
#     external_urls: ExternalUrls
#     followers: Followers
#     href: str
#     id: str
#     images: List[Image]
#     name: str
#     owner: Owner
#     public: bool
#     snapshot_id: str
#     tracks: PlaylistTracks  # Pagination of PlaylistTrack objects
#     type: str
#     uri: str


# @dataclass
# class SeveralTracks:
#     """ Get several tracks - https://developer.spotify.com/documentation/web-api/reference/get-several-tracks"""
#     items: List[Track]
#
#
#
# @dataclass
# class SavedTrack:
#     added_at: str
#     track: Track

#
# @dataclass
# class CurrentUserProfile:
#     country: str
#     display_name: str
#     email: str
#     explicit_content: ExplicitContent
#     external_urls: ExternalUrls
#     followers: Followers
#     href: str
#     id: str
#     images: List[Image]
#     product: str
#     type: str
#     uri: str
#
#
# @dataclass
# class UserProfile:
#     display_name: str
#     external_urls: ExternalUrls
#     followers: "Followers"
#     href: str
#     id: str
#     images: List[Image]
#     type: str
#     uri: str


# @dataclass
# class SavedTracks:
#     """ https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks """
#     href: str
#     limit: int
#     next: str
#     offset: int
#     previous: str
#     total: int
#     items: List[SavedTrack]
