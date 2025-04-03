import openai
import pinecone
from typing import List
from models.chat_model import RAGResponse


class RAGService:
    def __init__(self):
        self.embed_model = "text-embedding-ada-002"
        self.llm_model = "gpt-3.5-turbo"

    async def generate_response(self, question: str, chat_id: str) -> RAGResponse:
        # 1. Vektör arama
        query_embed = self._get_embedding(question)
        results = pinecone.index.query(
            vector=query_embed,
            top_k=3,
            include_metadata=True
        )

        # 2. Bağlam oluştur
        context = self._build_context(results.matches)

        # 3. LLM'den yanıt al
        response = openai.ChatCompletion.create(
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

    def _get_embedding(self, text: str) -> List[float]:
        return openai.Embedding.create(
            input=[text],
            model=self.embed_model
        ).data[0].embedding

    def _build_context(self, matches) -> str:
        return "\n\n".join([f"Kaynak: {m.metadata['source']}\nİçerik: {m.metadata['text']}" for m in matches])