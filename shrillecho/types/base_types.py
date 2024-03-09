from dataclasses import dataclass
from typing import Optional
# from dataclasses_json import dataclass_json
from fastclasses_json import dataclass_json


@dataclass_json
@dataclass
class ExternalUrls:
    spotify: Optional[str] = None
    href: Optional[str] = None



@dataclass_json
@dataclass
class ExternalIds:
    isrc: Optional[str] = None
    ean: Optional[str] = None
    upc: Optional[str] = None
 
   
  

@dataclass_json
@dataclass
class Followers:
    total: int


@dataclass_json
@dataclass
class Policies:
    opt_in_trial_premium_only_market: bool

@dataclass_json
@dataclass
class Copyright:
    text: str
    type: str

@dataclass_json
@dataclass
class ExplicitContent:
    filter_enabled: bool
    filter_locked: bool

@dataclass_json
@dataclass
class Image:
    url: str
    height: int
    width: int
   

@dataclass_json
@dataclass
class Restrictions:
    reason: Optional[str]
  
