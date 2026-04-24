import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key = api_key)
chroma_client = chromadb.PersistentClient(path = "./chroma_db")

def chunk_text(text, chunk_size = 200, overlap = 50):
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start: start + chunk_size]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


with open("knowledge_base.txt", "r") as f:
    document = f.read()
    chunks = chunk_text(document)


embedding_response = openai_client.embeddings.create(
    input = chunks,
    model = "text-embedding-3-small"
)

vector = [e.embedding for e in embedding_response.data]
collection = chroma_client.get_or_create_collection("immigration")
collection.upsert(
    documents = chunks,
    embeddings = vector, # type: ignore
    ids = [str(i) for i in range(len(chunks))],
    metadatas = [{"source": "knowledge_base", "chunk_index": i} for i in range(len(chunks))]
)