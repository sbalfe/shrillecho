from typing import List

# Types
from .components import AddedBy, Owner
from .base_types import *
from .tracks import Track


@dataclass_json
@dataclass
class PlaylistTrack:
    added_at: str
    added_by: AddedBy
    is_local: bool
    primary_color: Optional[str]
    track: Track


@dataclass_json
@dataclass
class PlaylistTracks:
    href: str
    limit: Optional[int]
    next: Optional[str]
    offset: Optional[int]
    previous: Optional[str]
    total: Optional[int]
    items: List[PlaylistTrack]


@dataclass_json
@dataclass
class Playlist:
    """ Get playlist - https://developer.spotify.com/documentation/web-api/reference/get-playlist """
    id: str
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
    tracks: Optional[PlaylistTracks] = None
    type: Optional[str] = None
    uri: Optional[str] = None
    followers: Optional[Followers] = None


