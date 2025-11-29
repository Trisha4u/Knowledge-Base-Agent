import streamlit as st
import requests

API_URL = "https://your-fastapi-url/query"  # or http://localhost:8000/query

st.title("Company Knowledge Base Agent")

question = st.text_input("Ask a question about the company policies / docs:")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        resp = requests.post(API_URL, json={"question": question})
        data = resp.json()
        st.subheader("Answer")
        st.write(data["answer"])

        st.subheader("Sources")
        for src in data["sources"]:
            with st.expander(src["document_id"]):
                st.write(src["chunk"])
