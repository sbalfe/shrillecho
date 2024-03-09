from typing import List, TYPE_CHECKING
from .base_types import *
from shrillecho.types.albums import Album
from shrillecho.types.artists import Artist
from shrillecho.types.components import LinkedFrom


@dataclass_json
@dataclass
class Track:
    """ Get track - https://developer.spotify.com/documentation/web-api/reference/get-track """
    album: Album
    artists: List[Artist]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_urls: ExternalUrls
    external_ids: ExternalIds
    href: str
    id: str
    name: str
    preview_url: str
    track_number: int
    type: str
    uri: str
    is_local: bool
    restrictions: Optional[Restrictions] = None
    is_playable: Optional[bool] = None
    linked_from: Optional[LinkedFrom] = None

    def __eq__(self, other):
        if isinstance(other, Track):
            return self.external_ids.isrc == other.external_ids.isrc
        return False
    def __hash__(self):
        return hash(self.external_ids.isrc)
@dataclass_json
@dataclass
class TrackSearchItems:
    href: str
    limit: int
    next: str
    offset: int
    previous: str
    total: int
    items: List[Track]

@dataclass_json
@dataclass
class AlbumSearchItems:
    href: str
    limit: int
    next: str
    offset: int
    previous: str
    total: int
    items: List[Album]


@dataclass_json
@dataclass
class ArtistSearchItems:
    href: str
    limit: int
    next: str
    offset: int
    previous: str
    total: int
    items: List[Artist]




@dataclass_json
@dataclass
class TrackSearch:
    tracks: TrackSearchItems

@dataclass_json
@dataclass
class AlbumSearch:
    albums: AlbumSearchItems

@dataclass_json
@dataclass
class ArtistSearch:
    artists: ArtistSearchItems


@dataclass_json
@dataclass
class SavedTrack:
    added_at: str
    track: Track


@dataclass_json
@dataclass
class SavedTracks:
    """ https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks """
    href: str
    limit: int
    next: str
    offset: int
    previous: str
    total: int
    items: List[SavedTrack]

@dataclass_json
@dataclass
class TrackInfo:
    href: str
    total: int



@dataclass_json
@dataclass
class SeveralTracks:
    """ Get several tracks - https://developer.spotify.com/documentation/web-api/reference/get-several-tracks"""
    tracks: List[Track]

@dataclass_json
@dataclass
class ReccSeed:
    afterFilteringSize: int
    afterRelinkingSize: int
    href: str
    id: str
    initialPoolSize: int
    type: str

@dataclass_json
@dataclass
class Recc:
    """ Get several tracks - https://developer.spotify.com/documentation/web-api/reference/get-several-tracks"""
    seeds: List[ReccSeed]
    tracks: List[Track]
