from typing import Optional


class User:
    def __init__(self, user, sp):
        self.__user = user
        self.__sp = sp

    def get_all_tracks(self, unique=True) -> Optional[set]:

        """ Given a user id , return all unique songs (de-duplicated, not local) """

        all_uris: set = set()
        for playlist in self.__sp.user_playlists(self.__user)['pagination']:
            for item in self.__sp.playlist_items(playlist['uri'])['pagination']:
                try:
                    all_uris.add(item['track']['uri'])
                except TypeError:
                    print("type error")
                    continue
        return all_uris
