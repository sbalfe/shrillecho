from pymongo import MongoClient
import json
class Mongo:
    def __init__(self, domain: str, port: str, db: str = None):
        self._mongo_client = MongoClient(f"mongodb://{domain}:{port}/")
        self._db = self._mongo_client[db]

    def set_db(self, db: str):
        self._db = self._mongo_client[db]

    def write_collection(self, col: str, data):
        collection = self._db[col]
        collection.insert_one(data)














