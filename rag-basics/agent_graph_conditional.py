from typing import Annotated, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def get_processing_time(visa_type: str) -> str:
    """查询特定签证类别的政府处理时间。
    输入签证类别名称，例如 'study permit'、'work permit'、'visitor visa'、'pr card'。
    返回当前官方处理时间估计。
    不适用于查询政策条件或申请资格，仅用于处理时间查询。
    """
    processing_times = {
        "study permit": "学习签证处理时间：线上申请约 4-12 周",
        "work permit": "工作签证处理时间：线上申请约 3-27 周，视类别而定",
        "visitor visa": "旅游签证处理时间：线上申请约 2-8 周",
        "pr card": "PR Card 续签处理时间：约 5-14 个月",
    }
    
    visa_lower = visa_type.lower()
    for key, value in processing_times.items():
        if key in visa_lower:
            return value
    return "Unknown visa type"

def should_continue(state: AgentState) -> Literal["use_tools", "finish"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "use_tools"
    return "finish"

def build_graph():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools([get_processing_time])
    def llm_node(state: AgentState)-> dict:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    tool_node = ToolNode([get_processing_time])

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("llm", llm_node)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_edge(START, "llm")
    graph_builder.add_edge("tools", "llm")
    graph_builder.add_conditional_edges(source = "llm", path = should_continue, path_map = {"use_tools": "tools", "finish": END})

    return graph_builder.compile()

if __name__ == "__main__":
    graph = build_graph()
    query1 = graph.invoke(AgentState(messages=[HumanMessage(content="学签需要多久")]))
    query2 = graph.invoke(AgentState(messages=[HumanMessage(content="你好")]))

    for msg in query1["messages"]:
        print(f"---{type(msg).__name__}---")
        print(f"content: {msg.content}")
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"tool_calls: {msg.tool_calls}")
        print()
    for msg in query2["messages"]:
        print(f"---{type(msg).__name__}---")
        print(f"content: {msg.content}")
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"tool_calls: {msg.tool_calls}")
        print()
