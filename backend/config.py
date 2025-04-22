# backend/config.py
from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB = os.getenv("MONGO_DB")

    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")