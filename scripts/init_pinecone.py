import pinecone
import os
from dotenv import load_dotenv

load_dotenv()


def initialize_pinecone():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

    if not pinecone_api_key or not pinecone_env:
        raise ValueError("Pinecone credentials not found in environment variables")

    pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)

    index_name = "medeni-hukuk"

    if index_name not in pinecone.list_indexes():
        print(f"Creating index {index_name}...")
        pinecone.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embedding dimension
            metric="cosine",
            pod_type="p1"
        )
        print("Index created successfully!")
    else:
        print(f"Index {index_name} already exists")

    print("Current indexes:", pinecone.list_indexes())


if __name__ == "__main__":
    initialize_pinecone()