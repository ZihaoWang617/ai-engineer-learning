"""
Day 56: Create the first Pinecone index for the immigration RAG project.

Idempotent: if the index already exists, skips creation.
Waits for the index to become ready before exiting.
"""
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    raise RuntimeError("PINECONE_API_KEY not found in .env")

pc = Pinecone(api_key=api_key)

INDEX_NAME = "jianuo-dev-v1"
DIMENSION = 1536
METRIC = "cosine"

# Idempotency: skip if exists
existing = [idx.name for idx in pc.list_indexes()]
if INDEX_NAME in existing:
    print(f"Index '{INDEX_NAME}' already exists. Skipping creation.")
else:
    print(f"Creating index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    print("Create request submitted. Polling for readiness...")
    while not pc.describe_index(INDEX_NAME).status['ready']:
        print("  still initializing...")
        time.sleep(2)
    print("Index is ready.")

# Final state
desc = pc.describe_index(INDEX_NAME)
print(f"\nIndex details:")
print(f"  name:      {desc.name}")
print(f"  dimension: {desc.dimension}")
print(f"  metric:    {desc.metric}")
print(f"  host:      {desc.host}")
print(f"  status:    {desc.status}")
