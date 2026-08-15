"""
Retrieval evaluation: 4-config ablation on 15-query stratified testset.
Metric: precision@3

Design principles:
- Testset stratified across 4 dimensions: answer_source, query_type, locality, category
- Ground truth uses lenient labeling (false negatives more harmful than false positives)
- Category distribution reflects real Jianuo usage (top 3: 学签, OINP, 联邦移民)
"""

TESTSET = [
    # ============ Content-heavy (5) ============
    {
        "id": 1,
        "query": "Express Entry 现在申请需要提前体检吗?",
        "meta": {
            "answer_source": "content",
            "query_type": "specific",
            "locality": "single",
            "category": "政策更新+联邦",
        },
        "relevant_doc_ids": {
            "policy_update_chunk_0",  # EE 提前体检 (2025.08.21)
        },
    },
    {
        "id": 2,
        "query": "LMIA 现在对 EE 加分还有效吗",
        "meta": {
            "answer_source": "content",
            "query_type": "specific",
            "locality": "single",
            "category": "政策更新+联邦",
        },
        "relevant_doc_ids": {
            "policy_update_chunk_2",  # LMIA 加分取消 (2025.03.25)
        },
    },
    {
        "id": 3,
        "query": "2024 年之后加拿大境内读硕士还能免 PAL 吗",
        "meta": {
            "answer_source": "content",
            "query_type": "vague",
            "locality": "multi",
            "category": "政策更新+学签",
        },
        "relevant_doc_ids": {
            "policy_update_chunk_3",  # PAL 扩大 (2025.01.22)
            "policy_update_chunk_9",  # 转学必须重新申请学签 (borderline, 宽松标)
        },
    },
    {
        "id": 4,
        "query": "配偶想跟着我来加拿大工作,有什么政策变化",
        "meta": {
            "answer_source": "content",
            "query_type": "vague",
            "locality": "multi",
            "category": "政策更新+工签",
        },
        "relevant_doc_ids": {
            "policy_update_chunk_4",  # SOWP 担保人资格收紧
            "policy_update_chunk_5",  # TEER 清单技术类
            "policy_update_chunk_6",  # TEER 清单医疗类
            "visa_work_spouse_open_international_guide",  # 宽松标
        },
    },
    {
        "id": 5,
        "query": "最近有什么新政影响身份 restoration",
        "meta": {
            "answer_source": "content",
            "query_type": "specific",
            "locality": "single",
            "category": "政策更新",
        },
        "relevant_doc_ids": {
            "policy_update_chunk_8",  # Restoration 政府费上调 (2024.12.01), 唯一直接答的政策 chunk
        },
    },
    {
        "id": 6,
        "query": "OINP 硕士 stage 1 需要什么材料",
        "meta": {
            "answer_source": "link",
            "query_type": "specific",
            "locality": "single",
            "category": "OINP",
        },
        "relevant_doc_ids": {
            "immi_prov_oinp_master_stage1_guide",  # stage1 guide 里应含材料清单
            # 注意: KB 里没有 immi_prov_oinp_master_stage1_material_list 独立 doc
            # (stage 2/3 才有 material_list, stage 1 材料在 guide 内)
        },
    },
    {
        "id": 7,
        "query": "枫叶卡续签 guide",
        "meta": {
            "answer_source": "link",
            "query_type": "specific",
            "locality": "single",
            "category": "枫叶卡",
        },
        "relevant_doc_ids": {
            "immi_other_pr_renewal_guide",  # 直接对应
            "immi_other_pr_renewal_material_list",  # 宽松标: 用户问 guide 但 material_list 也是续签资料一部分
        },
    },
    {
        "id": 8,
        "query": "父母担保填哪个 form",
        "meta": {
            "answer_source": "link",
            "query_type": "specific",
            "locality": "single",
            "category": "联邦",
        },
        "relevant_doc_ids": {
            "immi_federal_parent_sponsorship_guide",  # 父母担保主 guide
            "info_form_immigration_federal",  # 宽松标: 联邦移民通用信息表, 用户问"form"很可能指这个
        },
    },
    {
        "id": 9,
        "query": "我想读硕士 ontario 怎么申请",
        "meta": {
            "answer_source": "link",
            "query_type": "vague",
            "locality": "multi",
            "category": "OINP+院校",
        },
        "relevant_doc_ids": {
            "immi_prov_oinp_master_stage1_guide",  # stage 1 是入门
            "immi_prov_oinp_master_stage2_guide",  # 完整流程要 stage 2
            "info_form_school_application",  # 宽松标: 读硕士要先申学校
            # 说明: vague query "怎么申请" 会触发多 chunk retrieval, 
            # 期待系统能捞回 OINP 前两阶段主 guide
        },
    },
    {
        "id": 10,
        "query": "配偶担保怎么弄",
        "meta": {
            "answer_source": "link",
            "query_type": "vague",
            "locality": "multi",
            "category": "联邦",
        },
        "relevant_doc_ids": {
            "immi_federal_spousal_sponsorship_guide",  # 配偶担保 guide
            "immi_federal_spousal_sponsorship_material_list",  # 配偶担保材料清单
            # 宽松标: SOWP 政策也间接相关但那是工签方向, 不算配偶担保 (居民身份担保), 不标
        },
    },
    {
        "id": 11,
        "query": "OINP 硕士从申请到拿枫叶卡完整流程",
        "meta": {
            "answer_source": "mixed",
            "query_type": "vague",
            "locality": "cross_category",
            "category": "OINP+枫叶卡",
        },
        "relevant_doc_ids": {
            "immi_prov_oinp_master_stage1_guide",
            "immi_prov_oinp_master_stage2_guide",
            "immi_prov_oinp_master_stage2_1_attestation_form",
            "immi_prov_oinp_master_stage2_2_address_history",
            "immi_prov_oinp_master_stage3_single_guide",
            "immi_prov_oinp_master_stage3_couple_guide",  # 宽松标: query 未指定婚姻状态
            "immi_other_pr_citizenship_guide",  # 拿卡后入籍链路
        },
    },
    {
        "id": 12,
        "query": "EE 现在有什么变化 stage 1 材料是什么",
        "meta": {
            "answer_source": "mixed",
            "query_type": "specific",
            "locality": "multi",
            "category": "政策更新+联邦",
        },
        "relevant_doc_ids": {
            "policy_update_chunk_0",  # EE 提前体检
            "policy_update_chunk_2",  # LMIA 加分取消
            "immi_federal_ee_stage1_guide",
            "immi_federal_ee_stage1_material_list",
        },
    },
    {
        "id": 13,
        "query": "去日本旅游签需要什么 加拿大境内怎么办",
        "meta": {
            "answer_source": "mixed",
            "query_type": "specific",
            "locality": "cross_category",
            "category": "旅游签+护照贴签",
        },
        "relevant_doc_ids": {
            "visa_travel_japan_inperson_guide",
            "visa_travel_japan_online_guide",
            "passport_stamp_guide_canada",
        },
    },
    {
        "id": 14,
        "query": "境内学签续签学校换了要注意什么",
        "meta": {
            "answer_source": "content",  # 改: KB link 侧无覆盖, 主要靠 content
            "query_type": "vague",
            "locality": "multi",
            "category": "政策更新+学签(KB gap)",
        },
        "relevant_doc_ids": {
            "policy_update_chunk_3",  # PAL 扩大
            "policy_update_chunk_9",  # 转学必须重新申请学签
            # Note: 学签 12 doc 全是首签/转签, 无续签/换校 link doc (tech debt #8)
        },
    },
    {
        "id": 15,
        "query": "PGWP 需要什么材料 什么时候要提前体检",
        "meta": {
            "answer_source": "mixed",
            "query_type": "specific",
            "locality": "multi",
            "category": "工签+政策更新",
        },
        "relevant_doc_ids": {
            "visa_work_pgwp_guide",
            "visa_work_pgwp_material_list",
            "policy_update_chunk_0",  # EE 提前体检 (borderline)
        },
    },
]


def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int = 3) -> float:
    """
    Precision@k = |retrieved[:k] ∩ relevant| / k
    Denominator is k, not |relevant| (that would be recall).
    """
    retrieved_topk = set(retrieved_ids[:k])
    hits = len(retrieved_topk & relevant_ids)
    return hits / k


# TODO Day 73:
# - retrieve_config1_bm25_only
# - retrieve_config2_dense_only
# - retrieve_config3_hybrid_no_rerank
# - retrieve_config4_hybrid_rerank (current production, reuse existing code)
# - run_evaluation()
# - report() with stratified breakdown by meta dimensions
# ============ Config definitions ============

from rag_basics.langchain_query_pinecone import retrieve

CONFIGS = [
    ("Config 1: BM25 only",         dict(use_bm25=True,  use_dense=False, use_rerank=False)),
    ("Config 2: Dense only",        dict(use_bm25=False, use_dense=True,  use_rerank=False)),
    ("Config 3: Hybrid no rerank",  dict(use_bm25=True,  use_dense=True,  use_rerank=False)),
    ("Config 4: Hybrid + rerank",   dict(use_bm25=True,  use_dense=True,  use_rerank=True)),
]


# ============ Evaluation ============

def run_evaluation() -> list[dict]:
    """Run 15 queries × 4 configs. Return flat list of result records."""
    results = []
    for item in TESTSET:
        query = item["query"]
        query_id = item["id"]
        relevant = item["relevant_doc_ids"]
        meta = item["meta"]
        
        for config_name, config_kwargs in CONFIGS:
            # TODO 1: 调 retrieve(query, **config_kwargs) 得到 docs
            docs = retrieve(query, **config_kwargs)
            # TODO 2: 提取 resource_id list (list of str)
            retrieved_ids = [doc.metadata["resource_id"] for doc in docs]
            # TODO 3: 算 precision@3
            p_at_3 = precision_at_k(retrieved_ids, relevant, k=3)
            
            results.append({
                "query_id": query_id,
                "query": query,
                "config": config_name,
                "retrieved_ids": retrieved_ids,
                "p_at_3": p_at_3,
                # Include meta for stratification later
                "answer_source": meta["answer_source"],
                "query_type": meta["query_type"],
                "locality": meta["locality"],
                "category": meta["category"],
            })
    
    return results

from pathlib import Path

def save_results_to_csv(results: list[dict], path: str | None = None) -> None:
    """Save flat results list to CSV for stratified analysis."""
    import csv
    
    if path is None:
        path = Path(__file__).parent / "eval_results.csv"
    
    rows_for_csv = [
        {**r, "retrieved_ids": "|".join(r["retrieved_ids"])}
        for r in results
    ]
    fieldnames = list(rows_for_csv[0].keys())
    
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_for_csv)
    
    print(f"Saved {len(rows_for_csv)} rows to {path}")



def report_stratified(results: list[dict]) -> None:
    """Stratified precision@3 breakdown by label dimensions."""
    import pandas as pd
    
    df = pd.DataFrame(results)
    
    print("\n=== Stratified by answer_source ===")
    # TODO 1: groupby ['config', 'answer_source'] -> mean p_at_3 -> unstack
    print(df.groupby(['config', 'answer_source'])['p_at_3'].mean().unstack().fillna(0).round(3).to_string())
    
    print("\n=== Stratified by query_type ===")
    # TODO 2: same pattern
    print(df.groupby(['config', 'query_type'])['p_at_3'].mean().unstack().fillna(0).round(3).to_string())
    
    print("\n=== Stratified by locality ===")
    # TODO 3: same pattern
    print(df.groupby(['config', 'locality'])['p_at_3'].mean().unstack().fillna(0).round(3).to_string())

# ============ Reporting ============

def report_overall(results: list[dict]) -> None:
    """Print mean precision@3 per config, overall."""
    from collections import defaultdict
    per_config = defaultdict(list)
    for r in results:
        per_config[r["config"]].append(r["p_at_3"])
    
    print("\n=== Overall precision@3 ===")
    for config_name in [c[0] for c in CONFIGS]:
        scores = per_config[config_name]
        mean = sum(scores) / len(scores)
        print(f"  {config_name}: {mean:.3f}  (n={len(scores)})")

def report_per_query(results):
    """Print p@3 per query, one row per query, one col per config."""
    from collections import defaultdict
    per_query = defaultdict(dict)
    for r in results:
        per_query[r["query_id"]][r["config"]] = r["p_at_3"]
    
    print("\n=== Per-query precision@3 ===")
    config_names = [c[0] for c in CONFIGS]
    print(f"{'qid':>4} " + " ".join(f"{c.split(':')[0]:>10}" for c in config_names))
    for qid in sorted(per_query.keys()):
        row = per_query[qid]
        print(f"{qid:>4} " + " ".join(f"{row[c]:>10.3f}" for c in config_names))


def report_sample_details(results, sample_qid=1):
    """Print retrieved_ids for 1 sample query across all configs."""
    print(f"\n=== Sample query {sample_qid} retrieved_ids ===")
    for r in results:
        if r["query_id"] == sample_qid:
            print(f"  {r['config']}: {r['retrieved_ids']}  (p@3={r['p_at_3']:.3f})")

# ============ Main ============

if __name__ == "__main__":
    results = run_evaluation()
    report_overall(results)
    report_per_query(results)
    report_sample_details(results, sample_qid=1)
    report_stratified(results)
    save_results_to_csv(results)