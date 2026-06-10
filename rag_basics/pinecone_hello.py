"""
Day 56: First Pinecone connection.
This is exploration code, not production.
"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load .env from project root
load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    raise RuntimeError("PINECONE_API_KEY not found in .env")

pc = Pinecone(api_key=api_key)

# List existing indexes (should be empty on a fresh account)
print("Existing indexes:")
for idx in pc.list_indexes():
    print(f"  - {idx.name}")
print("Done.")