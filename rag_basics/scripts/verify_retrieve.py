"""Verify retrieve() returns consistent shape across 4 ablation configs.
Run: python -m rag_basics.scripts.verify_retrieve
"""
from rag_basics.langchain_query_pinecone import retrieve

test_queries = [
    "学签怎么办",
    "BC PNP 分数",
    "父母团聚担保要求",
]

configs = [
    ("Config 1 (bm25 only)",       dict(use_bm25=True,  use_dense=False, use_rerank=False)),
    ("Config 2 (dense only)",      dict(use_bm25=False, use_dense=True,  use_rerank=False)),
    ("Config 3 (hybrid no rerank)",dict(use_bm25=True,  use_dense=True,  use_rerank=False)),
    ("Config 4 (hybrid + rerank)", dict(use_bm25=True,  use_dense=True,  use_rerank=True)),
]

for q in test_queries:
    print(f"\n=== Query: {q} ===")
    for name, kwargs in configs:
        docs = retrieve(q, **kwargs)
        # Shape assertions
        assert isinstance(docs, list), f"{name}: expected list, got {type(docs)}"
        assert len(docs) <= 3, f"{name}: len {len(docs)} > top_k=3"
        assert all(hasattr(d, "metadata") for d in docs), f"{name}: doc missing metadata"
        assert all("resource_id" in d.metadata for d in docs), f"{name}: metadata missing resource_id"
        ids = [d.metadata["resource_id"] for d in docs]
        print(f"  {name}: {ids}")

print("\n✅ All shape assertions passed.")