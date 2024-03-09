from typing import List

# Types
from .base_types import *
from shrillecho.types.artists import SimpleArtist, Artist
from .components import LinkedFrom


@dataclass_json
@dataclass
class SimplifiedTrack:
    """ Track object for album"""
    artists: List[SimpleArtist]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    preview_url: Optional[str]
    track_number: int
    type: str
    uri: str
    is_local: bool
    restrictions: Optional[Restrictions] = None
    is_playable: Optional[bool] = None
    linked_from: Optional[LinkedFrom] = None


@dataclass_json
@dataclass
class AlbumTracks:
    """ https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks tracks object """
    href: str
    limit: int
    offset: int
    total: int
    items: List[SimplifiedTrack]
    next: Optional[str] = None
    previous: Optional[str] = None



@dataclass_json
@dataclass
class Album:
    """" Get album - https://developer.spotify.com/documentation/web-api/reference/get-an-album """
    album_type: str # ok
    artists: List[SimpleArtist] # ok
    available_markets: List[str] # ok
    external_urls: ExternalUrls # ok
    id: str #ok
    images: List[Image] # ok 
    name: str #ok
    release_date: str#ok
    release_date_precision: str#ok
    type: str#ok
    uri: str#ok
    genres: Optional[List[str]] = None #ok
    restrictions: Optional[Restrictions] = None #ok
    copyrights: Optional[List[Copyright]] = None # ok
    external_ids: Optional[ExternalIds] = None
    label: Optional[str] = None#ok
    popularity: Optional[int] = None#ok
    tracks: Optional[AlbumTracks] = None
    total_tracks: Optional[int] = None #ok
    href: Optional[str] = None#ok

@dataclass_json
@dataclass
class SimplifiedAlbum:
    album_type: str
    total_tracks: int
    available_markets: List[str]
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: dict
    type: str
    uri: str
    artists: List[SimpleArtist]
    album_group: str


@dataclass_json
@dataclass
class ArtistAlbums:
    href: str
    limit: int
    next: str
    offset: int
    previous: str
    total: int
    items: List[SimplifiedAlbum]



@dataclass_json
@dataclass
class SeveralAlbums:
    """ Get several albums - https://developer.spotify.com/documentation/web-api/reference/get-multiple-albums"""
    albums: List[Album]
