# MultiModal-RAG-Endee
A Multi-Format Retrieval-Augmented Generation (RAG) Assistant leveraging the Endee Distributed Vector Database and Google Gemini .It utilizes Hugging Face Sentence Transformers (`all-MiniLM-L6-v2`) to generate dense vector embeddings securely. Supports memory-backed workflows and natively retrieves queries across raw text, PDFs, and Word structures.

# Prerequisites
- Python 3.10+
- Endee Server Running locally (Port 8080)
- Gemini API Key

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
Place your documents (`.txt`, `.pdf`, `.docx`) inside the `data/` folder and run the indexer:
```bash
python ingest.py
```

### 2. Launch Dashboard
Start the Streamlit Application to query your indices with conversational history enabled:
```bash
streamlit run app.py
```
