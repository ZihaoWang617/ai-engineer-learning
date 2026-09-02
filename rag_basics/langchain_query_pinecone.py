from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain_community.retrievers import BM25Retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
import cohere
from pathlib import Path
import os
# Import loaders from ingest module to keep BM25 in sync with Pinecone
from rag_basics.langchain_ingest_pinecone import load_content_chunks, load_link_chunks

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

INDEX_NAME = "jianuo-dev-v1"

# --- Clients ---
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# --- Retrievers ---
vectorstore = PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embeddings,
)
semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# BM25 covers BOTH content and link chunks (方案 A)
_all_docs_for_bm25 = load_content_chunks() + load_link_chunks()
bm25_retriever = BM25Retriever.from_documents(_all_docs_for_bm25)
bm25_retriever.k = 3


from typing import Literal

class ChunkRelevance(BaseModel):
    """Represents the relevance assessment of a single context chunk to the user question."""
    chunk_index: int = Field(description=(
    "该 chunk 在本次 Context 里的位置, 对应 [Context-Chunk-N] 标记里的 N. "
    "0-indexed, 范围 0 到 (Context chunk 总数 - 1). "
    "不是 KB 原始 chunk_index." 
    ))
    score: Literal["HIGH", "MEDIUM", "NONE"] = Field(
        description=(
            "该 chunk 与 Question 的相关性评分. "
            "HIGH = chunk 内容直接定义/解释/回答了 Question 的核心概念. "
            "MEDIUM = chunk 与 Question 相关但只覆盖子场景/单个更新点, 不足以完整回答核心问题. "
            "NONE = chunk 仅在关键词或大类别上沾边, 内容与 Question 无实质关联 (例: Question 问 'BC PNP 是什么', chunk 内容是 'EE 体检要求' 或 'OINP 打分调整')."
        )
    )
    reason: str = Field(
        description="用一句简短中文解释为什么给这个 score (例: 'chunk 内容是 EE 政策更新, 与 BC PNP 无关')."
    )


class RagOutput(BaseModel):
    """Structured output for the RAG chain."""
    answer: str = Field(description="自然语言回答，用中文")
    branch: Literal["A", "B", "C1", "C2", "D"] = Field(
        description=(
            "Which branch from the system prompt this answer follows. "
            "A=chit-chat, B=dynamic-data-with-link, C1=exact-match, "
            "C2=partial-match, D=kb-gap. This drives whether sources are shown to user."
        ),
    )
    cited_link_ids: list[str] = Field(
        default_factory=list,
        description=(
            "If the answer references any link-type resources from the context, "
            "list their resource_id values here. Empty list if no link is cited."
        ),
    )
    relevance_assessment: list[ChunkRelevance] = Field(
    description=(
        "对 Context 里每一个 chunk 逐一做相关性评估. "
        "列表长度必须等于 Context 里的 chunk 数量, 顺序与 Context 一致. "
        "这个字段必须在选择 branch 之前完成, branch 判定依赖于此评估."
        )
    )

# --- Prompt ---
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是移民咨询助手, 只根据提供的 Context 回答用户问题, 不要编造。
【Step 0: Relevance Gate】(必须先做, 再选 branch)

在选择 branch 之前 (包括 Branch A / 闲聊 场景), 必须先对 Context 里每一个 chunk 
逐一评估相关性, 填入 relevance_assessment 字段.

严格约束:
- list 长度必须严格等于 Context 里实际显示的 chunk 数量
- chunk_index 必须是 Context 里 [Context-Chunk-N] 标记里的那个 N (从 0 开始, 到 N-1 结束, N = Context chunk 总数). 不是 header 里 "第 X 块" 的 X (那是 KB 原始 ID, 与本次判定无关).
- 不要凭空增加评估 (即使你觉得应该有某类 chunk 但 Context 里没有出现)
- 不要遗漏评估 (即使 chunk 明显 NONE 也要评估)

即使 Branch A 判定时不使用 relevance 结果, 仍需完成评估作为 audit 记录 — 这是 schema 契约, 
不可跳过.

评分标准:
- HIGH: chunk 内容直接定义/解释/回答了 Question 的核心概念
- MEDIUM: chunk 与 Question 相关, 但只覆盖子场景/单个更新点, 不足以完整回答
- NONE: chunk 仅在关键词或大类别上沾边, 内容与 Question 无实质关联

关键区分: 
- Question 里有 "BC PNP", chunk 里也有 "BC PNP" → 不代表 HIGH
- 只看 chunk 内容是否 address 了 Question 问的那件事本身

【Branch 判定规则】(基于 Step 0 结果)
- 如果 Question 是闲聊 / 与移民无关 → Branch A (无视 relevance)
- 如果 Question 问动态数据且有 authoritative_url chunk → Branch B
- 如果所有 chunk 都是 NONE → 强制走 Branch D
- 如果至少 1 个 chunk 是 HIGH → Branch C1
- 如果没有 HIGH 但至少有 1 个 MEDIUM → Branch C2
- 其他情况 → Branch D

【回答策略】每次生成 answer 前, 先判断 Context 与 Question 的关系, 走对应 branch:

Branch A - 闲聊 / 打招呼 / 与移民无关的 query:
  Context 里的 chunks 都与 Question 无实质关联 (用户在打招呼、问天气、闲聊等).
  → answer: 一句话自然回复, 不引用 Context (如: "你好! 我是移民咨询助手, 有什么可以帮你?")
  → cited_link_ids: 留空

Branch B - Question 问动态数据 (最新分数 / 费用 / 日期 / 名额 / 抽签结果) 且 Context 里有 link(authoritative_url) 类型资源:
  你不知道最新值 (KB 里没有实时数据). 
  → answer: 简短说明静态背景 (如频率、一般规律), 明确让用户查阅下方权威链接
    (如: "EE 抽签频率约每 2 周一次, 最新分数请查阅下方 IRCC 官方链接")
  → 严禁在 answer 里生成任何具体数字 (分数、金额、日期)
  → cited_link_ids: 只放 authoritative_url 类型资源的 resource_id

Branch C1 - Context 里的资源精确匹配 Question (问什么答什么):
  按下方【Context chunk 类型说明】和【判断规则】处理.

Branch C2 - Context 里有相关资源, 但与 Question 场景不完全匹配 (只是话题相近):
  ⚠️ 关键判断: Context chunk 描述的政策/规则的适用范围 (谁适用/什么时候适用/什么场景), 
     是否与用户 Question 里的具体场景 (身份/时间点/操作类型) 完全一致?
  
  如果不完全一致:
  → answer 必须做三件事:
    1. 引用 Context 原文 (用引号标注, 如: 根据 KB 里 "2024.11.15 转学必须重新申请学签" 政策)
    2. 明确说明该政策的具体适用场景 (从 Context 原文里读出的, 不要推广)
    3. 指出用户场景可能不完全适用, 建议直接咨询顾问确认
  → answer 示例: 
    "根据 KB 里 '2024.11.15 转学必须重新申请学签' 政策, 该规则针对转学场景。您问的
    '续签换校' 场景与此不完全相同, KB 里没有直接覆盖, 建议直接咨询顾问确认具体流程。"
  → cited_link_ids: 可引用相关资源, 但 answer 里必须体现"局限性"

Branch D - Context 有内容, 但都与 Question 无关 (KB gap):
  → answer 必须严格是: "我没有相关信息, 建议直接咨询顾问" (可加一句解释 KB 缺失什么)
  → ⚠️ 严禁使用你自己的先验知识回答. 即使你知道 Question 的答案 (如 BC PNP、EE 等常见移民术语的定义), 
    也不允许生成任何解释性内容. 你的角色是移民咨询助手, 只反映 KB 内容, 不做通用百科.
  → 严禁在 answer 里出现 Question 里的关键概念的定义 (如 "BC PNP 是...")
  → cited_link_ids: 留空

【Context chunk 类型说明】
Context 里的 chunk 有两种类型:
1. content 类型 (header 标 "类型:content"): 政策 / 知识文本, 用于生成 answer
2. link 类型 (header 标 "类型:link(xxx)"): 可下载资源. xxx 是具体资源类型:
   - link(fee_template): 收费模版
   - link(info_form): 信息收集表
   - link(guide): 指导手册
   - link(material_list): 材料收集清单
   - link(consent_form): 同意书 / 同意函
   - link(fill_instructions): 填写方式说明
   - link(authoritative_url): 外部权威链接 (触发 Branch B)
   
   每个 link chunk 会显示 resource_id, 用于在 cited_link_ids 里引用.

【判断规则】(适用于 Branch C)
- 用户问 "是什么 / 怎么样 / 为什么" → 主要用 content 生成 answer
- 用户问 "表格 / 模板 / 在哪下载 / 给我 XX 文件 / 需要什么材料" → 主要引用 link, answer 简短说明
- 混合意图 → answer 给知识说明, cited_link_ids 附相关资源

【严格通用规则】(所有 branch 都必须遵守)
- 不要在 answer 里输出 URL
- 不要在 answer 里输出 resource_id 字符串 (如 "visa_study_first_minor_material_list")
- 不要在 answer 里说 "请参考以下链接" 然后列出 resource_id
- answer 只用自然语言引导用户 (如 "具体材料清单请见下方相关资源"), 链接由系统自动展示
- 所有需要引用的资源, resource_id 只放进 cited_link_ids 字段
【Branch 输出要求】
- 每次回答必须在 branch 字段明确标注你走了哪个 branch (A/B/C1/C2/D)
- 这不是可选字段, 必须与你实际选择的 branch 一致"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])

# --- Module-level constants ---
RESOURCE_TYPE_LABELS = {
    "content": "政策更新",
    "guide": "指南",
    "material_list": "材料清单",
    "fee_template": "收费模版",
    "info_form": "信息表",
    "consent_form": "同意书",
    "fill_instructions": "填写说明",
    "authoritative_url": "外部权威源",
}

# --- Helpers ---
def _format_chunk_index(raw):
    if isinstance(raw, (int, float)):
        return int(raw)
    return raw


def format_docs(docs) -> str:
    parts = []
    for i, doc in enumerate(docs):
        md = doc.metadata
        source = md.get("source", "unknown")
        chunk_index = _format_chunk_index(md.get("chunk_index", "?"))
        resource_type = md.get("resource_type", "content")

        # 新判断:content 是知识文本,其他都是 link 类资源
        is_link = resource_type != "content"
        
        if is_link:
            resource_id = md.get("resource_id", "")
            # 把 resource_type 也告诉 LLM,帮助它判断资源类型
            header = (
                f"[来源:{source}, 第{chunk_index}块, "
                f"类型:link({resource_type}), resource_id:{resource_id}]"
            )
        else:
            header = f"[来源:{source}, 第{chunk_index}块, 类型:content]"

        parts.append(f"[Context-Chunk-{i}]\n{header}\n{doc.page_content}")
    return "\n\n".join(parts)


def hybrid_retriever(question: str, k: int) -> list:
    semantic_docs = semantic_retriever.invoke(question)
    bm25_docs = bm25_retriever.invoke(question)
    seen = set()
    combined = []
    for doc in semantic_docs + bm25_docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            combined.append(doc)
    return combined[:k]


def retrieve(
    query: str,
    use_bm25: bool = True,
    use_dense: bool = True,
    use_rerank: bool = True,
    top_k: int = 3,
) -> list:
    """Unified retrieval interface for production + ablation eval.
    
    Args:
        query: Search query string.
        use_bm25: Include BM25 lexical retrieval.
        use_dense: Include Pinecone dense retrieval.
        use_rerank: Apply Cohere cross-encoder rerank as final stage.
        top_k: Number of docs to return.
    
    Returns:
        List of Document objects ordered by relevance, len <= top_k.
    """
    # Validate: at least one retrieval strategy must be enabled
    if not (use_bm25 or use_dense):
        raise ValueError("At least one retrieval strategy (BM25 or dense) must be enabled.")
    
    # Determine intermediate k (before rerank)
    # 如果要 rerank, 粗排层多召回一些 (6 个) 给 rerank 挑; 否则直接要 top_k
    intermediate_k = 6 if use_rerank else top_k
    
    # Reset BM25 k to default before branching (avoid stale state from prior calls)
    # Reset shared retriever state before branching (avoid stale k from prior calls).
    # NOTE: mutating shared singleton attrs is not ideal — tech debt to refactor
    # to per-call similarity_search() bypassing retrievers.
    bm25_retriever.k = 3
    semantic_retriever.search_kwargs["k"] = 3

    # Branch 1: hybrid (both BM25 and dense)
    if use_bm25 and use_dense:
        docs = hybrid_retriever(query, intermediate_k)
    
    # Branch 2: BM25 only
    elif use_bm25 and not use_dense:
        bm25_retriever.k = intermediate_k
        docs = bm25_retriever.invoke(query)
    
    # Branch 3: dense only
    elif use_dense and not use_bm25:
        semantic_retriever.search_kwargs["k"] = intermediate_k
        docs = semantic_retriever.invoke(query)
    
    # Rerank stage (optional)
    if use_rerank:
        docs = rerank_docs(query, docs, top_n=top_k)  # 替换这行
    else:
        docs = docs[:top_k]  # 替换这行
    
    return docs

def rerank_docs(question: str, docs: list, top_n: int = 3) -> list:
    if not docs:
        return []
    texts = [doc.page_content for doc in docs]
    response = co.rerank(
        model="rerank-v3.5",
        query=question,
        documents=texts,
        top_n=top_n,
    )
    return [docs[result.index] for result in response.results]

def rewrite_query_for_retrieval(question: str, history: list) -> str:
    """Rewrite a follow-up question into a self-contained query using chat history.
    
    Only used for retrieval. Original question is preserved for answer generation.
    """
    if not history:
        return question  # First turn, no rewriting needed
    
    history_str = "\n".join(
        f"{'用户' if isinstance(m, HumanMessage) else '助手'}: {m.content}"
        for m in history
    )
    
    rewrite_prompt = f"""基于以下对话历史,把用户最新问题改写成一个可以独立理解的完整问题。
- 解析所有代词(它/这个/那个/他们等)为具体名词
- 补齐省略的主语或上下文
- 保持原问题的核心意图不变
- 只输出改写后的问题,不要任何解释

对话历史:
{history_str}

最新问题: {question}

改写后的问题:"""
    
    result = llm.invoke(rewrite_prompt)
    rewritten = result.content.strip()
    print(f"[rewrite] original:  {question}")
    print(f"[rewrite] rewritten: {rewritten}")
    return rewritten


# --- Chain (with structured output) ---
structured_llm = llm.with_structured_output(RagOutput)
rag_chain = prompt | structured_llm

store: dict[str, list] = {}

def get_history(session_id: str) -> list:
    """Return message list for a session. Create if not exists."""
    if session_id not in store:
        store[session_id] = []
    return store[session_id]


def ask(question: str, session_id: str = "default") -> dict:
    """Main RAG entry point with manual chat history + query rewriting."""
    try:
        # Get chat history FIRST (needed for query rewriting)
        history = get_history(session_id)
        
        # Rewrite query for retrieval using history (no-op if history is empty)
        retrieval_query = rewrite_query_for_retrieval(question, history)
        
        # Use rewritten query for retrieval; original question for answer generation
        docs = retrieve(retrieval_query)  # 或 retrieve(question), 保持原变量名
        context = format_docs(docs)

        # Invoke chain with explicit chat_history
        result: RagOutput = rag_chain.invoke({
            "context": context,
            "question": question,
            "chat_history": history,
        }) # type: ignore


        if len(result.relevance_assessment) != len(docs):
            print(f"[WARN] relevance_assessment length {len(result.relevance_assessment)} != docs length {len(docs)}")
        print(f"[relevance] branch={result.branch}")
        for r in result.relevance_assessment:
            print(f"  chunk {r.chunk_index}: {r.score} - {r.reason}")
        if result.branch == "D":
            result.answer = "我没有相关信息, 建议直接咨询顾问。"

        # Manually append to history AFTER successful invocation
        history.append(HumanMessage(content=question))
        history.append(AIMessage(content=result.answer))

        # Build sources — gated by LLM branch decision
        # Branch A (chit-chat) and D (KB gap): suppress sources to avoid misleading UI
        # Branch B/C1/C2: KB has relevance, show sources
        SOURCE_SUPPRESSED_BRANCHES = {"A", "D"}

        if result.branch in SOURCE_SUPPRESSED_BRANCHES:
            source_info = []
        else:
            source_info = []
            for doc in docs:
                title = doc.metadata.get("resource_title") or "未命名资源"
                rtype = doc.metadata.get("resource_type", "unknown")
                type_label = RESOURCE_TYPE_LABELS.get(rtype, rtype)
                source_info.append(f"{title} ({type_label})")

        # Resolve cited_link_ids -> full link details (guardrail against hallucinated IDs)
        retrieved_link_map = {
            doc.metadata["resource_id"]: doc
            for doc in docs
            if doc.metadata.get("resource_type") != "content"   # 改判断方向
            and doc.metadata.get("resource_id")
        }
        links = []
        for lid in result.cited_link_ids:
            if lid in retrieved_link_map:
                md = retrieved_link_map[lid].metadata
                links.append({
                    "title": md.get("resource_title", ""),
                    "url": md.get("resource_url", ""),
                    "resource_id": lid,
                })

        return {
            "answer": result.answer,
            "sources": source_info,
            "links": links,
        }
    except Exception as e:
        raise Exception(f"Error during question answering: {str(e)}")
    

def retrieve_kb_context(question: str) -> str:
    """
    Use to search the Canadian immigration knowledge base, which contains
    policy content (visa programs, eligibility criteria) AND link resources
    (forms, templates, guides, official IRCC PDFs).

    Args:
        question: A self-contained query string with pronouns resolved.

    Returns:
        Retrieved context chunks with type annotations (content or link).
    """
    try:
        docs = rerank_docs(question, hybrid_retriever(question, k=6), top_n=3)
        return f"Retrieved context from knowledge base:\n\n{format_docs(docs)}"
    except (ConnectionError, TimeoutError):
        return "知识库检索暂时不可用(网络连接问题)。建议稍后重试。"
    except Exception as e:
        print(f"[ERROR] retrieve_kb_context: {type(e).__name__}: {e}")
        return "知识库检索遇到未知问题, 建议稍后重试或联系支持团队。"


if __name__ == "__main__":
    print("欢迎使用移民咨询系统! 输入 'q' 退出。")
    while True:
        user_question = input("请输入你的问题: ")
        if user_question.lower() == "q":
            print("Exiting the program.")
            exit(0)
        result = ask(user_question, session_id="default")
        print(f"\n答案: {result['answer']}")
        if result["links"]:
            print("\n相关资源:")
            for link in result["links"]:
                print(f"  - {link['title']}: {link['url']}")
        print(f"\n来源: {result['sources']}\n")