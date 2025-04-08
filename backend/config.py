class Settings:
    # MongoDB Ayarları
    MONGO_URI = "mongodb+srv://gaffartoksoy:1fB2Bkn7zTUSPWj1@medeni-hukuk-tr.yy7hqk0.mongodb.net/?retryWrites=true&w=majority&appName=medeni-hukuk-tr"
    MONGO_DB = "medeni_hukuk"

    # Pinecone Ayarları
    PINECONE_API_KEY = "pcsk_6nfeYW_BfsQMdyByy43Ck42jwBtyeFZnoWseXR1cnQQfJqRaAbWBh8gbwhvw4SofP1LV1t"
    PINECONE_ENV = "medeni-hukuk-tr"
    PINECONE_INDEX_NAME = "medeni-hukuk-tr"

    # OpenAI
    OPENAI_API_KEY = "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"

    # JWT
    SECRET_KEY = "9a8f7e6d5c4b3a29182736455463728192"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30


settings = Settings()