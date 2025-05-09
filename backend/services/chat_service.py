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
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.legal_prompt = """
        Sen bir Türk Medeni Hukuku uzmanı asistanısın. Sadece medeni hukukla ilgili soruları yanıtlayabilirsin.
        Eğer soru medeni hukuk dışında bir konuyla ilgiliyse, yanıt vermemelisin.
        Yanıtlarında mutlaka ilgili yasa maddelerine ve kaynaklara atıfta bulunmalısın.
        """

    async def generate_response(self, user_id: str, session_id: str, question: str) -> str:
        try:
            # Önce sorunun hukuki olup olmadığını kontrol et
            is_legal = await self._check_if_legal_question(question)
            if not is_legal:
                return "Ben bir medeni hukuk asistanıyım. Sadece medeni hukukla ilgili soruları yanıtlayabilirim. Lütfen medeni hukukla ilgili bir soru sorun."

            # Step 1: Get relevant context from vector DB
            embedding = await self._get_embedding(question)
            query_result = await self.vector_repo.query_vectors(embedding)

            # Step 2: Build context from retrieved documents
            context = self._build_context(query_result.matches)

            # Step 3: Generate response using LLM
            response = await self._call_llm(user_id, session_id, question, context)

            # Kaynakları ekle
            sources = [match['metadata']['source'] for match in query_result.matches]
            if sources:
                response += "\n\nKaynaklar:\n" + "\n".join(f"- {source}" for source in sources)

            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def _check_if_legal_question(self, question: str) -> bool:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Soru hukuki mi değil mi belirle."},
                {"role": "user",
                 "content": f"Bu soru hukuki bir soru mu? (sadece 'evet' veya 'hayır' yanıtla): {question}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.lower().strip() == "evet"

    async def _get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding

    def _build_context(self, matches: List[dict]) -> str:
        context = ""
        for match in matches:
            context += f"Belge: {match['metadata']['text']}\n"
            context += f"Kaynak: {match['metadata']['source']}\n\n"
        return context

    async def _call_llm(self, user_id: str, session_id: str, question: str, context: str) -> str:
        prompt = f"""
        {self.legal_prompt}

        Bağlam:
        {context}

        Soru: {question}
        """

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.legal_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    async def create_chat_session(self, user_id: str, title: Optional[str] = None) -> ChatSession:
        return ChatSession(
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            title=title or "Yeni Sohbet"
        )