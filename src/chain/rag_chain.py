# src/chain/rag_chain.py
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_classic.chains import RetrievalQA

load_dotenv()

def build_rag_chain(vectorstore):
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.9
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )