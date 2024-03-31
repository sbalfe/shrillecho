
from dataclasses import asdict
import inspect
import json
from typing import Type, Callable, Any, Coroutine


class Cache:

    @staticmethod
    async def cache_response(cache_key: str, 
                             cache_update_function, 
                             expiry: int, cache_store=None, class_type: Type =None):
            
        cached_value = cache_store.get(cache_key)
        if cached_value:
            print(f"getting cached: {cache_key}")

            
            retrieved_value = json.loads(cached_value)
           
            return class_type.from_json(json.dumps(retrieved_value))
        else:
            print(f"refetching {cache_key}")
            new_value = await cache_update_function()

            new_value_dict = asdict(new_value)
        
            cache_store.set(cache_key, json.dumps(new_value_dict), ex=expiry)
      
            return new_value