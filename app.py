import os
import requests
import streamlit as st
import google.generativeai as genai
import json
import msgpack
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# --- PAGE SETUP ---
st.set_page_config(page_title="Endee AI Assistant", page_icon="🤖")
load_dotenv()

# --- SIDEBAR FILTER ---
st.sidebar.header("📁 Data Filters")
file_type_filter = st.sidebar.multiselect(
    "Filter by Document Type",
    options=["text", "pdf", "docx"],
    default=["text", "pdf", "docx"]
)
if not file_type_filter:
    st.sidebar.warning("⚠️ No filter selected. Search will return nothing.")



@st.cache_resource
def load_resources():
    embed = SentenceTransformer('all-MiniLM-L6-v2')
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    return embed, model

embed_model, llm = load_resources()
ENDEE_URL = os.getenv('ENDEE_URL', 'http://localhost:8080')
COLLECTION_NAME = "my_rag_collection"

# --- UI ---
st.title("Endee RAG Assistant")
st.info("Ask questions based on your documents in D:/endee/data")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to know?"):
    # Add User message to state and render
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.spinner("Searching Endee Database..."):
        qv = embed_model.encode(prompt).tolist()
        payload = {"vector": qv, "k": 5}
        
        # Apply Sidebar filter condition if any
        if 'file_type_filter' in globals() and file_type_filter:
            filter_obj = [{"file_type": {"$in": file_type_filter}}]
            payload["filter"] = json.dumps(filter_obj)
            
        try:
            search_url = f"{ENDEE_URL}/api/v1/index/{COLLECTION_NAME}/search"
            res = requests.post(search_url, json=payload, timeout=10)
            
            if res.status_code == 200:
                data = msgpack.unpackb(res.content, raw=False)
                hits = []
                if isinstance(data, list) and data:
                    if isinstance(data[0], list) and data[0]:
                        if isinstance(data[0][0], list):
                            hits = data[0]
                        else:
                            hits = data
                            
                context_items = []
                for h in hits:
                    if len(h) > 2:
                        meta_bytes = h[2]
                        try:
                            meta_str = meta_bytes.decode('utf-8') if isinstance(meta_bytes, bytes) else meta_bytes
                            meta_dict = json.loads(meta_str)
                            if 'text' in meta_dict:
                                context_items.append(meta_dict['text'])
                        except:
                            pass
                context = "\n---\n".join(context_items)
                
                if context:
                    # Inject History to Prompt
                    history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[-4:-1]])
                    final_prompt = f"Context: {context}\n\n{history_text}\nUser: {prompt}\nAnswer professionally and concisely:"
                    
                    answer = llm.generate_content(final_prompt)
                    response_text = answer.text
                    
                    # Add to history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    with st.chat_message("assistant"):
                        st.markdown(response_text)
                else:
                    with st.chat_message("assistant"):
                        st.warning("No relevant context found in documents.")
            else:
                with st.chat_message("assistant"):
                    st.error(f"Database Error {res.status_code}: Loading failed.")
        except Exception as e:
             with st.chat_message("assistant"):
                 st.error(f"Connection Failed: {e}")

st.divider()
st.caption("Final Year CSE Project | Endee + Gemini")