import datetime
import json
import re
from typing import Type, TypeVar, Callable, Any

from shrillecho.types.album_types import ArtistAlbums

T = TypeVar('T')


# Respect to spotipy for designing the regex and id / uri parsing functions
_regex_spotify_uri = r'^spotify:(?:(?P<type>track|artist|album|playlist|show|episode):(?P<id>[0-9A-Za-z]+)|user:(?P<username>[0-9A-Za-z]+):playlist:(?P<playlistid>[0-9A-Za-z]+))$'  
_regex_spotify_url = r'^(http[s]?:\/\/)?open.spotify.com\/(?P<type>track|artist|album|playlist|show|episode|user)\/(?P<id>[0-9A-Za-z]+)(\?.*)?$'  
_regex_base62 = r'^[0-9A-Za-z]+$'


def sp_fetch(api_function: Callable, dataclass_type: Type[T], *args, **kwargs) -> T:
    api_response = api_function(*args, **kwargs)
    json_data = json.dumps(api_response)
    return dataclass_type.from_json(json_data)

def get_id(type, id):
    uri_match = re.search(_regex_spotify_uri, id)
    if uri_match is not None:
        uri_match_groups = uri_match.groupdict()
        if uri_match_groups['type'] != type:
            raise Exception( "Unexpected Spotify URI type.")
        return uri_match_groups['id']

    url_match = re.search(_regex_spotify_url, id)
    if url_match is not None:
        url_match_groups = url_match.groupdict()
        if url_match_groups['type'] != type:
            raise Exception( "Unexpected Spotify URL type.")
    
        return url_match_groups['id']

    if re.search(_regex_base62, id) is not None:
        return id
    
    raise Exception( "Unexpected Spotify URL / URI type.")

def is_uri(uri):
    return re.search(_regex_spotify_uri, uri) is not None

def get_uri(type, id):
    if is_uri(id):
        return id
    else:
        return "spotify:" + type + ":" + get_id(type, id)
    
def is_earlier(target_date, min_date):

    try:
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        min_date_obj = datetime.strptime(min_date, '%Y-%m-%d')
    except:
        return True

    return target_date_obj < min_date_obj