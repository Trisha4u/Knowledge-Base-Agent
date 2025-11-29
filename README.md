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

