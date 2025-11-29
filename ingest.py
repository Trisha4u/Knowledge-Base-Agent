# ingest.py
import os
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pypdf import PdfReader

# --------- CONFIG ---------
DOCS_DIR = "docs"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "company_kb"
MODEL_NAME = "all-MiniLM-L6-v2"
# --------------------------


def chunk_text(text: str, max_chars: int = 600, overlap: int = 100):
    """
    Robust, low-RAM chunking.
    - works on words instead of slicing giant strings
    - overlap is approximate (in characters)
    """
    text = text.strip()
    if not text:
        return []

    words = text.split()
    chunks = []
    current = []
    current_len = 0

    # rough estimate: avg 5 chars per word -> overlap_words_count
    overlap_words = max(1, overlap // 5)

    for w in words:
        wlen = len(w) + 1  # +1 for space
        if current and current_len + wlen > max_chars:
            # close current chunk
            chunks.append(" ".join(current))

            # make next chunk start with overlap
            if overlap > 0 and len(current) > overlap_words:
                current = current[-overlap_words:]
            else:
                current = []

            current_len = sum(len(x) + 1 for x in current)

        current.append(w)
        current_len += wlen

    if current:
        chunks.append(" ".join(current))

    return chunks


def read_pdfs(doc_folder: str):
    folder = Path(doc_folder)
    if not folder.exists():
        raise FileNotFoundError(f"Folder '{doc_folder}' not found. Create it and add PDFs.")

    texts = []
    metadatas = []

    print(f"📄 Loading PDFs from {doc_folder}/ ...")

    for file in folder.iterdir():
        if not file.name.lower().endswith(".pdf"):
            continue

        print(f"Reading: {file.name}")
        reader = PdfReader(str(file))

        for page_idx, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""

            # clean whitespace
            page_text = " ".join(page_text.split())
            if not page_text.strip():
                continue

            # chunk per page (so we never hold the whole PDF in one string)
            chunks = chunk_text(page_text, max_chars=600, overlap=100)

            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metadatas.append(
                    {
                        "source": file.name,
                        "page": page_idx + 1,
                        "chunk": i,
                    }
                )

    return texts, metadatas


def main():
    # 1. Read and chunk PDFs
    texts, metadatas = read_pdfs(DOCS_DIR)
    print(f"✅ Total chunks: {len(texts)}")

    if not texts:
        print("⚠️ No text found in PDFs. Check that your PDF is readable.")
        return

    # 2. Embedding function (same model for ingestion & query)
    print(f"🧠 Loading embedding model ({MODEL_NAME}) on CPU ...")
    embedding_function = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)

    # 3. Connect to Chroma
    print("💾 Connecting to ChromaDB ...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # If collection already exists, drop it so we start clean
    try:
        client.delete_collection(COLLECTION_NAME)
        print("🧹 Old collection removed.")
    except Exception:
        pass  # first run, nothing to delete

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    # 4. Add chunks
    print("🔢 Inserting chunks into ChromaDB ...")
    ids = [f"chunk-{i}" for i in range(len(texts))]

    # add in small batches to avoid memory spikes
    batch_size = 64
    for start in range(0, len(texts), batch_size):
        end = min(start + batch_size, len(texts))
        collection.add(
            ids=ids[start:end],
            documents=texts[start:end],
            metadatas=metadatas[start:end],
        )
        print(f"   → Stored chunks {start}–{end-1}")

    print("✅ Ingestion complete! Chunks stored in ChromaDB.")


if __name__ == "__main__":
    main()
