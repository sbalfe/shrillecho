import re

class Parser:

    @staticmethod
    def parse_id_from_url(url: str):
        
        """ Given a spotify url for a playlist, obtain the ID """
        playlist_regex = r'(?:https:\/\/open\.spotify\.com\/playlist\/)([a-zA-Z0-9]+)'
        matches = re.match(playlist_regex, url)
        if matches:
            return matches.group(1)
        else:
            return False
        

    @staticmethod
    def get_uri(track_link: str):
        """ Extract uri from link via regex """
        track_regex = r"https:\/\/open\.spotify\.com\/track\/([a-zA-Z0-9]+)"

        match = re.search(track_regex, track_link)
        if match:
            uri = match.group(1)
            return uri
        else:
            print("No URI found.")