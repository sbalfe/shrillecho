import spotipy
from shrillecho.types.album_types import AlbumTracks
from shrillecho.types.playlist_types import PlaylistTracks
from typing import List
from shrillecho.types.track_types import SavedTracks
from shrillecho.utility.general_utility import *
import httpx
import math
import asyncio
import time


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def fetch_header():
   
    with open('.cache', 'r') as file:
        data = json.load(file)
    access_token = data.get('access_token')
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    return headers


async def async_fetch_urls(urls, chunk_size, client, tracks, sp_type):

    """
        Implement better error handling
    """
    for batch in chunks(urls, chunk_size):
        while len(batch) != 0:
            print(f"fetching batch size: {len(batch)}")
            
            responses = await asyncio.gather(*(client.get(url, headers=fetch_header()) for url in batch))
            passed_responses = []
            indices_to_remove = []
            retry = 0
            for idx, r in enumerate(responses):
                if r.status_code == 200:
                    passed_responses.append(r)
                    indices_to_remove.append(idx)
                else:
                    if r.status_code == 429:
                      
                        retry = int(r.headers.get('Retry-After'))
                    else:
                        print(r)
                        exit(1)
            if retry != 0:
                print("rate limit waiting to try again...")
                time.sleep(retry)

            batch = [url for idx, url in enumerate(batch) if idx not in indices_to_remove]
            if len(passed_responses) > 0:
                tracks.extend(sp_fetch(response.json, sp_type) for response in passed_responses)


async def fetch_async(sp: spotipy.Spotify, sp_type, *args, chunk_size=25):

    """
        Figure out the return type method
    """
    
    ep_path = ""
    ep = None

    if sp_type == PlaylistTracks:
    
        ep_path = f"playlists/{args[0]}/tracks"
        ep = sp.playlist_items
    elif sp_type == SavedTracks:
        ep_path = f"me/tracks"
        ep = sp.current_user_saved_tracks
    elif sp_type == AlbumTracks:
        ep_path = f"albums/{args[0]}/tracks"
        ep = sp.album_tracks
    elif sp_type == SavedTracks:
        ep_path = f"me/tracks"
        ep = sp.current_user_saved_tracks
    elif sp_type == UserPlaylist:
        print("user playlists")
        ep_path = f"me/playlists"
        print("current user playlists")
    
        ep = sp.current_user_playlists
    else:
        print("invalid type passed!")
        exit(1)

    async with httpx.AsyncClient() as client:
        urls = []
        limit = 50
   
        initial_item: sp_type = sp_fetch(ep, sp_type, limit=limit, offset=0, *args)
        items: List[sp_type] = [initial_item]
     
        pages = math.ceil(initial_item.total / limit)
      
        for page in range(1, pages):
            urls.append(f"https://api.spotify.com/v1/{ep_path}?limit=50&offset={limit * page}")
            
        await async_fetch_urls(urls, chunk_size, client, items, sp_type)

        """ sort this out """
        unpacked_items = []
        for chunk in items:
            for cube in chunk.items:

                if sp_type == SavedTracks:
                    unpacked_items.append(cube.track)
                else:
                    unpacked_items.append(cube)
        return unpacked_items


async def fetch_async_paginate(sp: spotipy.Spotify, sp_type, url_offset, page_limit, *args, chunk_size=25):
    
    ep_path = ""
    ep = None

    if sp_type == PlaylistTracks:
    
        ep_path = f"playlists/{args[0]}/tracks"
        ep = sp.playlist_items
    elif sp_type == SavedTracks:
        ep_path = f"me/tracks"
        ep = sp.current_user_saved_tracks
    elif sp_type == AlbumTracks:
        ep_path = f"albums/{args[0]}/tracks"
        ep = sp.album_tracks
    elif sp_type == SavedTracks:
        ep_path = f"me/tracks"
        ep = sp.current_user_saved_tracks
    elif sp_type == UserPlaylist:
       
        ep_path = f"me/playlists"

        ep = sp.current_user_playlists
    else:
        print("invalid type passed!")
        exit(1)

    async with httpx.AsyncClient() as client:
        urls = []
        limit = 50

        items: List[sp_type] = []
    
        for page in range(url_offset, url_offset+page_limit):
        
            print(f"https://api.spotify.com/v1/{ep_path}?limit=50&offset={limit * page}")
            urls.append(f"https://api.spotify.com/v1/{ep_path}?limit=50&offset={limit * page}")

        await async_fetch_urls(urls, chunk_size, client, items, sp_type)

        unpacked_items = []
        for chunk in items:
            for cube in chunk.items:
                if sp_type == SavedTracks:
                    unpacked_items.append(cube.track)
                else:
                    unpacked_items.append(cube)
        return unpacked_items