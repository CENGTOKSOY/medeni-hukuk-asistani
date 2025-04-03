import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re


def clean_text(text: str) -> str:
    """Hukuk metinlerine özel temizleme"""
    text = re.sub(r'\s+', ' ', text)  # Fazla boşlukları temizle
    text = re.sub(r'Madde (\d+)', r'\nMADDE \1\n', text)  # Madde numaralarını vurgula
    return text.strip()


def process_pdf(file_path: str) -> list[str]:
    """PDF'den temizlenmiş chunk'lar çıkarır"""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = " ".join([page.extract_text() for page in reader.pages])

    cleaned = clean_text(text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return splitter.split_text(cleaned)