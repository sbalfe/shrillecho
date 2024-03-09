import os
import re
from datetime import datetime

import requests
import spotipy
from typing import Optional
from selenium.webdriver.firefox.webdriver import WebDriver
from shrillecho.utility import general as sh, scraper
from shrillecho.types.albums import Album
from shrillecho.types.tracks import Track
import hashlib
import json

def get_driver():
    sh.log("Setting up driver")
    return scraper.setup_driver()


def hash_str(url: str):
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def log(message: str):
    print(f"[SHRILLERSPOT]: {message}")


# Utility
def get_artist_id(sp: spotipy.Spotify, artist_name: str) -> Optional[str]:
    """ Given the name of an artist, attempt to find their ID"""

    results = sp.search(q='artist:' + artist_name, type='artist')['artists']['pagination']
    if results:
        # Currently fetch the first result.
        return results[0]['id']
    else:
        print(f"No artist found with the name: {artist_name}")
        return None

def search_query_track(sp: spotipy.Spotify, query: str):
    try:
        track_query = sp.search(query, type="track")
        album_query = sp.search(query, type="album")

        album_id = album_query["albums"]["items"][0]["uri"]
        track_id = track_query["tracks"]["items"][0]["uri"]

        album: Album = Album.from_json(json.dumps(sp.album(album_id)))
        album_track_id = album.tracks.items[0].uri

        track_from_album: Track = Track.from_json(json.dumps(sp.track(album_track_id)))
        track_from_track: Track = Track.from_json(json.dumps(sp.track(track_id)))
    

        return track_from_track.external_ids.isrc, track_from_album.external_ids.isrc, track_from_track.name, track_from_album.name, track_from_album.duration_ms, track_from_track.duration_ms
    except: 
        print("failuire")
        return "","","","","",""



    # first_result = query["tracks"]["items"][0]
    # id = first_result["uri"]
    # print(id)
    # track: Track = Track.from_json(json.dumps(sp.track(id)))
  

    # return track.name, track.artists[0].name, track.external_ids.isrc

# Utility
def get_all_saved_tracks(sp: spotipy.Spotify, user: str, unique: True) -> list[str]:
    """ Given a user id, obtain all their liked songs """

    all_saved_tracks = []
    limit = 50
    offset = 0
    while True:
        response = sp.current_user_saved_tracks(limit=limit, offset=offset)
        saved_tracks = response['pagination']
        if not saved_tracks:
            break
        all_saved_tracks.extend(saved_tracks)
        offset += limit
        print(f"Fetched {offset} tracks...")

    return all_saved_tracks


def convert_isrcs_to_uris(sp, isrcs):
    # Todo - consider the list usage and whether it may produce dupes
    tracks = []
    for isrc in isrcs:
        print(f"progress: {isrc}")
        search = sp.search(f'isrc:{isrc}', type="track", limit=1)
        for track in search['tracks']['pagination']:
            tracks.append(track['uri'])
    return tracks


def crawl_related_artists(sp, artist, collected_artists, depth=0):
    if depth == 15:
        return

    related_artists = sp.artist_related_artists(artist)

    for artist in related_artists['artists']:
        lower_artist = artist['id']
        genres = artist['genres']
        monthly_listeners = artist['followers']['total']

        if lower_artist not in collected_artists:
            if monthly_listeners < 6000:
                if "future bass" in genres:
                    collected_artists.add(lower_artist)
                    crawl_related_artists(sp, lower_artist, collected_artists, depth + 1)

    return collected_artists


def convert_uris_to_isrcs(tracks, client):
    track_data = set()
    with client as client_handle:
        for track in tracks:
            track_response = client_handle.get(f'https://api.spotify.com/v1/tracks/{track}').json()
            track_data.add(track, track_response['external_ids']['isrc'])
    return track_data


def extract_id(uri):
    return uri.split(':')[2]


# def null(tracks, client):
#     access_token, client_token = client.tokens()
#
#     with requests.session() as session:
#         add_headers(session, client_token, access_token)
#
#         session.headers.update({
#             'Client-Token': client_token,
#             'Authorization': f'Bearer {access_token}'
#         })
#
#         isrc_set = set()
#
#         i = 0
#         for track in tracks:
#             dir = './cache/track_isrcs'
#
#             check_path = os.path.join(dir, f'{track.split(":")[2]}_isrc_cache.txt')
#             if os.path.exists(check_path):
#                 with open(check_path, 'r') as read_isrc:
#                     print(f"reading old isrc: {read_isrc.read()}")
#                     isrc_set.add(read_isrc.read())
#                     continue
#
#             try:
#                 track_data = session.get(f'https://api.spotify.com/v1/tracks/{track.split(":")[2]}', verify=True)
#                 track_data_j = track_data.json()
#                 print(f"progress: {i} / {len(tracks)}")
#                 try:
#
#                     isrc = track_data_j['external_ids']['isrc']
#                     isrc_set.add(isrc)
#
#                     if not os.path.exists(dir):
#                         os.makedirs(dir)
#                     path = os.path.join(dir, f'{track.split(":")[2]}_isrc_cache.txt')
#                     with open(path, 'w') as track_isrc_cache:
#                         track_isrc_cache.write(isrc)
#                 except Exception as e:
#
#                     print(f'no isrc found for track: {track_data_j["uri"]} ')
#             except:
#                 if track_data.status_code == 502:
#                     print("502 error investigate")
#                     exit(1)
#             i += 1
#     return isrc_set


def tracks_from_album(sp, album):
    track_ids = []

    tracks = sp.album_tracks(album)
    for track in tracks['pagination']:
        name = track['name']
        if name == 'Life':
            get_track = sp.track(track['uri'], market="US")

            try:
                pass
                # print(f"isrc: {get_track['external_ids']}")
            except:
                print("no linked_from field")

    return track_ids


def print_test():
    print("shrillecho-app test")


def json_debug(json, file_name: str = "quick_debug") -> str:
    # Get the current date and time
    current_time = datetime.now()

    # Format and print the current time in 24-hour clock format
    formatted_time = current_time.strftime("%H-%M-%S")

    with open(f'../data/json_debug/{file_name}_{formatted_time}.json', 'w') as json_debug:
        json_debug.write(json)


def get_artist_id(sp, artist_name):
    results = sp.search(q='artist:' + artist_name, type='artist')['artists']['pagination']
    if results:
        return results[0]['id']
    else:
        print(f"No artist found with the name: {artist_name}")
        return 1


def get_latest_tracks(sp, artist):
    tracks = []

    releases = sp.artist_albums(artist, album_type='single,album,appears_on,compilation', country="US", limit=20,
                                offset=0)

    sorted_data = sorted(releases['pagination'], key=lambda x: datetime.strptime(x['release_date'], "%Y-%m-%d"),
                         reverse=True)
    for item in sorted_data:
        get_album = sp.album(item['uri'])
        print(get_album['copyrights'])
        # print(item)
        # print(f"name: {item['name']} external: {sp.album(item['uri'])['external_ids']}")
        tracks.extend(tracks_from_album(sp, item['uri']))
    print(len(set(tracks)))




def write_songs_to_playlist(sp, name: str, tracks):
    playlist = sp.user_playlist_create(user='alcct3q9gddtkpcyidgx1z9yf', name=name, public=False)
    limit = 50
    for i in range(0, len(tracks), limit):
        sp.playlist_add_items(playlist['id'], list(tracks)[i:i + limit])


def get_followers_from_seed(sp: spotipy.Spotify, seed_user: str, driver: WebDriver, use_cache: bool = True) -> list:
    sh.log("getting followers")
    return scraper.get_followers(driver, seed_user, use_cache)
