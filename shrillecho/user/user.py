from typing import List, Optional

from shrillecho.spotify.client import SpotifyClient
from shrillecho.types.artist_types import Artist, FollowedArtists


class SpotifyUserUtil:

    @staticmethod
    async def collect_artist(sp: SpotifyClient, followed_artist_page: FollowedArtists, artists: List[Artist], after=None):

        if len(followed_artist_page.artists.items) == 0:
            return artists

        followed_artist_page: FollowedArtists = await sp.current_user_followed_artists(limit=50, after=after)

        artists.extend(followed_artist_page.artists.items)

        after = followed_artist_page.artists.items[-1]

        await SpotifyUserUtil.collect_artist(sp, followed_artist_page=followed_artist_page, artists=artists, after=after)


    @staticmethod
    async def get_followed_artists(sp: SpotifyClient) -> List[Artist]:

        artists: List[Artist] = []

        followed_artist_page: FollowedArtists = await sp.current_user_followed_artists(limit=50, after=None)
    
       
        while len(followed_artist_page.artists.items) != 0:
            after = followed_artist_page.artists.items[-1].id
            artists.extend(followed_artist_page.artists.items)
            followed_artist_page: FollowedArtists = await sp.current_user_followed_artists(limit=50, after=after)
           
        return artists