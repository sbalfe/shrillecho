from __future__ import annotations
from typing import List
from .base_types import *


@dataclass_json
@dataclass
class CurrentUserProfile:
    display_name: str
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    type: str
    uri: str
    followers: Followers
    country: Optional[str] = None
    product: Optional[str] = None
    explicit_content: Optional[ExplicitContent] = None
    email: str = None
    birthdate: Optional[str] = None
    policies: Optional[Policies] = None

@dataclass_json
@dataclass
class UserProfile:
    display_name: str
    external_urls: ExternalUrls
    followers: Followers
    href: str
    id: str
    images: List[Image]
    type: str
    uri: str
