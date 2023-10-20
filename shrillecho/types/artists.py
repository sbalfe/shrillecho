from typing import List, TYPE_CHECKING, Optional
from .base_types import *

@dataclass_json
@dataclass
class Artist:
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str
    followers: Optional[Followers] = None
    genres: Optional[List[str]] = None
    images: Optional[List[Image]] = None
    popularity: Optional[int] = None


@dataclass_json
@dataclass
class SimpleArtist:
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str