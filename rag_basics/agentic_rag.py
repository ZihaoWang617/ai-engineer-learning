from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_query import format_docs, hybrid_retriever, rerank_docs

class AgenticRAGState(TypedDict):
    question: str
    retrieved_docs: list
    answer: str
    evaluation_score: str
    iteration_count: int
    needs_retrieval: bool

llm = ChatOpenAI(model = "gpt-4o-mini", temperature=0)

def query_analysis(state: AgenticRAGState) -> dict:
    prompt = f"""这个问题需要查询移民政策知识库才能回答吗？回答 yes 或 no。
    e.g. 
    "Question: 2024年美国的移民政策是什么？Answer: yes"
    "Question: 你好。 Answer: no"
    "Question: 今天天气怎么样？ Answer: no" 
    Question: {state['question']} Answer:
    """
    
    response = llm.invoke(prompt)
    content = response.content.strip().lower()
    needs_retrieval = "yes" in content
    return {
        "needs_retrieval": needs_retrieval,
        "iteration_count": 0
    }

def retrieve(state: AgenticRAGState) -> dict:
    docs = rerank_docs(
        state["question"],
        hybrid_retriever(state["question"], k = 6),
        top_n =3
    )
    return {
        "retrieved_docs": docs,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def self_evaluate(state: AgenticRAGState) -> dict:
    docs_str = format_docs(state["retrieved_docs"])
    prompt = f"""你是一个严格的检索质量评估员。

任务：判断给定的检索文档是否包含足够信息来回答用户问题。

评估标准：
- 如果文档包含直接回答问题的相关信息 → 回答 "good"
- 如果文档完全不相关 / 信息缺失 / 偏题 → 回答 "bad"

⚠️ 严格标准：宁可保守说 bad 触发重试，也不要错误说 good 让用户拿到错答案。

用户问题：{state['question']}
检索到的文档：{docs_str}
重要：你的回答必须是一个单词 good 或 bad，不要任何解释、句号或其他内容。
"""
    response = llm.invoke(prompt)
    content = response.content.strip().lower()
    if "bad" in content:
        evaluation_score = "bad"
    elif "good" in content:
        evaluation_score = "good"
    else:
        evaluation_score = "bad"
    return {
        "evaluation_score": evaluation_score
    }
    
def generate(state: AgenticRAGState) -> dict:
    docs = state.get("retrieved_docs")
    if not docs:
        prompt = f"用户问: {state['question']}\n请友好地回答："
    else:
        docs_str = format_docs(docs)
        eval_warning = ""
        if state.get("evaluation_score") == "bad":
            eval_warning = "\n\n⚠️ 检索到的文档可能不完全相关。如果文档信息不足以回答，请明确告诉用户'我没有相关信息'，不要编造。"
        prompt =  f"""你是移民顾问，只根据提供的内容回答，不要编造。
如果内容里没有答案，说"我没有相关信息"。{eval_warning}
检索到的文档：
{docs_str}
用户问题：{state['question']}
请给出你的回答："""
    response = llm.invoke(prompt)
    answer = response.content.strip()
    return {
        "answer": answer
    }
    
# Graph 接线（放在 if __name__ 之前）
def route_after_analysis(state: AgenticRAGState) -> str:
    if state["needs_retrieval"]:
        return "retrieve"
    return "generate"

def route_after_eval(state: AgenticRAGState) -> str:
    if state["evaluation_score"] == "good":
        return "generate"
    elif state["iteration_count"] < 2:
        return "retrieve"
    else:
        return "generate"

workflow = StateGraph(AgenticRAGState)

workflow.add_node("query_analysis", query_analysis)
workflow.add_node("retrieve", retrieve)
workflow.add_node("self_evaluate", self_evaluate)
workflow.add_node("generate", generate)

workflow.add_edge(START, "query_analysis")
workflow.add_conditional_edges(
    "query_analysis",
    route_after_analysis,
    {"retrieve": "retrieve", "generate": "generate"}
)
workflow.add_edge("retrieve", "self_evaluate")
workflow.add_conditional_edges(
    "self_evaluate",
    route_after_eval,
    {"retrieve": "retrieve", "generate": "generate"}
)
workflow.add_edge("generate", END)

app = workflow.compile()


if __name__ == "__main__":
    test_cases = [
        "你好",
        "BC PNP 的具体要求是什么",
        "什么是 ABCXYZ123 移民项目",
    ]
    
    for q in test_cases:
        print(f"\n{'='*60}\n问题：{q}\n{'='*60}")
        result = app.invoke({"question": q})
        print(f"答案：{result['answer']}")
        print(f"迭代次数：{result.get('iteration_count', 0)}")
        print(f"评估分数：{result.get('evaluation_score', 'N/A')}")