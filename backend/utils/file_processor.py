import os
import PyPDF2
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from docx import Document
from typing import List, Dict
import uuid


def determine_document_type(file_path: str) -> str:
    """Dosya adına ve içeriğine göre belge türünü belirler"""
    filename = os.path.basename(file_path).lower()

    if 'emsal' in filename or 'karar' in filename or 'yargıtay' in filename:
        return 'precedent'
    elif 'kanun' in filename or 'madde' in filename or 'yasa' in filename:
        return 'law'
    elif 'kitap' in filename or 'doktrin' in filename or 'makale' in filename:
        return 'commentary'
    else:
        return 'other'


def clean_text(text: str) -> str:
    """Hukuk metinlerine özel temizleme"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'Madde (\d+)', r'\nMADDE \1\n', text)
    text = re.sub(r'(YARGITAY.*?KARARI)', r'\n\n\1\n', text, flags=re.IGNORECASE)
    return text.strip()


def extract_metadata(file_path: str, chunk: str, page_num: int = None) -> Dict:
    """Belge türüne özel metadata çıkarımı"""
    doc_type = determine_document_type(file_path)
    metadata = {
        "document_id": str(uuid.uuid4()),
        "source": os.path.basename(file_path),
        "document_type": doc_type,
        "page": page_num if page_num is not None else ""
    }

    # Emsal kararlar için ekstra metadata
    if doc_type == 'precedent':
        if 'YARGITAY' in chunk:
            metadata["court"] = "Yargıtay"
        if 'KARAR NO' in chunk:
            metadata["decision_no"] = re.search(r'KARAR NO[: ]*(\d+/\d+)', chunk, re.IGNORECASE).group(1)

    # Kanun maddeleri için
    elif doc_type == 'law' and 'MADDE' in chunk:
        metadata["article_no"] = re.search(r'MADDE (\d+)', chunk).group(1)

    return metadata


def process_pdf(file_path: str) -> List[Dict]:
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        all_chunks = []
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\nMADDE", "\nYARGITAY", "\n\n"]
        )

        for page_num, page in enumerate(reader.pages):
            raw_text = page.extract_text() or ""
            cleaned = clean_text(raw_text)
            chunks = splitter.split_text(cleaned)

            for i, chunk in enumerate(chunks):
                metadata = extract_metadata(file_path, chunk, page_num + 1)
                all_chunks.append({
                    "text": chunk,
                    "metadata": metadata,
                    "chunk_id": f"{metadata['document_id']}-{page_num + 1}-{i}"
                })

        return all_chunks


def process_docx(file_path: str) -> List[Dict]:
    doc = Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    cleaned = clean_text(full_text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\nMADDE", "\nYARGITAY", "\n\n"]
    )
    chunks = splitter.split_text(cleaned)

    return [{
        "text": chunk,
        "metadata": extract_metadata(file_path, chunk),
        "chunk_id": f"docx-{i}"
    } for i, chunk in enumerate(chunks)]


def process_txt(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    cleaned = clean_text(text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\nMADDE", "\nYARGITAY", "\n\n"]
    )
    chunks = splitter.split_text(cleaned)

    return [{
        "text": chunk,
        "metadata": extract_metadata(file_path, chunk),
        "chunk_id": f"txt-{i}"
    } for i, chunk in enumerate(chunks)]


def process_document(file_path: str) -> List[Dict]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")

    if file_path.endswith(".pdf"):
        return process_pdf(file_path)
    elif file_path.endswith(".docx"):
        return process_docx(file_path)
    elif file_path.endswith(".txt"):
        return process_txt(file_path)
    else:
        raise ValueError(f"Desteklenmeyen dosya formatı: {file_path}")