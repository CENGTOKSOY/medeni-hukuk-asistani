from typing import List, Optional
from fastapi import HTTPException
from backend.models.chat_model import ChatSession, Message, MessageRole
from backend.repositories.vector_repo import VectorRepository
from backend.utils.file_processor import process_document
from openai import OpenAI
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

class ChatService:
    def __init__(self):
        self.vector_repo = VectorRepository()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # OpenAI nesnesi

    async def generate_response(self, user_id: str, session_id: str, question: str) -> str:
        try:
            # Step 1: Get relevant context from vector DB
            embedding = await self._get_embedding(question)
            query_result = await self.vector_repo.query_vectors(embedding)

            # Step 2: Build context from retrieved documents
            context = self._build_context(query_result.matches)

            # Step 3: Generate response using LLM
            response = await self._call_llm(user_id, session_id, question, context)

            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding

    def _build_context(self, matches: List[dict]) -> str:
        context = ""
        for match in matches:
            context += f"Document excerpt: {match['metadata']['text']}\n"
            context += f"Source: {match['metadata']['source']}\n\n"
        return context

    async def _call_llm(self, user_id: str, session_id: str, question: str, context: str) -> str:
        prompt = f"""
        You are a legal assistant specialized in Turkish Civil Law. Answer the question based on the context below.
        Provide detailed, accurate information with references to relevant laws when possible.

        Context:
        {context}

        Question: {question}
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    async def create_chat_session(self, user_id: str, title: Optional[str] = None) -> ChatSession:
        return ChatSession(
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            title=title or "New Chat"
        )
