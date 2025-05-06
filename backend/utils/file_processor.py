import os
import PyPDF2
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from docx import Document


def clean_text(text: str) -> str:
    """Hukuk metinlerine özel temizleme"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'Madde (\d+)', r'\nMADDE \1\n', text)
    return text.strip()


def process_pdf(file_path: str) -> list[dict]:
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        all_chunks = []
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        for page_num, page in enumerate(reader.pages):
            raw_text = page.extract_text() or ""
            cleaned = clean_text(raw_text)
            chunks = splitter.split_text(cleaned)

            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "text": chunk,
                    "page": page_num + 1,
                    "chunk_id": f"{page_num + 1}-{i}"
                })

        return all_chunks


def process_docx(file_path: str) -> list[dict]:
    doc = Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    cleaned = clean_text(full_text)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(cleaned)

    return [{"text": chunk, "page": "", "chunk_id": f"docx-{i}"} for i, chunk in enumerate(chunks)]


def process_txt(file_path: str) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    cleaned = clean_text(text)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(cleaned)

    return [{"text": chunk, "page": "", "chunk_id": f"txt-{i}"} for i, chunk in enumerate(chunks)]


def process_document(file_path: str) -> list[dict]:
    if file_path.endswith(".pdf"):
        return process_pdf(file_path)
    elif file_path.endswith(".docx"):
        return process_docx(file_path)
    elif file_path.endswith(".txt"):
        return process_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
