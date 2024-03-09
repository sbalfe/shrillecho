from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from fastclasses_json import dataclass_json


@dataclass_json
@dataclass
class PublisherMetadata:
    id: int
    urn: str
    artist: str
    contains_music: bool
    isrc: str
    

@dataclass_json
@dataclass
class User:
    avatar_url: str
    first_name: str
    followers_count: int
    full_name: str
    id: int
    kind: str
    last_modified: str
    last_name: str
    permalink: str
    permalink_url: str
    uri: str
    urn: str
    username: str
    verified: bool
    city: str
    country_code: str
    badges: List[bool]  # Replace Dict with List
    station_urn: str
    station_permalink: str


@dataclass_json
@dataclass
class Format:
    protocol: str
    mime_type: str


@dataclass_json
@dataclass
class Transcoding:
    url: str
    preset: str
    duration: int
    snipped: bool
    format: Format
    quality: str


@dataclass_json
@dataclass
class Media:
    transcodings: List[Transcoding]


@dataclass
class UsefulMeta:
    title: Optional[str]
    isrc: Optional[str]
    artist: Optional[str]
    username: Optional[str]
    created_at: Optional[str]
    release_date: Optional[str]
    duration: Optional[int]
    full_duration: Optional[int]
    artwork_url: Optional[str]

    @property
    def meta_list(self):
        ret = []
        if self.artist != None:
            ret += self.artist.split()
        if self.username != None:
            ret += self.username.split()
        if self.title != None:
            ret += self.title.split()
        return ret
        

@dataclass_json
@dataclass
class SoundCloudTrack:
    artwork_url: str 
    caption: Optional[str] 
    commentable: bool # NOT USEFUL
    comment_count: int # NOT USEFUL
    created_at: str 
    description: str
    downloadable: bool 
    download_count: int 
    duration: int
    full_duration: int 
    embeddable_by: str # NOT USEFUL
    genre: str
    has_downloads_left: bool # NOT USEFUL
    id: int# NOT USEFUL
    kind: str
    label_name: str
    last_modified: str
    license: str
    likes_count: int
    permalink: str
    permalink_url: str
    playback_count: int
    public: bool
    publisher_metadata: PublisherMetadata
    purchase_title: str
    purchase_url: str
    release_date: str
    reposts_count: int
    secret_token: Optional[str]
    sharing: str
    state: str
    streamable: bool
    tag_list: str
    title: str
    track_format: str
    uri: str
    urn: str
    user_id: int
    visuals: Optional[Any]
    waveform_url: str
    display_date: str
    media: Media  # Replace Dict with List
    station_urn: str
    station_permalink: str
    track_authorization: str
    monetization_model: str
    policy: str
    user: User

    @property
    def useful_meta(self):
        return UsefulMeta(
            title=self.title if self.title else None,
            isrc=self.publisher_metadata.isrc if self.publisher_metadata else None,
            artist=self.publisher_metadata.artist if self.publisher_metadata else None,
            username=self.user.username if self.user else None,
            created_at=self.created_at or None,
            release_date=self.release_date or None,
            duration=self.duration if self.duration is not None else None,
            full_duration=self.full_duration if self.full_duration is not None else None,
            artwork_url=self.artwork_url
        )
    