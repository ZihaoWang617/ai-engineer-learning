import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key = api_key)
chroma_client = chromadb.PersistentClient(path = "./chroma_db")


with open("knowledge_base.txt", "r") as f:
    document = f.read()
    chunks = document.split("\n\n")
    chunks = [chunk for chunk in chunks if chunk.strip()]


embedding_response = openai_client.embeddings.create(
    input = chunks,
    model = "text-embedding-3-small"
)

vector = [e.embedding for e in embedding_response.data]
collection = chroma_client.get_or_create_collection("immigration")
collection.upsert(
    documents = chunks,
    embeddings = vector,
    ids = [str(i) for i in range(len(chunks))]
)