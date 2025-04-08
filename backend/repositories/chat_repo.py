from pymongo import MongoClient
from datetime import datetime
from models.chat_model import Chat, Message


class ChatRepository:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://gaffartoksoy:<db_password>@medeni-hukuk-tr.yy7hqk0.mongodb.net/?retryWrites=true&w=majority&appName=medeni-hukuk-tr")
        self.db = self.client["medeni_hukuk_db"]
        self.chats = self.db["chats"]

    async def create_chat(self, user_id: str) -> Chat:
        chat = {
            "user_id": user_id,
            "title": "Yeni Sohbet",
            "messages": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = self.chats.insert_one(chat)
        return Chat(**{**chat, "id": str(result.inserted_id)})

    async def add_message(self, chat_id: str, message: Message):
        self.chats.update_one(
            {"_id": chat_id},
            {"$push": {"messages": message.dict()}},
            {"$set": {"updated_at": datetime.now()}}
        )