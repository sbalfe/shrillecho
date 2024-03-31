import re
import shrillecho.utility.archive_maybe_delete.general as gen
from shrillecho.types.playlist_types import Playlist as Playlist_t

class Playlist:
    def __init__(self, sp,  playlist: Playlist_t = None):
        self.__playlist: Playlist_t = playlist
        self.__sp = sp

    def get_tracks(self):
        track_ids = []

        results = self.__sp.playlist_items(self.__playlist.id)
        tracks = results['pagination']

        while results['next']:
            results = self.__sp.next(results)
            tracks.extend(results['pagination'])

        for item in tracks:
            track = item['track']
            if track is None:
                break
            track_ids.append(track['id'])

        return track_ids

    def get_all_uris(self):

        """ Given a playlist return all the uris"""
    
        playlist = "next"
        track_uris = []
        offset = 0
        limit = 1
        while playlist["next"]:
            playlist = self.__sp.playlist_items(self.__playlist, offset=offset, limit=limit)
            tracks = playlist['pagination']
            if not tracks:
                break
            track_uris.extend(tracks)
            offset += limit

        return track_uris
    
    

    def get_all_isrcs(self):
        """ Given a playlist return every single isrc (if it exists i.e not local file or copyrighted track)"""
        isrcs = set()
        for track in self.playlist_pagination():
            if track is None:
                continue
            try:
                isrcs.add((gen.extract_id(track['uri']), track['external_ids']['isrc']))
            except:
                matches = re.findall(r'\b\w*local\w*\b', track['uri'])
                if not matches:
                    print(f"no isrc for this track: {track['uri']}")
                else:
                    print(f"Local file detected, ignoring")
        return isrcs

    def playlist_pagination(self):

        """ Given a playlist yield the next page of results from it"""

        offset = 0
        limit = 100
        resp = self.__sp.playlist_items(self.__playlist, limit=limit)
        for item in resp['pagination']:
            if item['track'] is None:
                print(item)
            yield item['track']
        while resp['next'] is not None:
            offset += limit
            resp = self.__sp.playlist_items(self.__playlist, limit=limit, offset=offset)
            for item in resp['pagination']:
                if item['track'] is None:
                    print(item)
                yield item['track']
