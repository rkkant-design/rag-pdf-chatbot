"""Minimal chat UI that calls the FastAPI /chat endpoint."""
import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Chat with your PDFs", page_icon="\U0001F4C4")
st.title("\U0001F4C4 Chat with your PDFs")
st.caption(
    "Grounded answers from your own documents — every answer cites its source, "
    "and the bot says so honestly when the answer is not in the documents."
)

if "history" not in st.session_state:
    st.session_state.history = []


def render_sources(sources):
    if sources:
        st.caption("Sources: " + ", ".join(f"{s['document']} p.{s['page']}" for s in sources))


for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])
        render_sources(turn.get("sources"))

question = st.chat_input("Ask a question about your documents...")
if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(f"{API_URL}/chat", json={"question": question}, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                text = data.get("answer", "(no response)")
                sources = data.get("sources", [])
            except Exception as exc:  # noqa: BLE001
                text, sources = f"Error contacting the API at {API_URL}: {exc}", []
        st.markdown(text)
        render_sources(sources)

    st.session_state.history.append({"role": "assistant", "content": text, "sources": sources})
