from typing import List


# Types
from .component_types import AddedBy, Owner
from .base_types import *
from .track_types import Track, TrackInfo
import json

from .user_types import UserProfile


@dataclass_json
@dataclass
class PlaylistTrack:
    added_at: str
    added_by: AddedBy
    is_local: bool
    track: Track
    primary_color: Optional[str]
   


@dataclass_json
@dataclass
class PlaylistTracks:

    limit: Optional[int] = None
    next: Optional[str] = None
    offset: Optional[int]= None
    previous: Optional[str] = None
    total: Optional[int] = None
    items: List[PlaylistTrack] = None
    href: Optional[str] = None


@dataclass_json
@dataclass
class Playlist:
    """ Get playlist - https://developer.spotify.com/documentation/web-api/reference/get-playlist """
    id: str
    tracks: Optional[PlaylistTracks]
    collaborative: Optional[bool] = None
    description: Optional[str] = None
    external_urls: Optional[ExternalUrls] = None
    href: Optional[str] = None
    images: Optional[List[Image]] = None
    name: Optional[str] = None
    owner: Optional[Owner] = None
    primary_color: Optional[str] = None
    public: Optional[bool] = None
    snapshot_id: Optional[str] = None
    type: Optional[str] = None
    uri: Optional[str] = None
    followers: Optional[Followers] = None


@dataclass_json
@dataclass
class SimplifiedPlaylistObject:
    collaborative: bool
    description: str
    external_urls: ExternalUrls
    href: str
    id: str
    images: list[Image]
    name: str
    owner: UserProfile
    public: bool
    snapshot_id: str
    tracks: TrackInfo
    type: str
    uri: str

@dataclass_json
@dataclass
class UserPlaylists:
    """ https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists """
    href: str
    limit: int
    next: str
    offset: int
    previous: str
    total: int
    items: List[SimplifiedPlaylistObject]
