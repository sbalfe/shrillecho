from __future__ import annotations
from .base_types import *


@dataclass_json
@dataclass
class AddedBy:
    external_urls: ExternalUrls
    href: str
    id: str
    type: str
    uri: str
    followers: Optional[Followers] = None


@dataclass_json
@dataclass
class ArtistForAlbum:
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


@dataclass_json
@dataclass
class LinkedFrom:
    external_urls: ExternalUrls
    href: str
    id: str
    type: str
    uri: str


@dataclass_json
@dataclass
class Owner:
    display_name: Optional[str]
    external_urls: ExternalUrls
    href: str
    id: str
    type: str
    uri: str
    followers: Optional[Followers] = None
