from langchain_community.document_loaders import TextLoader  # 读文件
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings  # embedding
from langchain_pinecone import PineconeVectorStore
from pathlib import Path
from dotenv import load_dotenv
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)
INDEX_NAME = "jianuo-dev-v1"

file = TextLoader("knowledge_base.txt")
documents = file.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)
for i, chunk in enumerate(chunks):
    chunk.metadata["source"] = "knowledge_base"
    chunk.metadata["chunk_index"] = i

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = PineconeVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=INDEX_NAME
)
print(f"Upserted {len(chunks)} chunks to {INDEX_NAME}")