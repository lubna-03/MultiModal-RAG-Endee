# Endee RAG Assistant

A Retrieval-Augmented Generation (RAG) assistant built using the **Endee Vector Distributed Database** and **Google Gemini 2.5**. It utilizes **Hugging Face Sentence Transformers** (`all-MiniLM-L6-v2`) to generate dense vector embeddings securely.

## 🚀 Key Features
- **Low-Level MessagePack Data Retrieval**: Decodes vector match responses iteratively from raw binary server buffers utilizing `msgpack` for maximum latency performance.
- **Conditional Database Predicate Filtering**: Translates dashboard structures into stringified query predicates operators delivery dynamically to non-relational C++ indexing backends.
- **Multi-Format Ingestion Harness**: Supports adaptive layout scanners supporting `.txt`, `.pdf` (via PyMuPDF), and `.docx` recursively securely.
- **Conversational Memory Buffering**: Maintains stateful historical cycles inside layout streams for seamless chatbot experience.

## Prerequisites
- **Docker** and **Docker Compose**
- Python 3.10+
- Gemini API Key

## 🛠️ Backend Setup (Endee)
Start the Vector database server using Docker:
```bash
docker-compose up -d
```

## Installation
1. Setup environment variables inside `.env`:
   ```env
   ENDEE_URL=http://localhost:8080
   GEMINI_API_KEY=your_gemini_key_here
   HF_TOKEN=your_huggingface_token_here
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### 1. Data Ingestion
Place your documents (`.txt`, `.pdf`, `.docx`) inside the `data/` folder and run the indexing script:
```bash
python ingest.py
```

### 2. Launch Dashboard
Start the Streamlit Application session:
```bash
streamlit run app.py
```
