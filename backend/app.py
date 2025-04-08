from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from config import settings
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

app = FastAPI(title="Medeni Hukuk Asistanı API")

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Bağlantısı (Direkt bağlantı)
mongo_client = MongoClient(settings.MONGO_URI)
db = mongo_client[settings.MONGO_DB]

# Dependency
def get_db():
    return db

@app.on_event("startup")
async def startup_event():
    # Pinecone başlatma
    import pinecone
    pinecone.init(
        api_key=settings.PINECONE_API_KEY,
        environment=settings.PINECONE_ENV
    )

@app.get("/")
async def root():
    return {"status": "API aktif", "database": "MongoDB bağlantısı başarılı"}

# Routeları ekle
from services.auth_service import router as auth_router
from services.chat_service import router as chat_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])