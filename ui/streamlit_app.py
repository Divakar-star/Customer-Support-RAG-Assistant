import uuid

import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1/session"

st.set_page_config(page_title="Document Q&A", page_icon="\U0001F4C4")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

HEADERS = {"X-Session-Id": st.session_state.session_id}

st.title("Document Q&A")
st.caption(
    "Upload your own files and ask questions about them. Nothing is saved permanently - "
    "everything here disappears when you refresh this page or the server restarts."
)

with st.sidebar:
    st.subheader("Your documents")
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, or Markdown files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )
    if uploaded_files and st.button("Upload + Index"):
        for uploaded in uploaded_files:
            with st.spinner(f"Indexing {uploaded.name}..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/documents",
                        headers=HEADERS,
                        files={"file": (uploaded.name, uploaded.getvalue())},
                        timeout=120,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                except requests.RequestException as exc:
                    st.error(f"Upload failed for {uploaded.name}: {exc}")
                else:
                    st.success(
                        f"{uploaded.name}: {data['status']} "
                        f"({data['chunks_created']} chunks)"
                    )
        st.rerun()

    try:
        docs_resp = requests.get(f"{API_BASE}/documents", headers=HEADERS, timeout=10)
        docs_resp.raise_for_status()
        docs = docs_resp.json()
        if docs:
            for doc in docs:
                st.write(f"- {doc['file_name']} ({doc['chunks']} chunks)")
        else:
            st.info("No documents uploaded yet.")
    except requests.RequestException:
        st.warning("Could not load document list - is the API running?")

    if st.button("Clear session"):
        try:
            requests.delete(f"{API_BASE}/documents", headers=HEADERS, timeout=10)
        except requests.RequestException as exc:
            st.error(f"Failed to clear session: {exc}")
        else:
            st.session_state.history = []
            st.session_state.conversation_id = None
            st.rerun()

for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])
        if turn["citations"]:
            sources = ", ".join(
                f"{c['document']} (page {c['page']})" for c in turn["citations"]
            )
            st.caption(f"Sources: {sources}")

question = st.chat_input("Ask a question about your uploaded documents...")
if question:
    with st.spinner("Searching your documents..."):
        try:
            resp = requests.post(
                f"{API_BASE}/chat",
                headers=HEADERS,
                json={
                    "question": question,
                    "conversation_id": st.session_state.conversation_id,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            st.error(f"Request failed: {exc}")
        else:
            st.session_state.conversation_id = data["conversation_id"]
            st.session_state.history.append(
                {
                    "question": question,
                    "answer": data["answer"],
                    "citations": data["citations"],
                }
            )
            st.rerun()
