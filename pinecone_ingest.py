# pinecone_ingest.py
import openai
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings

from config import OPENAI_API_KEY
from pinecone_creator import index

# Initialize OpenAI & embedder
openai.api_key = OPENAI_API_KEY
embedder = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def ingest_docs(directory_path: str = "docs"):
    """
    Load all text files under `directory_path`, split them into chunks,
    embed each chunk, and upsert into Pinecone in batches.
    """
    loader = DirectoryLoader(directory_path, glob="**/*.txt", loader_cls=TextLoader)
    docs = loader.load()
    to_upsert = []

    for doc in docs:
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            vector = embedder.embed_documents([chunk])[0]
            to_upsert.append((
                f"{doc.metadata['source']}_{i}",
                vector,
                {"source": doc.metadata["source"]}
            ))

    # Batch upsert
    batch_size = 100
    for i in range(0, len(to_upsert), batch_size):
        batch = to_upsert[i : i + batch_size]
        index.upsert(items=batch)

if __name__ == "__main__":
    ingest_docs()
