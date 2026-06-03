from typing import Annotated, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.types import Command, interrupt 
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
@tool
def submit_application(application_data: str) -> str:
    """
    当涉及到提交申请到政府系统的步骤时，使用此工具来模拟提交过程。
输入申请数据的字符串表示，例如申请表格的内容或相关信息。
返回提交结果的字符串，例如 "Application submitted successfully" 或 "Application submission failed"。 
    该工具模拟了提交过程中的人工干预，允许用户在提交前进行确认。
    """
    approval = interrupt({
    "action": "Submitting application to government system",
    "data_preview": application_data,
    "question": "Do you want to submit this application?"
})
    if approval == "approve":
        return "Application submitted successfully"
    elif approval == "reject":
        return "Application submission rejected by user."
    else:
        return f"Unknown approval value: {approval}. Cancelled by safety."
    
tools = [submit_application]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

def llm_node(state: AgentState)-> dict:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("llm", llm_node)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "llm")
    builder.add_conditional_edges("llm", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "llm")
    
    checkpointer = InMemorySaver() # 或者 SqliteSaver("checkpoint.db")
    graph = builder.compile(checkpointer=checkpointer)   # ← compile 时传 checkpointer
    return graph

if __name__ == "__main__":
    graph = build_graph()
    config = {"configurable": {"thread_id": "test_session_001"}}
    
    # 第一次 invoke
    result = graph.invoke(
        {"messages": [HumanMessage(content="请帮我提交 BC PNP 申请，申请人是 Alice Wang，护照号 E12345678")]},
        config=config
    )
    
    # ↓ Step 2 新增：处理 interrupt 循环
    while result.get("__interrupt__"):                  # ← 注意用 .get() 不用 []
        interrupt_obj = result["__interrupt__"][0]
        payload = interrupt_obj.value
        
        print("\n=== HUMAN APPROVAL NEEDED ===")
        print(f"Action:       {payload['action']}")
        print(f"Data preview: {payload['data_preview']}")
        print(f"Question:     {payload['question']}")
        
        user_answer = input("\nYour decision (approve/reject): ").strip().lower()
        
        result = graph.invoke(
            Command(resume=user_answer),               # ← keyword arg
            config=config                              # ← 同一 thread_id
        )
    
    # ↓ 循环外：打印最终结果
    print("\n=== FINAL ANSWER ===")
    print(result["messages"][-1].content)