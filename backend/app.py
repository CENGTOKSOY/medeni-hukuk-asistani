from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from backend.services.chat_service import ChatService
from backend.services.rag_service import RAGService
from backend.models.chat_model import ChatRequest, QuestionRequest

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm origin'lere izin ver (prod ortamında sınırlandırılmalı)
    allow_credentials=True,
    allow_methods=["*"],  # Tüm HTTP metodlarına izin ver
    allow_headers=["*"],  # Tüm başlıklara izin ver
)

#app = FastAPI()

# Ana sayfa olarak index.html döndür
@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

# Dependency Injection
def get_chat_service():
    return ChatService()

def get_rag_service():
    return RAGService()

@app.post("/api/chats")
async def create_chat(service: ChatService = Depends(get_chat_service)):
    return await service.create_chat()

@app.post("/api/ask")
async def ask_question(
    request: QuestionRequest,
    rag: RAGService = Depends(get_rag_service)
):
    return await rag.generate_response(request.question, request.chat_id)
