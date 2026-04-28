from langchain_community.document_loaders import TextLoader  # 读文件
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings  # embedding
from langchain_chroma import Chroma  # 存入ChromaD
from dotenv import load_dotenv
load_dotenv()

file = TextLoader("knowledge_base.txt")
documents = file.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)
for i, chunk in enumerate(chunks):
    chunk.metadata["source"] = "knowledge_base"
    chunk.metadata["chunk_index"] = i
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="immigration_lc",
    persist_directory="./chroma_db_lc"
)
