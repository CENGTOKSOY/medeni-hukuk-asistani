from openai import OpenAI
from pinecone import Pinecone
from typing import List
from backend.models.chat_model import RAGResponse

class RAGService:
    def __init__(self):
        self.embed_model = "text-embedding-3-large"
        self.llm_model = "gpt-3.5-turbo"
        self.client = OpenAI()  # OpenAI nesnesi
        self.pinecone = Pinecone()  # Pinecone nesnesi
        self.index = self.pinecone.Index("medeni-hukuk-danisman")  # Pinecone'daki index adın

    async def generate_response(self, question: str, chat_id: str) -> RAGResponse:
        # 1. Vektör arama
        query_embed = await self._get_embedding(question)
        results = self.index.query(
            vector=query_embed,
            top_k=3,
            include_metadata=True
        )

        # 2. Bağlam oluştur
        context = self._build_context(results.matches)

        # 3. LLM'den yanıt al
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "Sen bir medeni hukuk asistanısın."},
                {"role": "user", "content": f"Bağlam: {context}\n\nSoru: {question}"}
            ],
            temperature=0.3
        )

        return RAGResponse(
            answer=response.choices[0].message.content,
            references=[m.metadata['source'] for m in results.matches]
        )

    async def _get_embedding(self, text: str) -> list:
        response = self.client.embeddings.create(
            model=self.embed_model,
            input=text
        )
        return response.data[0].embedding

    def _build_context(self, matches) -> str:
        return "\n\n".join(
            [f"Kaynak: {m.metadata['source']}\nİçerik: {m.metadata['text']}" for m in matches]
        )
