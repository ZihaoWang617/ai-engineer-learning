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

@tool
def check_processing_time(visa_type: str) -> str:
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
    return f"未找到 '{visa_type}' 的处理时间数据，请尝试： study permit, work permit, visitor visa, pr card."

def validate_eligibility(program: str, years_of_experience: int) -> str:
    """检查申请人是否符合特定移民项目的基本资格。
    需要两个参数：
    - program：移民项目名称，例如 'express entry'、'bc pnp'、'atlantic immigration'
    - years_of_experience：申请人的工作经验年数，必须是正整数
    不适用于查询处理时间或政策细节，仅用于资格判断。
    """
    if years_of_experience <0:
        return "错误：工作经验年数不能为负数"
    eligibility_rules = {
        "express entry": {
            "min_years": 1,
            "message": "Express Entry 要求至少 1 年符合资格的工作经验（NOC TEER 0/1/2/3）"
        },
        "bc pnp": {
            "min_years": 2,
            "message": "BC PNP Skills Immigration 要求至少 2 年相关工作经验"
        },
        "atlantic immigration": {
            "min_years": 1,
            "message": "Atlantic Immigration Program 要求至少 1 年全职工作经验"
        },
    }
    program_lower = program.lower()
    for key, rules in eligibility_rules.items():
        if key in program_lower:
            if years_of_experience >= rules["min_years"]:
                return f"✅ 符合 {key} 的基本工作经验要求。{rules['message']}"
            else:
                return f"❌ 不符合 {key} 的要求。{rules['message']}，您目前有 {years_of_experience} 年经验"
    return f"未找到 '{program}' 的资格数据，支持查询：express entry、bc pnp、atlantic immigration"


tools = [calculate, search_immigration_policy, check_processing_time, validate_eligibility]

agent = create_agent(llm, tools)

if __name__ == "__main__":
    result = agent.invoke({
        "messages": [HumanMessage(content="工作签证的情况怎么样？")]
    })
    for message in result["messages"]:
        print(f"\n[{message.type}]: {message.content}")