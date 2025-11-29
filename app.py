import os
import re
import streamlit as st
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# --- Chroma / model config ---
PERSIST_DIR = "chroma_db"       # same as in ingest.py
COLLECTION_NAME = "company_kb"  # same as in ingest.py
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

# --------- Helpers: embeddings & DB ----------

@st.cache_resource
def get_embedder():
    return SentenceTransformer(EMBED_MODEL_NAME)


@st.cache_resource
def get_collection():
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    # Do NOT pass embedding_function here (it’s already defined in ingest.py)
    return client.get_collection(COLLECTION_NAME)


def embed_query(text: str, model: SentenceTransformer):
    vec = model.encode([text])[0]
    return vec.tolist()


def retrieve_chunks(question: str, collection, embedder, top_k: int = 5):
    """Return top_k text chunks for the question."""
    query_emb = embed_query(question, embedder)

    try:
        result = collection.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            include=["documents"]
        )
    except Exception as e:
        return [], f"Error querying ChromaDB: {e}"

    docs_list = result.get("documents", [[]])
    if not docs_list or not docs_list[0]:
        return [], None

    docs = docs_list[0]
    return docs, None


# --------- Helpers: answer extraction ----------

STOPWORDS = {
    "what", "when", "where", "who", "how", "why",
    "is", "are", "am", "the", "a", "an", "and", "or",
    "for", "of", "to", "in", "on", "at", "do", "does",
    "did", "can", "could", "i", "you", "we", "they",
    "it", "this", "that", "about"
}

GREETINGS = {"hi", "hello", "hey", "hii", "heyy"}


def tokenize(text: str):
    return re.findall(r"\b\w+\b", text.lower())


def score_unit(unit: str, question_tokens):
    tokens = [t for t in tokenize(unit) if t not in STOPWORDS]
    q_tokens = [t for t in question_tokens if t not in STOPWORDS]
    return len(set(tokens) & set(q_tokens))


def get_unknown_message() -> str:
    return (
        "I couldn't find anything about that in the document. "
        "Try asking things like:\n"
        "- How many sick leaves do employees get per year?\n"
        "- What are the working hours?\n"
        "- What is the WFH policy?"
    )


def extract_answer(question: str, chunks, max_units: int = 3):
    """
    Produces a clean short paragraph answer (about 2–3 lines).
    Uses keyword matching from retrieved chunks.
    """

    # No chunks from DB → unknown
    if not chunks:
        return get_unknown_message()

    q_tokens = tokenize(question)
    filtered_q = [t for t in q_tokens if t not in STOPWORDS]

    # Greeting / small talk (hi, hello, etc.)
    if filtered_q and all(t in GREETINGS for t in filtered_q):
        return (
            "Hi! I'm the company knowledge base chatbot. "
            "Ask me about leaves, working hours, WFH policy, user roles, onboarding, or support.\n\n"
            "Example questions:\n"
            "- How many sick leaves do employees get per year?\n"
            "- What are the working hours?\n"
            "- What is the WFH policy?"
        )

    scored_units = []

    # collect sentence-level units from chunks
    for chunk in chunks:
        # Clean basic bullets & newlines
        clean_chunk = chunk.replace("\n", " ").replace("", "").replace("•", "").strip()

        # Split into sentences
        parts = re.split(r"(?<=[.!?])\s+", clean_chunk)

        for p in parts:
            unit = p.strip()

            # skip very small fragments
            if len(unit) < 20:
                continue

            # skip header/meta-like lines from the PDF
            if any(h in unit for h in [
                "Company Knowledge Base –", "Document Title:", "Version:", "Last Updated:"
            ]):
                continue

            score = score_unit(unit, q_tokens)
            scored_units.append((score, unit))

    # If nothing useful matched → unknown
    if not scored_units:
        return get_unknown_message()

    # If best score is 0 → probably unrelated → unknown
    scored_units.sort(key=lambda x: x[0], reverse=True)
    best_score = scored_units[0][0]
    if best_score == 0:
        return get_unknown_message()

    # Take top N distinct units
    top_units = []
    used = set()

    for score, unit in scored_units:
        normalized = unit.lower().strip()
        if normalized not in used:
            used.add(normalized)
            top_units.append(unit)
        if len(top_units) >= max_units:
            break

    # A short, readable paragraph (2–3 lines approx.)
    return " ".join(top_units)


# --------- Streamlit UI ----------

def main():
    st.set_page_config(
        page_title="Company Knowledge Base Chatbot",
        page_icon="💬",
        layout="wide"
    )

    st.title("💬 Amce Company Knowledge Base Chatbot")
    st.write(
        "Ask anything based on the company policy and operations. "
        "Answers are strictly limited to what is present in the document."
    )

    question = st.text_input("💭 Your question:")

    if st.button("Ask"):
        if not question.strip():
            st.warning("Please type a question first.")
            return

        embedder = get_embedder()
        collection = get_collection()

        with st.spinner("Searching the knowledge base..."):
            chunks, err = retrieve_chunks(question, collection, embedder, top_k=5)
            if err:
                st.error(err)
                return
            answer = extract_answer(question, chunks)

        st.subheader("✅ Answer")
        st.write(answer)


if __name__ == "__main__":
    main()
