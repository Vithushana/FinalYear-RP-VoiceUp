import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/voiceup")
client = MongoClient(MONGO_URI)

# Fix: explicitly check for None instead of truth-testing
default_db = client.get_default_database()
db = default_db if default_db is not None else client["voiceup"]

# Ensure unique index on users.email
users = db["users"]
users.create_index([("email", ASCENDING)], unique=True)
