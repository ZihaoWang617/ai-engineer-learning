"""
agent_with_mcp.py
- 用 MultiServerMCPClient 连接 mcp-learning/server_v2.py
- 从 server 拉取 tools,替换原来 hardcoded 的 get_processing_time
- LangGraph 结构保持 Day 43-44 的形态
"""

import asyncio
import os
from typing import Annotated, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────
# State 不变(和 Day 43-44 一样)
# ─────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# ─────────────────────────────────────────
# TODO #1 ─ 填你自己的 absolute path
# ─────────────────────────────────────────
SERVER_PATH = os.path.expanduser("~/Desktop/ai-engineer-learning/mcp-learning/server_v3.py")


# ─────────────────────────────────────────
# 路由函数(和原版本一样,不需要改)
# ─────────────────────────────────────────
def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


# ─────────────────────────────────────────
# Build graph ─ 关键变化在这里
# ─────────────────────────────────────────
async def build_graph():
    # Step A: 创建 MCP client,声明要连哪个 server
    client = MultiServerMCPClient({
        "immigration": {
            "command": "python",
            "args": [SERVER_PATH],
            "transport": "stdio",
        }
    })

    # Step B: 从 server 拉取 tools(adapter 自动把 MCP Tool → LangChain Tool)
    # TODO #2 ─ get_tools() 是 async 方法。下面这行需要补什么关键字?

    tools = await client.get_tools()  # ← 这里漏了一个东西,会报错

    # Step C: bind 到 LLM(和原版本一样,只是 tools 不再 hardcoded)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    def llm_node(state: AgentState) -> dict:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    # Step D: 组装 graph(完全和 Day 43-44 一样)
    builder = StateGraph(AgentState)
    builder.add_node("llm", llm_node)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "llm")
    builder.add_conditional_edges("llm", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "llm")

    return builder.compile()


# ─────────────────────────────────────────
# Main ─ async 入口
# ─────────────────────────────────────────
async def main():
    graph = await build_graph()

    # TODO #3 ─ 设计一个会触发 get_immigration_program_summary 的问题
    # 提示:tool 的 description 说什么时候该用?
    test_query = "BC PNP Tech 的要求是什么?"

    result = await graph.ainvoke({
        "messages": [HumanMessage(content=test_query)]
    })

    for msg in result["messages"]:
        print(f"--- {type(msg).__name__} ---")
        print(f"content: {msg.content}")
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"tool_calls: {msg.tool_calls}")
        print()


if __name__ == "__main__":
    asyncio.run(main())