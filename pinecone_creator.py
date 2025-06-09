import os
import glob
import openai
from docx import Document
from pinecone import Pinecone, ServerlessSpec
from config import OPENAI_API_KEY, PINECONE_API_KEY
# --- Configuration ---
openai.api_key = OPENAI_API_KEY
pinecone_api_key = PINECONE_API_KEY

INDEX_NAME = "train-xar-knowledge-base"
EMBED_MODEL = "text-embedding-ada-002"
PINECONE_DIM = 1536
CHUNK_SIZE = 500

# --- Pinecone Setup ---
pc = Pinecone(api_key=pinecone_api_key)
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=PINECONE_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(INDEX_NAME)

# --- Text Utilities ---
def extract_text(docx_path):
    return "\n".join([p.text for p in Document(docx_path).paragraphs])

def chunk_text(text, chunk_size=CHUNK_SIZE):
    words, chunks, temp = text.split(), [], []
    for word in words:
        temp.append(word)
        if len(temp) >= chunk_size:
            chunks.append(" ".join(temp))
            temp = []
    if temp: chunks.append(" ".join(temp))
    return chunks

def get_embedding(text, model=EMBED_MODEL):
    return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]

# --- Ingestion ---
def upsert_docx_to_pinecone(docx_path):
    doc_name = os.path.splitext(os.path.basename(docx_path))[0]
    text = extract_text(docx_path)
    chunks = chunk_text(text)

    vectors = [
        (f"{doc_name}-chunk{i}", get_embedding(chunk), {"text": chunk, "doc_name": doc_name})
        for i, chunk in enumerate(chunks)
    ]
    if vectors:
        index.upsert(vectors)
        print(f"✅ Upserted {len(vectors)} chunks from: {doc_name}")
    else:
        print(f"⚠️ No valid text to upsert from: {doc_name}")

# --- Batch Entry Point ---
def ingest_folder(folder_path):
    files = glob.glob(os.path.join(folder_path, "*.docx"))
    if not files:
        print("❌ No .docx files found.")
        return
    for f in files:
        if not os.path.basename(f).startswith("~$"):
            upsert_docx_to_pinecone(f)

# Run directly
if __name__ == "__main__":
    ingest_folder(r"C:\Users\ayush\Downloads\TR")
