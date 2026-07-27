import os
import re
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from config.settings import PROCESSED_DATA_DIR, CHROMA_PERSIST_DIR
from embeddings.embedding_model import embedding_loader

BOOK_FILE_NAME = "D2_Biology_Bookpages.txt"
GUIDE_FILE_NAME = "D3_Full_GuideBook.txt"

def parse_textbook(file_path: Path) -> list[Document]:
    """Parses D2 textbook into page-level documents with metadata."""
    documents = []
    if not file_path.exists():
        print(f"[!] Warning: {file_path.name} not found.")
        return documents

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Regex to catch both --- PAGE X --- and --- PAGE FM-X --- formats
    pages = re.split(r'---\s*PAGE\s+([A-Za-z0-9-]+)\s*---', content)
    
    current_chapter = "General / Overview"
    for i in range(1, len(pages), 2):
        page_label = pages[i].strip()
        page_text = pages[i+1].strip()

        if not page_text:
            continue

        try:
            page_num = int(page_label)
        except ValueError:
            page_num = 0  # Front matter pages

        ch_match = re.search(r'Chapter\s*(\d+)[:\s]*([^\n]+)', page_text, re.IGNORECASE)
        if ch_match:
            current_chapter = f"Chapter {ch_match.group(1)}: {ch_match.group(2).strip()}"

        doc = Document(
            page_content=page_text,
            metadata={
                "subject": "Biology",
                "chapter": current_chapter,
                "book_type": "Textbook",
                "page_number": page_num,
                "source_file": file_path.name
            }
        )
        documents.append(doc)

    print(f"[+] Parsed {len(documents)} pages from Textbook ({file_path.name}).")
    return documents

def parse_guidebook(file_path: Path) -> list[Document]:
    """Parses D3 guide into chapter/section level documents with metadata."""
    documents = []
    if not file_path.exists():
        print(f"[!] Warning: {file_path.name} not found.")
        return documents

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    sections = re.split(r'START OF FILE \[\d+/36\]:\s*([^\n]+)', content)

    for i in range(1, len(sections), 2):
        file_label = sections[i].strip()
        section_text = sections[i+1].strip()

        if not section_text:
            continue

        ch_match = re.search(r'Ch(\d+)', file_label, re.IGNORECASE)
        chapter_str = f"Chapter {ch_match.group(1)}" if ch_match else "General"

        q_type = "Guide"
        if "MCQ" in file_label:
            q_type = "Guide - MCQs"
        elif "Short" in file_label:
            q_type = "Guide - Short Qs"
        elif "Long" in file_label:
            q_type = "Guide - Long Qs"

        doc = Document(
            page_content=section_text,
            metadata={
                "subject": "Biology",
                "chapter": chapter_str,
                "book_type": q_type,
                "page_number": -1,
                "source_file": file_label
            }
        )
        documents.append(doc)

    print(f"[+] Parsed {len(documents)} sections from Guide ({file_path.name}).")
    return documents

def run_ingestion():
    """Reads processed files, embeds content in CPU-friendly batches, and persists into ChromaDB."""
    book_path = PROCESSED_DATA_DIR / BOOK_FILE_NAME
    guide_path = PROCESSED_DATA_DIR / GUIDE_FILE_NAME

    all_docs = []
    all_docs.extend(parse_textbook(book_path))
    all_docs.extend(parse_guidebook(guide_path))

    if not all_docs:
        print("[-] No documents to ingest. Check data/processed/ directory.")
        return

    print(f"[*] Total Documents/Chunks to Index: {len(all_docs)}")
    print(f"[*] Initializing Vector Database at: {CHROMA_PERSIST_DIR}")

    embedding_model = embedding_loader.get_embedding_model()

    # Batching to prevent PyTorch thread deadlocks on large embedding models
    batch_size = 32
    total_docs = len(all_docs)
    total_batches = ((total_docs - 1) // batch_size) + 1

    print(f"[*] Embedding {total_docs} chunks in {total_batches} batches (Batch Size: {batch_size})...")

    # Initialize Chroma store with the first batch
    first_batch = all_docs[:batch_size]
    vector_db = Chroma.from_documents(
        documents=first_batch,
        embedding=embedding_model,
        persist_directory=str(CHROMA_PERSIST_DIR)
    )
    print(f"[+] Batch 1/{total_batches} embedded ({len(first_batch)}/{total_docs} chunks)")

    # Sequentially process and write remaining batches
    for i in range(batch_size, total_docs, batch_size):
        batch = all_docs[i:i + batch_size]
        vector_db.add_documents(batch)
        batch_num = (i // batch_size) + 1
        processed_count = min(i + batch_size, total_docs)
        print(f"[+] Batch {batch_num}/{total_batches} embedded ({processed_count}/{total_docs} chunks)")

    print("[+] INGESTION COMPLETE! Vector database populated and saved.")

if __name__ == "__main__":
    run_ingestion()