from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

@tool
def calculate(expression: str) -> str:
    """计算数学表达式，输入必须是合法的 Python 数学表达式，例如 '100 + 200 * 3'"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算出错：{str(e)}"

@tool
def search_immigration_policy(query: str) -> str:
    """查询加拿大移民政策信息，例如 Express Entry 分数线、BC PNP 要求等"""
    mock_data = {
        "express entry": "Express Entry 最新一轮 CRS 分数线为 491 分（2026年4月）",
        "bc pnp": "BC PNP Tech Pilot 要求：BC省雇主、NOC TEER 0/1/2/3、无最低分要求",
        "lmia": "LMIA 处理时间：普通流程 2-6 个月，全球人才流最快 2 周",
    }
    query_lower = query.lower()
    for key, value in mock_data.items():
        if key in query_lower:
            return value
    return "未找到相关政策信息，请尝试更具体的查询关键词"

tools = [calculate, search_immigration_policy]

agent = create_agent(llm, tools)

if __name__ == "__main__":
    result = agent.invoke({
        "messages": [HumanMessage(content="Express Entry 最新分数线是多少？另外帮我算一下 491 乘以 2 是多少")]
    })
    for message in result["messages"]:
        print(f"\n[{message.type}]: {message.content}")