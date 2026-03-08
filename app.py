# app.py
import streamlit as st
from src.retrieval.vectorstore import get_or_build_vectorstore
from src.ingestion.loader import load_pdf
from src.ingestion.chunker import chunk_documents
from src.chain.rag_chain import build_rag_chain
from src.chain.sql_chain import build_sql_chain
from src.utils import build_augmented_query

st.set_page_config(page_title="RAG Assistant", page_icon="🤖", layout="centered")

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    mode = st.radio(
        "Data source",
        options=["PDF — Gartner Report", "Database — Sales Data"],
        index=0,
    )
    st.divider()
    if st.button("🗑 Clear chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("PDF uses vector search over the Gartner 2024 Annual Report.\nDatabase uses SQL generation over sample sales data.")

use_sql = mode.startswith("Database")

title = "🗄️ Sales Database — Q&A" if use_sql else "📄 Gartner Report — Q&A"
st.title(title)

# --- Chain loaders (cached per mode) ---
@st.cache_resource(show_spinner="Loading PDF index...")
def get_pdf_chain():
    docs = load_pdf("data/raw/gartnerinc2024annualreport.pdf")
    chunks = chunk_documents(docs)
    vectorstore = get_or_build_vectorstore(chunks)
    return build_rag_chain(vectorstore)

@st.cache_resource(show_spinner="Connecting to database...")
def get_sql_chain():
    return build_sql_chain("data/sample.db")

chain = get_sql_chain() if use_sql else get_pdf_chain()

# --- Session state ---
mode_key = "sql" if use_sql else "pdf"
if "messages" not in st.session_state:
    st.session_state.messages = {}
if mode_key not in st.session_state.messages:
    st.session_state.messages[mode_key] = []

messages = st.session_state.messages[mode_key]

# --- Chat history ---
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📌 Sources"):
                for src in msg["sources"]:
                    st.caption(f"**Page {src['page']}:** {src['preview']}")

# --- Input ---
placeholder = (
    "Ask about sales, revenue, regions..." if use_sql
    else "Ask about the Gartner annual report..."
)

if query := st.chat_input(placeholder):
    messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    augmented = build_augmented_query(query, messages[:-1])

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if use_sql:
                result = chain.invoke({"input": augmented})
                raw = result["output"]
                if isinstance(raw, list):
                    answer = " ".join(
                        block["text"] for block in raw
                        if isinstance(block, dict) and block.get("type") == "text"
                    )
                else:
                    answer = raw
                sources = []
            else:
                result = chain.invoke({"query": augmented})
                answer = result["result"]
                sources = [
                    {
                        "page": doc.metadata.get("page", "?"),
                        "preview": doc.page_content[:200].replace("\n", " "),
                    }
                    for doc in result.get("source_documents", [])
                ]

        st.markdown(answer)
        if sources:
            with st.expander("📌 Sources"):
                for src in sources:
                    st.caption(f"**Page {src['page']}:** {src['preview']}")

    messages.append({"role": "assistant", "content": answer, "sources": sources})
