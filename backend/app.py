from fastapi import FastAPI, Depends
from services.chat_service import ChatService
from services.rag_service import RAGService
from models.chat_model import ChatRequest, QuestionRequest

app = FastAPI()

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