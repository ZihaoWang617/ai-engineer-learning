from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
def build_graph():

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools([get_processing_time])

    def llm_node(state: AgentState) -> dict:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    tool_node = ToolNode([get_processing_time])
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("llm_call", llm_node)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("llm_final", llm_node)

    graph_builder.add_edge(START, "llm_call")
    graph_builder.add_edge("llm_call", "tools")
    graph_builder.add_edge("tools", "llm_final")
    graph_builder.add_edge("llm_final", END)

    return graph_builder.compile()


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

    
if __name__ == "__main__":

    graph = build_graph()
    result = graph.invoke({"messages": [HumanMessage("学签需要多久")]})

    for msg in result["messages"]:
        print(f"---{type(msg).__name__}---")
        print(f"content: {msg.content}")
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"tool_calls: {msg.tool_calls}")
        print()