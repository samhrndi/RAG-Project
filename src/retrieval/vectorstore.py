# src/retrieval/vectorstore.py
import os
from langchain_chroma import Chroma
from src.retrieval.embedder import get_embedder

CHROMA_DIR = "./chroma_db"

def build_vectorstore(chunks):
    embedder = get_embedder()
    return Chroma.from_documents(
        documents=chunks,
        embedding=embedder,
        persist_directory=CHROMA_DIR
    )

def load_vectorstore():
    embedder = get_embedder()
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedder
    )

def get_or_build_vectorstore(chunks=None):
    """Load existing vectorstore if available, otherwise build from chunks."""
    already_exists = os.path.isdir(CHROMA_DIR) and any(
        f.endswith(".bin") or f.endswith(".parquet")
        for _, _, files in os.walk(CHROMA_DIR)
        for f in files
    )
    if already_exists:
        print("📦 Loading existing vectorstore...")
        return load_vectorstore()
    if chunks is None:
        raise ValueError("No vectorstore found and no chunks provided to build one.")
    print("🔨 Building vectorstore from chunks...")
    return build_vectorstore(chunks)