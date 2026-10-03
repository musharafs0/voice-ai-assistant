import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)

mongo_db = client["voice_ai"]

chat_collection = mongo_db["chat_history"]


# Retrieves the chat history for a specific user from the MongoDB collection.

def get_chat_history(user_id: int, limit: int = 5):
    chats = list(
        chat_collection
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )

    chats.reverse()

    return chats