"""
Ingest knowledge base into Pinecone.
Supports two source types:
- knowledge_base.txt (content chunks)
- knowledge_base_links.json (link chunks)
"""

import json
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# --- Config ---
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

INDEX_NAME = "jianuo-dev-v1"
BASE_DIR = Path(__file__).resolve().parent
CONTENT_FILE = BASE_DIR / "knowledge_base.txt"
LINKS_FILE = BASE_DIR / "knowledge_base_links.json"


def load_content_chunks() -> list[Document]:
    """Load content-type chunks from knowledge_base.txt.

    Two-stage splitting:
    1. Primary: MarkdownHeaderTextSplitter splits by '##' policy headers,
       giving one policy per chunk for semantic clarity.
    2. Secondary: RecursiveCharacterTextSplitter splits any chunk exceeding
       1200 chars (e.g. the TEER reference list) while preserving policy_title
       metadata across sub-chunks.
    """
    raw_text = CONTENT_FILE.read_text(encoding="utf-8")

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("##", "policy_title")],
        strip_headers=False,
    )
    header_chunks = header_splitter.split_text(raw_text)

    fallback_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, chunk_overlap=100
    )

    final_chunks: list[Document] = []
    for doc in header_chunks:
        if len(doc.page_content) <= 1200:
            final_chunks.append(doc)
        else:
            sub_docs = fallback_splitter.split_documents([doc])
            final_chunks.extend(sub_docs)

    for i, chunk in enumerate(final_chunks):
        policy_title = chunk.metadata.get("policy_title", "unknown")
        chunk.metadata = {
            "source": "knowledge_base.txt",
            "chunk_index": i,
            "resource_type": "content",
            "resource_url": "",
            "resource_id": f"policy_update_chunk_{i}",
            "resource_title": policy_title,
            "category_l1": "政策更新",
            "category_l2": "IRCC 政策时间线",
            "category_l3": "N/A",
        }

    print(f"[content] Loaded {len(final_chunks)} chunks from {CONTENT_FILE.name} (header-based)")
    return final_chunks


def load_link_chunks() -> list[Document]:
    """Load link-type chunks from knowledge_base_links.json.
    
    Note: resource_type now uses granular values (fee_template/guide/
    material_list/consent_form/fill_instructions/info_form/template)
    instead of generic "link". To distinguish content vs link chunks,
    use `metadata["source"]` or check `resource_type != "content"`.
    """
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        link_records = json.load(f)

    chunks = []
    for i, record in enumerate(link_records):
        # 拼 category 层级字符串,用于 page_content
        cat_parts = [record["category_l1"], record["category_l2"]]
        if record.get("category_l3"):
            cat_parts.append(record["category_l3"])
        category_str = " > ".join(cat_parts)

        # page_content 包含 category —— embedding 和 BM25 才能利用分类结构
        keywords_str = ", ".join(record.get("keywords", []))
        page_content = (
            f"分类:{category_str}\n"
            f"标题:{record['title']}\n"
            f"描述:{record['description']}\n"
            f"关键词:{keywords_str}"
        )

        doc = Document(
            page_content=page_content,
            metadata={
                "source": "knowledge_base_links.json",
                "chunk_index": i,
                "resource_type": record["resource_type"],
                "resource_url": record["url"],
                "resource_id": record["id"],
                "resource_title": record["title"],
                "category_l1": record["category_l1"],
                "category_l2": record["category_l2"],
                "category_l3": record.get("category_l3") or "N/A",
            },
        )
        chunks.append(doc)

    print(f"[link] Loaded {len(chunks)} chunks from {LINKS_FILE.name}")
    return chunks

# --- Index management ---
def clear_index(index_name: str) -> None:
    """Delete all vectors in the index before re-ingesting."""
    pc = Pinecone()
    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    total = stats.get("total_vector_count", 0)

    if total == 0:
        print(f"[clear] Index {index_name} is empty. Skipping.")
        return

    print(f"[clear] Deleting {total} vectors from {index_name}...")
    index.delete(delete_all=True)
    print(f"[clear] Done.")
    import time
    # Wait for delete to propagate across replicas
    print(f"[clear] Waiting for delete to propagate...")
    for _ in range(30):  # max 30 seconds
        time.sleep(1)
        stats = index.describe_index_stats()
        if stats.get("total_vector_count", 0) == 0:
            break
    print(f"[clear] Confirmed empty.")


# --- Main ingest ---
def ingest_all(clear_first: bool = True) -> None:
    """Ingest both content and link chunks into Pinecone."""
    if clear_first:
        clear_index(INDEX_NAME)

    content_chunks = load_content_chunks()
    link_chunks = load_link_chunks()
    all_chunks = content_chunks + link_chunks

    print(f"[ingest] Total chunks to upsert: {len(all_chunks)} "
          f"(content={len(content_chunks)}, link={len(link_chunks)})")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    PineconeVectorStore.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        index_name=INDEX_NAME,
    )

    print(f"[ingest] Upserted {len(all_chunks)} chunks to {INDEX_NAME}")


if __name__ == "__main__":
    ingest_all(clear_first=True)