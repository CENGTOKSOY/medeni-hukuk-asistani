from openai import OpenAI
from pinecone import Pinecone
from typing import List
from backend.models.chat_model import RAGResponse
import os
from dotenv import load_dotenv

load_dotenv()


class RAGService:
    def __init__(self):
        self.embed_model = "text-embedding-3-large"
        self.llm_model = "gpt-4"  # GPT-4'e güncellendi
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pinecone.Index("medeni-hukuk-danisman")
        self.legal_prompt = """
        Sen bir Türk Medeni Hukuku uzmanı asistanısın. Sadece medeni hukukla ilgili soruları yanıtlayabilirsin.
        Yanıtlarında mutlaka ilgili yasa maddelerine atıfta bulunmalısın.
        """

    async def generate_response(self, question: str, chat_id: str) -> RAGResponse:
        # 1. Sorunun hukuki olup olmadığını kontrol et
        is_legal = await self._check_if_legal_question(question)
        if not is_legal:
            return RAGResponse(
                answer="Ben bir medeni hukuk asistanıyım. Sadece medeni hukukla ilgili soruları yanıtlayabilirim.",
                references=[]
            )

        # 2. Vektör arama
        query_embed = await self._get_embedding(question)
        results = self.index.query(
            vector=query_embed,
            top_k=3,
            include_metadata=True
        )

        # 3. Bağlam oluştur
        context = self._build_context(results.matches)

        # 4. LLM'den yanıt al
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": self.legal_prompt},
                {"role": "user", "content": f"Bağlam: {context}\n\nSoru: {question}"}
            ],
            temperature=0.3
        )

        answer = response.choices[0].message.content
        references = [m.metadata['source'] for m in results.matches]

        # Kaynakları yanıta ekle
        if references:
            answer += "\n\nKaynaklar:\n" + "\n".join(f"- {ref}" for ref in references)

        return RAGResponse(
            answer=answer,
            references=references
        )

    async def _check_if_legal_question(self, question: str) -> bool:
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "Soru hukuki mi değil mi belirle."},
                {"role": "user",
                 "content": f"Bu soru hukuki bir soru mu? (sadece 'evet' veya 'hayır' yanıtla): {question}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.lower().strip() == "evet"

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