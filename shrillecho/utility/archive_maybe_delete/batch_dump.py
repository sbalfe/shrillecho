#  async def _async_fetch_urls(self, urls, chunk_size, client, tracks, sp_type):
#         def chunks(lst, n):
#             for i in range(0, len(lst), n):
#                 yield lst[i:i + n]
          
    
#         if self.auth:
#             self.access_token = self.auth
#         elif self.auth_flow:
#             self.access_token = self.auth_flow.get_access_token()
#         else:
#             raise Exception(message="No authorization provided to the client")

#         print(self.access_token)
#         headers = {"Authorization" : f"Bearer { self.access_token}"}

#         for batch in chunks(urls, chunk_size):
#             while len(batch) != 0:
#                 print(f"fetching batch size: {len(batch)}")
#                 responses = await asyncio.gather(*(client.get(url, headers=headers) for url in batch))
#                 passed_responses = []
#                 indices_to_remove = []
#                 retry = 0
#                 for idx, r in enumerate(responses):
#                     if r.status_code == 200:
#                         passed_responses.append(r)
#                         indices_to_remove.append(idx)
#                         # cache the get response for this URL, for retry purposes , wipe it 
#                         # after as we have a complete caching layer, so we dont really want to have this fully caching
#                         # always but maybe consider.
#                     else:
#                         if r.status_code == 429:
#                             retry = int(r.headers.get('Retry-After'))
#                         else:
#                             self.batch_errors += 1 
#                             raise SpotifyClient.ShrillechoException("Batch Error, setting batch size to 10", error_code=r.status_code)
#                 if retry != 0:
#                     print("rate limit waiting to try again...")
#                     await asyncio.sleep(retry)

#                 batch = [url for idx, url in enumerate(batch) if idx not in indices_to_remove]
#                 if len(passed_responses) > 0:
#                     tracks.extend(sp_fetch(response.json, sp_type) for response in passed_responses)
            
#     # add query params via dict
#     async def _batch_request(self, ep_path: str, initial_item , sp_type: Type[T], query_params = None, override_urls = None, chunk_size=25):
#         async with httpx.AsyncClient() as client:
#             urls = []
#             limit = 50
    
#             items: List[sp_type] = [initial_item]
        
#             pages = math.ceil(initial_item.total / limit)
        
#             for page in range(1, pages):
#                 urls.append(f"https://api.spotify.com/v1/{ep_path}?limit=50&offset={limit * page}")
                
#             try:
#                 await self._async_fetch_urls(urls, chunk_size, client, items, sp_type)
#             except SpotifyClient.ShrillechoException as e:
#                  if self.batch_errors > 3:
#                       raise Exception("Fatal Error, Batch request failed after 3 retries")
#                  items: List[sp_type] = [initial_item]
#                  await self._async_fetch_urls(urls=urls, client=client, tracks=items, sp_type=sp_type, chunk_size=10)

#             self.batch_errors = 0

#             """ sort this out, essentially this batcher is designed for paginated requests
#                 so we want the items bit all collated into one sequential list
#             """
#             unpacked_items = []
        
#             for chunk in items:
#                 for cube in chunk.items:
#                         unpacked_items.append(cube)

#             return unpacked_items
        
# async def current_user_saved_tracks_b(self, chunk_size = 25, track_list=True) -> List[SavedTrack] | SavedTracks:
 
#         async def batch_request() -> List[SavedTrack]:
#             initial_item = await self._get(f"me/tracks?offset={0}&limit={50}", response_type=SavedTracks)
#             return await self._batch_request(ep_path="me/tracks", 
#                                         initial_item=initial_item,
#                                             sp_type=SavedTracks,
#                                             chunk_size=chunk_size)

#         saved_tracks: List[SavedTrack] = await redis_client.cache_query(cache_key="my_tracks_0", 
#                                           cache_update_function=batch_request, 
#                                           expiry=3600, 
#                                           class_type=SavedTrack)
#         if track_list:
#             tracks: List[Track] = []
#             for item in saved_tracks:
#                 tracks.append(item.track)
#             return tracks

#         return await saved_tracks

# async def current_user_saved_playlists(self,limit: int = None, 
#                                         offset: int = None,
#                                           batch=False,
#                                           chunk_size=25, invalidate_cache=False) -> List[SimplifiedPlaylistObject] | UserPlaylists:
        
#         cache_key = "my_playlists_new_cache"
#         ep = "me/playlists"
        
#         if not batch:
#             return await self._get(f"{ep}?offset={offset}&limit={limit}", response_type=UserPlaylists)
        
#         async def batch_request() -> List[SimplifiedPlaylistObject]:
#             initial_item = await self._get(f"{ep}?offset={0}&limit={50}", response_type=UserPlaylists)
#             return await self._batch_request(ep_path=ep, 
#                                         initial_item=initial_item,
#                                             sp_type=UserPlaylists,
#                                             chunk_size=chunk_size)
#         if invalidate_cache:
#             self.redis.delete(cache_key)

#         return await redis_client.cache_query(cache_key=cache_key, 
#                                           cache_update_function=batch_request, 
#                                           expiry=3600, 
#                                           class_type=SimplifiedPlaylistObject)

# async def playlist_tracks(self, playlist_id, limit: int = None, 
#                                         offset: int = None,
#                                           batch=True,
#                                           chunk_size=25, invalidate_cache=False, track_list=True) -> List[PlaylistTrack] | List[Track] | PlaylistTracks:
#         if not batch:
#             return await self._get(f"playlists/{playlist_id}/tracks?offset={offset}&limit={limit}", response_type=PlaylistTracks)
        
#         async def batch_request() -> List[PlaylistTrack]:
#             initial_item = await self._get(f"playlists/{playlist_id}/tracks?offset={0}&limit={50}", response_type=PlaylistTracks)
#             return await self._batch_request(ep_path=f"playlists/{playlist_id}/tracks", 
#                                         initial_item=initial_item,
#                                             sp_type=PlaylistTracks,
#                                             chunk_size=chunk_size)
#         if invalidate_cache:
#             self.redis.delete(f"playlist_tracks_{playlist_id}")

#         playlist_tracks: List[PlaylistTrack] = await redis_client.cache_query(cache_key=f"playlist_tracks_{playlist_id}", 
#                                           cache_update_function=batch_request, 
#                                           expiry=3600, 
#                                           class_type=PlaylistTrack)
#         if track_list:
#             tracks: List[Track] = []
#             for item in playlist_tracks:
#                 tracks.append(item.track)
#             return tracks
        
#         return playlist_tracks

#  async def album_tracks(self, album: str, batch=True, chunk_size=25) -> List[SimplifiedTrack]:
#         async def batch_request() -> List[SimplifiedTrack]:


#             initial_item = await self._get(f"albums/{album}/tracks?offset={0}&limit={50}", response_type=AlbumTracks)
#             return await self._batch_request(ep_path=f"albums/{album}/tracks", 
#                                         initial_item=initial_item,
#                                             sp_type=AlbumTracks,
#                                             chunk_size=chunk_size)

#         artist_albums: List[SimplifiedTrack] = await redis_client.cache_query(cache_key=f"album_tracks_{album}", 
#                                         cache_update_function=batch_request, 
#                                         expiry=3600, 
#                                         class_type=SimplifiedTrack)
#         return artist_albums

#    async def artist_albums_bat(self, artist: str, batch=True, offset=0, include_groups="album,single,appears_on,compilation", chunk_size=25) -> List[SimplifiedAlbum]:

#         if not batch:   
        
#             return await self._get(f"artists/{artist}/albums?offset={offset}&limit={50}", response_type=ArtistAlbums)
            
#         async def batch_request() -> List[SimplifiedAlbum]:

#             query_params = {}

#             query_params['include_groups'] = include_groups

#             initial_item = await self._get(f"artists/{artist}/albums?offset={0}&limit={50}", response_type=ArtistAlbums)
#             return await self._batch_request(ep_path=f"artists/{artist}/albums", 
#                                         initial_item=initial_item,
#                                             sp_type=ArtistAlbums,
#                                             chunk_size=chunk_size,
#                                             query_params=query_params)

#         artist_albums: List[SimplifiedAlbum] = await redis_client.cache_query(cache_key=f"artist_albums_{artist}", 
#                                           cache_update_function=batch_request, 
#                                           expiry=3600, 
#                                           class_type=SimplifiedAlbum)
#         return artist_albums

    # async def user_playlists(self, user:str, batch=True, chunk_size=25) -> List[SimplifiedPlaylistObject]:
    #     if not batch:
    #         pass 

    #     async def batch_request() ->  List[SimplifiedPlaylistObject]:

    #         initial_item = await self._get(f"users/{user}/playlists?offset={0}&limit={50}", response_type=UserPlaylists)
    #         return await self._batch_request(ep_path=f"users/{user}/playlists", 
    #                                     initial_item=initial_item,
    #                                         sp_type=UserPlaylists,
    #                                         chunk_size=chunk_size)

    #     artist_albums: List[SimplifiedPlaylistObject] = await redis_client.cache_query(cache_key=f"user_playlists_{user}", 
    #                                       cache_update_function=batch_request, 
    #                                       expiry=3600, 
    #                                       class_type=SimplifiedPlaylistObject)
    #     return artist_albums