from pymongo.mongo_client import MongoClient
from rich import print

class MongoDB:
    def __init__(self, url: str, database: str):
        client = MongoClient(url)
        self.database = client[database]
        
    def post(self, data: list, collection: str):
        conn = self.database[collection]
        for item in data:
            conn.insert_many(item)
        print(f"""Inserted {len(data)} documents in collection {collection}""")

    def update(self, collection: str, target: dict, value: dict):
        conn = self.database[collection]        
        conn.update_one(
            target, value
        )

    def find(self, collection: str, query: dict = None):
        conn = self.database[collection]
        documents = []
                
        for document in conn.find(query):
            documents.append(document)
        
        return documents