# src/ingestion/loader.py
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, CSVLoader

def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    return loader.load()

def load_web(url: str):
    loader = WebBaseLoader(url)
    return loader.load()

def load_csv(file_path: str):
    loader = CSVLoader(file_path)
    return loader.load()