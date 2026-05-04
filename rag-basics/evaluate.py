import json
from dotenv import load_dotenv
load_dotenv('../.env')
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_query import hybrid_retriever, rerank_docs

with open("test_set.json", "r") as f:
    data = json.load(f)
db = Chroma(
    persist_directory='chroma_db_lc',
    embedding_function=OpenAIEmbeddings(),
    collection_name='immigration_lc'
)
hit = 0

for item in data: 
    question = item["question"]
    chunk = item["ground_truth_chunk_index"]
    results = db.similarity_search(question, k = 1)
    retrieved_indices = [doc.metadata["chunk_index"] for doc in results]
    print(f"  Retrieved: {retrieved_indices}")
    if chunk in retrieved_indices:
        hit +=1
        print(f"HIT: {question}")
    else:
        print(f"MISS: {question}")
print(f"Recall@1: {hit}/{len(data)}")

hybrid_hit = 0
for item in data:
    question = item["question"]
    chunk = item["ground_truth_chunk_index"]
    results = hybrid_retriever(question, k = 6)
    rerank = rerank_docs(question, results, top_n = 1)
    retrieved_indice = [doc.metadata["chunk_index"] for doc in rerank]

    if chunk in retrieved_indice:
        hybrid_hit +=1
        print(f"HIT: {question}")
    else:
        print(f"MISS: {question}")
print(f"Hybrid+Rerank Recall@1: {hybrid_hit}/{len(data)}")