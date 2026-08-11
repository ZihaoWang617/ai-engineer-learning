"""
One-shot cleanup: delete 7 old content vectors (auto-UUID ids) from Pinecone.
Run BEFORE re-running langchain_ingest_pinecone.py after content metadata schema update.
"""
import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# 7 个旧 content vector UUID (from eval_category_index.txt)
OLD_CONTENT_IDS = [
    "45f59167-9fed-493d-b3c9-ed9d8de22497",
    "629fe39d-0cc2-4c93-abbd-e190dfbc7b43",
    "b77fa463-07ec-4c3e-87f9-239ad29527db",
    "c88e48b2-fb87-4ce7-9fcc-bc1dd693d8cf",
    "d09a58a2-46b4-49c7-9256-cb0199e7d716",
    "dcbdd552-c031-4fd3-95c7-11c315dfc6b5",
    "eaea09b2-ab52-4079-ac07-0a57f5fc5fa6",
]

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("jianuo-dev-v1")

before = index.describe_index_stats().total_vector_count
print(f"[before] Pinecone reports {before} vectors")

index.delete(ids=OLD_CONTENT_IDS)
print(f"[delete] Requested delete of {len(OLD_CONTENT_IDS)} content vectors")

# Pinecone delete is eventual consistency, wait briefly + verify
import time
time.sleep(3)

after = index.describe_index_stats().total_vector_count
print(f"[after] Pinecone reports {after} vectors")
print(f"[delta] {before - after} deleted (expected: {len(OLD_CONTENT_IDS)})")

if before - after != len(OLD_CONTENT_IDS):
    print("[WARN] Delete count mismatch — check Pinecone dashboard, may need retry")
else:
    print("[OK] Ready to re-upsert with new content metadata schema")
