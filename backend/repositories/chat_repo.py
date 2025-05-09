from pymongo import MongoClient, ReturnDocument
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from models.chat_model import ChatSession, Message, MessageRole
import os
from pymongo.errors import PyMongoError
from fastapi import HTTPException
import logging

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatRepository:
    def __init__(self):
        try:
            # MongoDB bağlantısı
            self.client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
            self.db = self.client["medeni_hukuk_db"]
            self.chats = self.db["chat_sessions"]

            # Index oluşturma
            self._create_indexes()
            logger.info("MongoDB bağlantısı başarılı ve indexler oluşturuldu")

        except PyMongoError as e:
            logger.error(f"MongoDB bağlantı hatası: {str(e)}")
            raise HTTPException(status_code=500, detail="Database connection failed")

    def _create_indexes(self):
        """Performans için gerekli indexleri oluşturur"""
        self.chats.create_index([("user_id", 1)])
        self.chats.create_index([("session_id", 1)], unique=True)
        self.chats.create_index([("updated_at", -1)])
        self.chats.create_index([("is_active", 1)])

    async def create_session(self, user_id: str, initial_message: Optional[str] = None) -> ChatSession:
        """Yeni sohbet oturumu oluşturur"""
        try:
            session_id = ObjectId().hex
            chat_data = {
                "user_id": user_id,
                "session_id": session_id,
                "title": initial_message[:50] + "..." if initial_message else "Yeni Sohbet",
                "messages": [],
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            result = self.chats.insert_one(chat_data)

            if initial_message:
                await self.add_message(
                    session_id,
                    Message(
                        content=initial_message,
                        role=MessageRole.USER
                    )
                )

            return ChatSession(**{**chat_data, "id": str(result.inserted_id)})

        except PyMongoError as e:
            logger.error(f"Oturum oluşturma hatası: {str(e)}")
            raise HTTPException(status_code=500, detail="Session creation failed")

    async def add_message(self, session_id: str, message: Message) -> ChatSession:
        """Sohbet oturumuna yeni mesaj ekler"""
        try:
            updated_chat = self.chats.find_one_and_update(
                {"session_id": session_id},
                {
                    "$push": {"messages": message.dict()},
                    "$set": {"updated_at": datetime.now()}
                },
                return_document=ReturnDocument.AFTER
            )

            if not updated_chat:
                raise HTTPException(status_code=404, detail="Chat session not found")

            return ChatSession(**updated_chat)

        except PyMongoError as e:
            logger.error(f"Mesaj ekleme hatası: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to add message")

    async def get_session(self, session_id: str) -> ChatSession:
        """Tek bir sohbet oturumunu getirir"""
        try:
            session = self.chats.find_one({"session_id": session_id})

            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")

            return ChatSession(**session)

        except PyMongoError as e:
            logger.error(f"Oturum getirme hatası: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve session")

    async def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[ChatSession]:
        """Kullanıcının sohbet oturumlarını getirir"""
        try:
            query = {"user_id": user_id}
            if active_only:
                query["is_active"] = True

            cursor = self.chats.find(query).sort("updated_at", -1)

            return [ChatSession(**session) for session in cursor]

        except PyMongoError as e:
            logger.error(f"Kullanıcı oturumları getirme hatası: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve user sessions")

    async def close_session(self, session_id: str) -> bool:
        """Sohbet oturumunu kapatır (aktif olmayan olarak işaretler)"""
        try:
            result = self.chats.update_one(
                {"session_id": session_id},
                {"$set": {"is_active": False, "updated_at": datetime.now()}}
            )

            if result.modified_count == 0:
                raise HTTPException(status_code=404, detail="Chat session not found")

            return True

        except PyMongoError as e:
            logger.error(f"Oturum kapatma hatası: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to close session")

    async def update_session_title(self, session_id: str, new_title: str) -> ChatSession:
        """Sohbet başlığını günceller"""
        try:
            updated_session = self.chats.find_one_and_update(
                {"session_id": session_id},
                {"$set": {"title": new_title, "updated_at": datetime.now()}},
                return_document=ReturnDocument.AFTER
            )

            if not updated_session:
                raise HTTPException(status_code=404, detail="Chat session not found")

            return ChatSession(**updated_session)

        except PyMongoError as e:
            logger.error(f"Başlık güncelleme hatası: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update session title")