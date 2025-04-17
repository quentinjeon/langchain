from fastapi import Depends
from pymongo import MongoClient
import pinecone, os

def get_mongo():
    client = MongoClient(os.getenv("MONGO_URL"))
    return client[os.getenv("MONGO_DB")]

def get_pinecone():
    pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
    return pinecone.Index(os.getenv("PINECONE_INDEX")) 