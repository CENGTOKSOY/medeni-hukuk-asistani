import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

def initialize_pinecone():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

    if not pinecone_api_key or not pinecone_env:
        raise ValueError("Pinecone credentials not found in environment variables")

    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "medeni-hukuk-danisman"

    # İndeks mevcut değilse oluştur
    if index_name not in pc.list_indexes().names():
        print(f"Creating index {index_name}...")
        pc.create_index(
            name=index_name,
            dimension=3072,  # 'text-embedding-3-large'dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=pinecone_env
            )
        )
        print("Index created successfully!")
    else:
        print(f"Index {index_name} already exists")

    print("Current indexes:", pc.list_indexes().names())

if __name__ == "__main__":
    initialize_pinecone()