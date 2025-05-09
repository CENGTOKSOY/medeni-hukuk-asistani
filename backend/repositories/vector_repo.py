from typing import List, Optional
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings  # ✅ Embedding modeli eklendi

load_dotenv()


class VectorRepository:
    def __init__(self):
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_env = os.getenv("PINECONE_ENVIRONMENT")  # Örn: "us-west-2"

        if not pinecone_api_key or not pinecone_env:
            raise ValueError("Pinecone credentials not configured")

        self.index_name = "medeni-hukuk"

        # Pinecone istemcisi başlat
        self.pc = Pinecone(api_key=pinecone_api_key)

        # Index yoksa oluştur
        if self.index_name not in self.pc.list_indexes().names():
            self._create_index()

        # Index'e erişim sağla
        self.index = self.pc.Index(self.index_name)

        # ✅ Embedding modelini başlat
        self.embed_model = OpenAIEmbeddings()

    def _create_index(self, dimension=1536, metric="cosine"):
        self.pc.create_index(
            name=self.index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud="aws",
                region=os.getenv("PINECONE_ENVIRONMENT")
            )
        )

    def _get_embedding(self, text: str) -> List[float]:
        """
        ✅ Belirli bir metni OpenAI kullanarak embed eder.
        """
        return self.embed_model.embed_query(text)

    async def upsert_vectors(self, vectors: List[dict]):
        try:
            return self.index.upsert(vectors=vectors)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def query_vectors(self, vector: List[float], top_k: int = 5, namespace: str = "",
                            filter: Optional[dict] = None):
        try:
            return self.index.query(
                vector=vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=True
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_vectors(self, ids: List[str], namespace: str = ""):
        try:
            return self.index.delete(ids=ids, namespace=namespace)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
