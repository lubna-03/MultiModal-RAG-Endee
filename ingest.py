import os
import requests
import json
import fitz  # PyMuPDF
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
ENDEE_URL = os.getenv('ENDEE_URL', 'http://localhost:8080')
COLLECTION_NAME = "my_rag_collection"
RECREATE_INDEX = True  
DATA_DIR = r"D:\endee\data"  # ABSOLUTE PATH

# 2. Recursive Splitter Configuration
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)

def load_pdf(filepath):
    text = ""
    try:
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"Error loading PDF {filepath}: {e}")
    return text

def load_docx(filepath):
    text = ""
    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error loading DOCX {filepath}: {e}")
    return text

def run_ingestion():
    if not os.path.exists(DATA_DIR):
        print(f"ERROR: Folder not found at {DATA_DIR}")
        return

    if RECREATE_INDEX:
        print(f"Deleting existing index: {COLLECTION_NAME}...")
        try:
            res = requests.delete(f"{ENDEE_URL}/api/v1/index/{COLLECTION_NAME}/delete")
            if res.status_code == 200:
                print(f"Index deleted successfully.")
            else:
                print(f"Index delete response: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Delete Error: {e}")

    
    print(f"Checking/Creating Index: {COLLECTION_NAME}...")
    create_payload = {
        "index_name": COLLECTION_NAME,
        "dim": 384,
        "space_type": "cosine"
    }
    try:
        res = requests.post(f"{ENDEE_URL}/api/v1/index/create", json=create_payload)
        if res.status_code == 200:
            print(f"Created index {COLLECTION_NAME}")
        elif res.status_code == 409:
            print(f"Index {COLLECTION_NAME} already exists")
        else:
            print(f"Index check/create response: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Connection Error during index creation: {e}")

    all_chunks_count = 0
    supported_ext = ('.txt', '.pdf', '.docx')
    files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(supported_ext) and f != "requirements.txt"]
    
    if not files:
        print(f" No supported files (.txt, .pdf, .docx) found in {DATA_DIR}")
        return

    for filename in files:
        print(f"Processing: {filename}...")
        filepath = os.path.join(DATA_DIR, filename)
        ext = os.path.splitext(filename)[1].lower()
        
        raw_text = ""
        file_type = ""
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            file_type = 'text'
        elif ext == '.pdf':
            raw_text = load_pdf(filepath)
            file_type = 'pdf'
        elif ext == '.docx':
            raw_text = load_docx(filepath)
            file_type = 'docx'
            
        if not raw_text.strip():
            print(f" Skipped empty or unloaded file: {filename}")
            continue

        chunks = text_splitter.split_text(raw_text)
        
        for i, chunk_text in enumerate(chunks):
            vector = embed_model.encode(chunk_text).tolist()
            payload = {
                "id": f"{filename}_{i}",
                "vector": vector,
                "meta": json.dumps({
                    "text": chunk_text, 
                    "source": filename, 
                    "file_type": file_type,
                    "chunk_id": i
                })
            }
                
            try:
                insert_url = f"{ENDEE_URL}/api/v1/index/{COLLECTION_NAME}/vector/insert"
                response = requests.post(insert_url, json=payload)
                if response.status_code == 200:
                    all_chunks_count += 1
                else:
                    print(f"Failed chunk {i}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f" Connection Error: {e}")
                        
    print(f"---")
    print(f" Ingestion Complete! Created and stored {all_chunks_count} chunks.")

if __name__ == "__main__":
    run_ingestion()