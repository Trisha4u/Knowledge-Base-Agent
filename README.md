# 💬 Company Knowledge Base Chatbot  
AI Agent Challenge – Knowledge Base Agent

This project is a **Company Knowledge Base Chatbot** that answers employee questions using information strictly extracted from a company PDF.  
It uses **local embeddings**, **ChromaDB**, and **Streamlit**, and does **not require an API key**.

The agent helps employees quickly find answers related to:
- Leave policy  
- Working hours  
- WFH rules  
- Onboarding steps  
- User roles  
- Product information  
- Support & escalation guidelines  
- FAQs inside the PDF  

---

## 🚀 Demo Link  
👉 *Add your Streamlit deployment link here after hosting*

---

## 📘 Overview  

Many companies struggle with repeated employee questions about policies, HR rules, and internal procedures. This project solves the problem by building an AI-powered chatbot that:

- Reads the **Company Knowledge Base PDF**  
- Converts content into embeddings  
- Stores them in a **local vector database (ChromaDB)**  
- Uses similarity search to retrieve relevant sections  
- Generates short 2–3 line answers based strictly on the PDF  

This ensures **no hallucination**, **no external API dependency**, and **accurate document-grounded responses**.

---

## 🛠️ Tech Stack

| Component | Technology |
|----------|-------------|
| Frontend UI | **Streamlit** |
| Embeddings Model | **SentenceTransformers (all-MiniLM-L6-v2)** |
| Vector Database | **ChromaDB (PersistentClient)** |
| PDF Processing | **pypdf** |
| Language | **Python 3.10+** |
| Hosting | Streamlit Cloud |

---

## 📂 Project Structure

knowledge-base-agent/
│
├── app.py # Main Streamlit chatbot UI
├── ingest.py # Converts PDF → chunks → embeddings → ChromaDB
├── requirements.txt # Dependencies
│
├── docs/
│ └── Company Knowledge Base.pdf # Company knowledge source
│
├── chroma_db/ # Vector database (auto-created by ingest.py)
│
└── README.md

---

## 📄 Features

### ✅ 1. Ask questions in natural language  
User can type:  
- “How many sick leaves do employees get?”  
- “What are working hours?”  
- “What is the WFH policy?”  

### ✅ 2. Answers strictly from PDF  
No hallucinations.  
Only information present in the document is shown.

### ✅ 3. Short, clean 2–3 line answers  
Readable, chatbot-style responses.

### ✅ 4. Handles unknown questions  
If asked something outside the PDF (e.g., “Who is Virat Kohli?”), it replies with:  

> “I couldn’t find anything about that in the document. Try asking about leaves, working hours, WFH, roles, onboarding, or support.”

### ✅ 5. Greeting support  
Typing “hi”, “hello”, etc. gives a friendly chatbot introduction.

---

## 🏗️ Architecture Diagram
               ┌────────────────────────┐
               │      PDF Document       │
               │  (Company KB Document)  │
               └───────────┬────────────┘
                           │
                      ingest.py
                           │
   ┌─────────────Chunks + Embeddings─────────────┐
                           │
                    ┌──────▼──────┐
                    │  ChromaDB   │  ← Vector Database
                    │ (company_kb)│
                    └──────┬──────┘
                           │
                     app.py (UI)
                           │
            ┌────────Query + Embedding────────┐
                           │
                    SentenceTransformer
                           │
                 Top-K similar chunks
                           │
                   Answer extraction
                           │
                  Final 2–3 line answer
                           │
                       User UI

2. Activate it

Windows:

.venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Ingest the PDF into ChromaDB
python ingest.py

5. Run the chatbot
streamlit run app.py

