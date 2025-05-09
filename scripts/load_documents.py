import os
from dotenv import load_dotenv
from backend.utils.file_processor import process_document
from backend.repositories.vector_repo import VectorRepository
from tqdm import tqdm
import uuid
import asyncio  # Asenkron işlemler için asyncio'yu import et

load_dotenv()

# Asenkron fonksiyon olduğu için, bu fonksiyonu asenkron yapmalısınız
async def load_documents_to_pinecone():
    vector_repo = VectorRepository()
    documents_dir = "data/raw_documents"

    if not os.path.exists(documents_dir):
        print(f"Directory {documents_dir} does not exist")
        return

    for filename in tqdm(os.listdir(documents_dir)):
        if filename.endswith((".pdf", ".docx", ".txt")):
            file_path = os.path.join(documents_dir, filename)
            print(f"Processing {filename}...")

            try:
                chunks = process_document(file_path)
                vectors = []

                for chunk in chunks:
                    vector = {
                        "id": str(uuid.uuid4()),
                        "values": vector_repo._get_embedding(chunk["text"]),
                        "metadata": {
                            "text": chunk["text"],
                            "source": filename,
                            "page": chunk.get("page", ""),
                            "chunk_id": chunk["chunk_id"]
                        }
                    }
                    vectors.append(vector)

                if vectors:
                    # Asenkron fonksiyon olduğu için, burada await kullanmalısınız
                    await vector_repo.upsert_vectors(vectors)
                    print(f"Loaded {len(vectors)} chunks from {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue

# Asenkron fonksiyonları çalıştırmak için asyncio kullanıyoruz
if __name__ == "__main__":
    asyncio.run(load_documents_to_pinecone())
