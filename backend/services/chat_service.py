from fastapi import APIRouter, HTTPException
from models.chat_model import ChatRequest, ChatResponse
import openai
import pinecone
from config import settings

router = APIRouter()


# Pinecone ve OpenAI zaten startup'ta başlatıldı

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    try:
        # Embedding oluştur
        embedding = openai.Embedding.create(
            input=request.question,
            model="text-embedding-ada-002",
            api_key=settings.OPENAI_API_KEY
        )["data"][0]["embedding"]

        # Pinecone sorgusu
        index = pinecone.Index(settings.PINECONE_INDEX_NAME)
        results = index.query(vector=embedding, top_k=3, include_metadata=True)

        # Context hazırla
        context = "\n".join([match.metadata["text"] for match in results.matches])

        # GPT-4 ile cevap oluştur
        response = openai.ChatCompletion.create(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "Sen Türk Medeni Kanunu uzmanısın. Sadece verilen bağlama dayanarak cevap ver."},
                {"role": "user", "content": f"Bağlam:\n{context}\n\nSoru: {request.question}"}
            ],
            temperature=0.3
        )

        return {"answer": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))