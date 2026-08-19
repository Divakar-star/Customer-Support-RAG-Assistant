import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Acme Support Assistant", page_icon="\U0001F4AC")

tab_chat, tab_upload = st.tabs(["Chat", "Upload Documents"])

with tab_chat:
    st.title("Acme Support Assistant")

    if "history" not in st.session_state:
        st.session_state.history = []
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

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

    question = st.chat_input("Ask a question about Acme policies...")
    if question:
        with st.spinner("Searching company documents..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/chat",
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

with tab_upload:
    st.title("Upload Knowledge Document")
    uploaded = st.file_uploader("Choose a PDF, TXT, or Markdown file", type=["pdf", "txt", "md"])
    if uploaded and st.button("Upload + Index"):
        with st.spinner("Indexing document..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/documents",
                    files={"file": (uploaded.name, uploaded.getvalue())},
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException as exc:
                st.error(f"Upload failed: {exc}")
            else:
                st.success(f"Status: {data['status']} - {data['chunks_created']} chunks created.")

    st.subheader("Indexed Documents")
    try:
        docs_resp = requests.get(f"{API_BASE}/documents", timeout=10)
        docs_resp.raise_for_status()
        docs = docs_resp.json()
        if docs:
            st.table(docs)
        else:
            st.info("No documents indexed yet.")
    except requests.RequestException:
        st.warning("Could not load document list - is the API running?")
