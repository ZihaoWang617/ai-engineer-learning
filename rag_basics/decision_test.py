from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from agent_graph_conditional import should_continue, AgentState

state_a = AgentState(messages=[HumanMessage(content="你好")])
state_b = AgentState(messages=[HumanMessage(content="查BCPNP"), AIMessage(content="", tool_calls=[{"name": "search", "args": {"q": "BC PNP"}, "id": "1"}])])
state_c = AgentState(messages = [HumanMessage("查 BC PNP"), AIMessage("", tool_calls=[{"name":"search","args":{"q":"BC PNP"},"id":"1"}]), ToolMessage(content="BC PNP 有 5 个 stream", tool_call_id="1"), AIMessage("根据搜索结果，BC PNP 有 5 个 stream，分别是...", tool_calls=[])])

if __name__ == "__main__":
    print("A:", should_continue(state_a))
    print("B:", should_continue(state_b))
    print("C:", should_continue(state_c))