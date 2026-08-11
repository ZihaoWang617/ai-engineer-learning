"""
Dump all Pinecone vectors grouped by category_l2.
Uses native Pinecone query with dummy vector to retrieve full inventory
(bypasses LangChain's relevance-ranked similarity_search).
"""
import os
from collections import defaultdict
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("jianuo-dev-v1")

stats = index.describe_index_stats()
total = stats.total_vector_count
print(f"[Pinecone] Index reports {total} total vectors\n")

dummy = [0.0] * 1536
res = index.query(vector=dummy, top_k=total, include_metadata=True)

by_cat = defaultdict(list)
for match in res.matches:
    md = match.metadata or {}
    # Link chunks: resource_id 存在
    # Content chunks: 目前没 resource_id -> fallback 到 Pinecone match.id
    doc_id = md.get("resource_id", match.id)
    cat_l1 = md.get("category_l1", "?")
    cat_l2 = md.get("category_l2", "uncategorized")
    rtype = md.get("resource_type", "?")
    by_cat[(cat_l1, cat_l2)].append((doc_id, rtype))

grand_total = 0
for (l1, l2) in sorted(by_cat.keys()):
    items = by_cat[(l1, l2)]
    print(f"\n=== [{l1}] / [{l2}] ({len(items)}) ===")
    for did, rt in sorted(items):
        print(f"  [{rt}] {did}")
    grand_total += len(items)

print(f"\n--- Total: {grand_total} vectors ---")
