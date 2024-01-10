from pymongo import MongoClient
import json

def load_from_dump():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['PlayersDB']
    collection = db['players']
    
    