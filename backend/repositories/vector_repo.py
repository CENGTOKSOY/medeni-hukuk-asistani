import pinecone
from typing import List, Optional
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()


class VectorRepository:
    def __init__(self):
        pinecone_api_key = os.getenv("pcsk_6nfeYW_BfsQMdyByy43Ck42jwBtyeFZnoWseXR1cnQQfJqRaAbWBh8gbwhvw4SofP1LV1t")
        pinecone_env = os.getenv("medeni-hukuk-tr")

        if not pinecone_api_key or not pinecone_env:
            raise ValueError("Pinecone credentials not configured")

        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        self.index_name = "medeni-hukuk"

        if self.index_name not in pinecone.list_indexes():
            self._create_index()

        self.index = pinecone.Index(self.index_name)

    def _create_index(self, dimension=1536, metric="cosine"):
        pinecone.create_index(
            name=self.index_name,
            dimension=dimension,
            metric=metric,
            pod_type="p1"
        )

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