from abc import ABC, abstractmethod
import datetime
from functools import wraps
import hashlib
import json
from dataclasses import asdict
from pymongo import MongoClient
import redis



class Cache(ABC):

    @abstractmethod
    async def cache_query(self, cache_key: str, cache_update_function, expiry: int, class_type: type, **kwargs):
        pass

class Mongo(Cache):
    def __init__(self, domain: str, port: str, db: str = None):
        self._mongo_client = MongoClient(f"mongodb://{domain}:{port}/")
        self._db = self._mongo_client[db]

    def set_db(self, db: str):
        self._db = self._mongo_client[db]

    async def cache_query(self, cache_key, cache_update_function, expiry, class_type, **kwargs):
        collection = self._db[kwargs.get('col')]

        doc = collection.find_one({'_id': cache_key})

        if doc:
            print(f"using cached: {cache_key}")
           
            doc.pop('expireAt', None) 
            if 'items' in doc and isinstance(doc['items'], list):
                return [class_type.from_json(json.dumps(item)) for item in doc['items']]
            else:
                return class_type.from_json(json.dumps(doc))

        print(f"fetching new: {cache_key}")
        new_data = await cache_update_function()

        if isinstance(new_data, list):
            data_dict = {'_id': cache_key, 'items': [asdict(item) for item in new_data]}
        else:
            data_dict = asdict(new_data)
            data_dict['_id'] = cache_key
      
        data_dict['expireAt'] = datetime.datetime.now() + datetime.timedelta(seconds=expiry)

        collection.replace_one({'_id': cache_key}, data_dict, upsert=True)
        
        return new_data

class Redis(Cache):

    def __init__(self, host: str, port: str):
        self.redis_client = redis.Redis(host=host, port=port, db=0)

    async def cache_query(self, cache_key: str, cache_update_function, expiry, class_type, **kwargs):
        cached_value = self.redis_client.get(cache_key)
        if cached_value:
            retrieved_value = json.loads(cached_value)
            # print(f"[REDIS CACHE] Existing entry {cache_key}")
            if isinstance(retrieved_value, list):
                return [class_type.from_json(json.dumps(item)) for item in retrieved_value]

            return class_type.from_json(json.dumps(retrieved_value))
        else:
            # print(f"[REDIS CACHE] New entry {cache_key}")
            new_value = await cache_update_function()

            if isinstance(new_value, list):
                new_value_dict = [asdict(item) for item in new_value]
            else:
               
                new_value_dict = asdict(new_value)

            self.redis_client.set(cache_key, json.dumps(new_value_dict), ex=expiry)
            
            return new_value


mongo_client = Mongo('localhost', '27017', 'shrillecho')
redis_client = Redis('localhost', '6379')

def cached(cache_key_prefix, class_type, expiry=3600, invalidate_cache=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
     
            args_str = "_".join([str(arg) for arg in args[1:]])
            kwargs_str = "_".join([f"{k}_{v}" for k, v in kwargs.items()])
            dynamic_part = f"{args_str}_{kwargs_str}"

            dynamic_hash = hashlib.sha256(dynamic_part.encode()).hexdigest()


            full_cache_key = f"{cache_key_prefix}_{dynamic_hash}"
        

            # if invalidate_cache:
            #     await CacheManager.invalidate_cache(full_cache_key)

            async def update_function():
                return await func(*args, **kwargs)
            
            return await redis_client.cache_query(full_cache_key, update_function, expiry, class_type)
        return wrapper
    return decorator













