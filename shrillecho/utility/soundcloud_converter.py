from typing import Tuple
from io import BytesIO
from itertools import combinations
from typing import List, Set
from dotenv import load_dotenv
from soundcloud import SoundCloud, AlbumPlaylist
from spotipy import Spotify
import requests
from shrillecho.types.soundcloud_types import SoundCloudTrack, UsefulMeta
from shrillecho.types.track_types import Track, TrackSearch
import json
from dataclasses import dataclass
import httpx
import asyncio
from dotenv import load_dotenv
import os
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np



class SoundCloudConverter:
    @dataclass
    class ResolvePlaylist:
        name: str
        total_tracks: str
        tracks: List[SoundCloudTrack]

    @dataclass
    class SoundCloudMeta():
        title: str
        description: str
        isrc: str
        artist: str
        username: str
        created_at: str
        duration: int
        full_duration: int
        release_date: str

    __base_url = 'https://api-v2.soundcloud.com'
    __spotify_base_url = 'https://api.spotify.com/v1'

    __soundcloud_headers = {
        "Authorization": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    }
   



    def __init__(self, sp: Spotify, sc: SoundCloud, token):
        self.__sp = sp
        self.__sc = sc
        self.__spot_token = token

    @staticmethod
    def get_header():
        with open('.cache', 'r') as file:
            data = json.load(file)
        access_token = data.get('access_token', None)

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        return headers

    @staticmethod
    def gen_combos(meta: List[str], max_length: int = 3) -> Set[str]:
        
        def clean_tokens(strings, characters_to_remove):
            translation_table = str.maketrans('', '', characters_to_remove)
            cleaned_strings = [s.translate(translation_table) for s in strings]
            stripped_strings = [str.strip() for str in cleaned_strings]
            return stripped_strings
        
        tokens = set(clean_tokens(meta, ",@#()"))
        permuted_combos = set()
        for r in range(1, max_length + 1):
            for c in combinations(tokens, r):
                # for p in permutations(c): // removing permutations as optimisation
                permuted_combos.add(' '.join(c))
        return permuted_combos

    @staticmethod
    def tfidf_similarity(new_string, string_list):
        combined_text = " ".join(string_list)
        documents = [combined_text, new_string]
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity[0][0]

    async def _get_soundcloud_tracks(self, sc_ids: List[int]) -> List[SoundCloudTrack]:
        async with httpx.AsyncClient() as client:
            responses = await asyncio.gather(
                *(client.get(f"{self.__base_url}/tracks/{sc_id}", headers=self.__soundcloud_headers) for sc_id in
                  sc_ids))
        tracks = [SoundCloudTrack.from_json(json.dumps(resp.json())) for resp in responses]
        return tracks

    async def _resolve_soundcloud_tracks(self, sc_link: str) -> ResolvePlaylist:
        sc_playlist: AlbumPlaylist = self.__sc.resolve(sc_link)
        sc_tracks: List[SoundCloudTrack] = await self._get_soundcloud_tracks(
            [sc_track.id for sc_track in sc_playlist.tracks])
        return SoundCloudConverter.ResolvePlaylist(tracks=sc_tracks, name=sc_playlist.title,
                                                   total_tracks=sc_playlist.track_count)

    async def async_search(self, queries: List[str], search_type: str) -> List[TrackSearch]:
        '''
            Given a set of search combos, for each one return the first 50 results for artist hits.
        '''
        params_list = []
        for q in queries:
            params_list.append(
                {
                    'q': q,
                    'limit': 50,
                    'offset': 0,
                    'type': search_type,
                }
            )

        spot_headers = {
            "Authorization": f"Bearer {self.__spot_token}"
        }

        async with httpx.AsyncClient() as client:
            responses = await asyncio.gather(
                *(client.get(f"{self.__spotify_base_url}/search", headers=spot_headers, params=param) for
                  param in params_list))

        for resp in responses:
            if resp.status_code != 200:
                print(resp.text)
                print("rate limit error")
                exit(0)

        searches = [TrackSearch.from_json(json.dumps(resp.json())) for resp in responses]
        return searches

    async def fetch_pages(self, combos):
        def chunks(lst, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        chunk_size = 50
        sleep = False
        search_combos = combos
        if len(combos) > 100:
            search_combos = list(combos)[20:40]
            chunk_size = 10
            sleep = True
        combo_chunks = [list(chunk) for chunk in chunks(list(search_combos), chunk_size)]
        all_pages: List[TrackSearch] = []
        for combo_chunk in combo_chunks:
            if sleep:
                time.sleep(4)
            all_pages.extend(await self.async_search(combo_chunk, search_type='track'))
        return all_pages

    def analyse_pages(self, all_pages: List[TrackSearch], combos, meta: UsefulMeta):
        ids_added = []
        scores: List[Tuple[int, Track]] = []
        for page in all_pages:
            try:
                for track in page.tracks.items:
                    track_score = SoundCloudConverter.tfidf_similarity(track.name, combos)
                    artist_score = SoundCloudConverter.tfidf_similarity(track.artists[0].name, combos)
                    if track_score > 0.2 and artist_score > 0.1:
                        if track.id not in ids_added:
                            if abs(track.duration_ms - meta.duration) < 1500:
                                scores.append((track_score, track))
                                ids_added.append(track.id)
            except Exception as e:
                print("error", str(e))
                exit(0)

        return scores

    @staticmethod
    def download_image(url):
        response = requests.get(url)
        if response.status_code == 200:
            image_bytes = BytesIO(response.content)
            img = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), -1)
            if img is not None:
                return img
            else:
                raise Exception(f"Failed to decode image from URL: {url}")
        else:
            raise Exception(f"Failed to download image from URL: {url}")

    def compare_images_by_url(self, url1, url2):
        img1 = SoundCloudConverter.download_image(url1)
        img2 = SoundCloudConverter.download_image(url2)
        if img1 is not None and img2 is not None:
            img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            common_size = (100, 100)
            img1_resized = cv2.resize(img1_gray, common_size)
            img2_resized = cv2.resize(img2_gray, common_size)
            similarity_score = ssim(img1_resized, img2_resized)
            return similarity_score

    async def resolve_combinations(self, combos, meta: UsefulMeta) -> Track:

        all_pages: List[TrackSearch] = await self.fetch_pages(combos)
        time.sleep(1)

        scores: List[Tuple[int, Track]] = self.analyse_pages(all_pages, combos, meta)

        if len(scores) > 0:
            for item in scores:
                print(item[1].name, item[0])

            best_score = max(scores, key=lambda x: x[0])

            if best_score[0] < 0.4:
                image_score = self.compare_images_by_url(meta.artwork_url, best_score[1].album.images[2].url)
                if image_score > 0.7:
                    print("passed via image check")
                    return best_score[1]
                else:
                    print("failed image check")
                    return None

            print("passed via being similar enough already")
            return best_score[1]

    async def _search(self, sc_track_meta: UsefulMeta) -> Track:

        combos = SoundCloudConverter.gen_combos(meta=sc_track_meta.meta_list)
        return await self.resolve_combinations(combos, sc_track_meta)

    def _try_isrc_conversion(self, meta: UsefulMeta) -> str | None:
        try:
            isrc_search: TrackSearch = TrackSearch.from_json(json.dumps(self.__sp.search(f'isrc:{meta.isrc}', type='track')))
            return isrc_search.tracks.items[0]
        except:
            return None

    async def _attempt_conversion(self, sc_track_meta, index: int) -> Track:
        sp_track: Track = self._try_isrc_conversion(sc_track_meta)
        if sp_track:
            print(
                f'[ISRC MATCH] SPOTIFY {sp_track.name} | {sp_track.artists[0].name} | SOUNDCLOUD {sc_track_meta.title} | {sc_track_meta.artist}')
            return sp_track
        else:
            print(f'[NO VALID ISRC] {sc_track_meta.title}')
            track: Track = await self._search(sc_track_meta)
            if track:
                print(
                    f'[SEARCH MATCH] SPOTIFY {track.name} | {track.artists[0].name} | SOUNDCLOUD {sc_track_meta.title} | {sc_track_meta.artist}')
                return track
        return None

    async def convert(self, track=None, playlist: str = None):
        if playlist:
            sc_playlist: SoundCloudConverter.ResolvePlaylist = await self._resolve_soundcloud_tracks(playlist)
            converted = 0
            pl_ids = []
            for idx, sc_track in enumerate(sc_playlist.tracks):
                if idx > 50:
                    track: Track = await self._attempt_conversion(sc_track.useful_meta, idx)
                    if track:
                        pl_ids.append(track.id)
                        converted += 1
            self.create_playlist_with_tracks(sc_playlist.name, pl_ids)

        elif track:
            print("[SHRILLECHO] Converting track")
            sc_track = self.__sc.resolve(track)
            tracks: List[SoundCloudTrack] = await self._get_soundcloud_tracks([sc_track.id])
        
            track: Track = await self._attempt_conversion(tracks[0].useful_meta, 0)
            return track

    def create_playlist_with_tracks(self, playlist_name, track_ids):

        playlist = self.__sp.user_playlist_create('alcct3q9gddtkpcyidgx1z9yf', playlist_name, public=True)

        # Split track_ids into batches of 50 (maximum allowed per request)
        batch_size = 50
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            self.__sp.playlist_add_items(playlist['id'], batch)

        print(f'Playlist "{playlist_name}" with {len(track_ids)} tracks created successfully.')
