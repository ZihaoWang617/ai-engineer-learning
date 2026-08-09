"""Quick sanity check on ingested data."""
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

INDEX_NAME = "jianuo-dev-v1"

pc = Pinecone()
index = pc.Index(INDEX_NAME)

# 1. Total count
stats = index.describe_index_stats()
print(f"Total vectors: {stats.get('total_vector_count', 0)}")
print(f"Expected: 53 (7 content + 46 link)")
print()

# 2. Sample query - should return mix of content and link
query_vec = [0.1] * 1536  # dummy vector, just to fetch some records
results = index.query(vector=query_vec, top_k=5, include_metadata=True)

print("Sample 5 records (metadata only):")
for i, match in enumerate(results.matches):
    md = match.metadata
    print(f"\n[{i+1}] resource_type = {md.get('resource_type')}")
    print(f"    source = {md.get('source')}")
    print(f"    chunk_index = {md.get('chunk_index')}")
    if md.get('source') == 'knowledge_base_links.json':
        print(f"    title = {md.get('resource_title', '')[:60]}")
        print(f"    url = {md.get('resource_url', '')[:60]}")