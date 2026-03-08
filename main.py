# main.py
from src.ingestion.loader import load_pdf
from src.ingestion.chunker import chunk_documents
from src.retrieval.vectorstore import get_or_build_vectorstore
from src.chain.rag_chain import build_rag_chain
from src.chain.sql_chain import build_sql_chain
from src.utils import build_augmented_query

# Choose mode: 'pdf', 'db', or 'auto'
MODE = "auto"

SQL_KEYWORDS = {
    "total", "sum", "average", "count", "how many", "revenue", "sales",
    "units", "region", "product", "month", "highest", "lowest", "best",
    "worst", "compare", "group", "aggregate", "which", "show me",
}

def looks_like_sql_query(text: str) -> bool:
    return any(kw in text.lower() for kw in SQL_KEYWORDS)

def load_pdf_chain():
    print("📄 Loading PDF pipeline...")
    docs = load_pdf("data/raw/gartnerinc2024annualreport.pdf")
    chunks = chunk_documents(docs)
    print(f"✅ {len(chunks)} chunks ready")
    vectorstore = get_or_build_vectorstore(chunks)
    print("✅ Vectorstore ready")
    chain = build_rag_chain(vectorstore)
    print("✅ RAG chain ready\n")
    return chain

def load_sql_chain():
    chain = build_sql_chain("data/sample.db")
    print("✅ SQL chain ready\n")
    return chain

# --- Mode setup ---
if MODE == "db":
    active_mode = "db"
    sql_chain = load_sql_chain()
    pdf_chain = None
elif MODE == "pdf":
    active_mode = "pdf"
    pdf_chain = load_pdf_chain()
    sql_chain = None
else:  # auto — load both
    print("🔀 Auto mode: loading both PDF and SQL chains...\n")
    pdf_chain = load_pdf_chain()
    sql_chain = load_sql_chain()
    active_mode = "auto"

print("💬 Ask anything. Type 'exit' to quit.")
if active_mode == "auto":
    print("   (Auto mode: routes between PDF and SQL based on your question)\n")

history = []  # list of {"role": ..., "content": ...} dicts

while True:
    query = input("🧑 You: ").strip()
    if query.lower() in ("exit", "quit"):
        print("👋 Goodbye!")
        break
    if not query:
        continue

    if active_mode == "auto":
        use_sql = looks_like_sql_query(query)
        print(f"   [routing → {'SQL' if use_sql else 'PDF'}]")
    else:
        use_sql = (active_mode == "db")

    augmented = build_augmented_query(query, history)

    if use_sql:
        result = sql_chain.invoke({"input": augmented})
        raw = result["output"]
        if isinstance(raw, list):
            answer = " ".join(
                block["text"] for block in raw
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            answer = raw
        print(f"\n🤖 Answer: {answer}\n")
    else:
        result = pdf_chain.invoke({"query": augmented})
        answer = result["result"]
        print(f"\n🤖 Answer: {answer}")
        print("\n📌 Sources used:")
        for i, doc in enumerate(result.get("source_documents", []), 1):
            page = doc.metadata.get("page", "?")
            preview = doc.page_content[:150].replace("\n", " ")
            print(f"  [{i}] Page {page}: {preview}...")
        print()

    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": answer})
    print("-" * 60 + "\n")
