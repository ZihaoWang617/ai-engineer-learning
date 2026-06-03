from mcp.server.fastmcp import FastMCP
import json
from rag_basics.langchain_query import vectorstore, hybrid_retriever, rerank_docs
mcp = FastMCP("immigration-assistant")

PROGRAMS = {
    "BC_PNP_Tech": """BC PNP Tech (British Columbia Provincial Nominee Program - Tech stream)

Requirements:
- Valid full-time job offer from a BC employer in one of 35 eligible tech occupations (e.g., software engineer, data scientist, web developer)
- Offer must be indeterminate (no end date) or at least 12 months long at time of application
- Meet minimum wage requirement for the occupation in BC
- Score sufficient points on the BC PNP Skills Immigration Registration System (SIRS)

Processing time: approximately 2-3 months for provincial nomination, then 6-12 months for federal PR processing via Express Entry.

Official source: https://www.welcomebc.ca/Immigrate-to-B-C/BC-PNP""",

    "EE_CEC": """Express Entry - Canadian Experience Class (EE CEC)

Requirements:
- At least 1 year of skilled work experience in Canada within the last 3 years (full-time or equivalent part-time)
- Work experience must be in NOC TEER 0, 1, 2, or 3 occupations
- Meet language requirements: CLB 7 for TEER 0 or 1 occupations; CLB 5 for TEER 2 or 3 occupations
- No minimum education requirement, but education improves Comprehensive Ranking System (CRS) score
- Must not be in Canada on a study or work permit that prohibits applying for PR

Processing time: approximately 6 months after receiving an Invitation to Apply (ITA).

Official source: https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/eligibility/canadian-experience-class.html""",

    "OINP_Tech_Draw": """Ontario Immigrant Nominee Program - Tech Draw (Express Entry stream)

Requirements:
- Active Express Entry profile registered with IRCC
- Work experience in one of the eligible tech occupations targeted by OINP (e.g., software engineers, IT project managers, computer systems analysts)
- Have or intend to work in Ontario (job offer in Ontario is a strong asset but not always mandatory)
- Meet minimum CRS score as set in each OINP tech-targeted draw
- Meet federal Express Entry eligibility for CEC, FSW, or FST programs

Processing time: approximately 2-4 weeks for a provincial nomination letter from OINP, then 6 months for federal PR processing after receiving ITA via Express Entry (nomination adds 600 CRS points).

Official source: https://www.ontario.ca/page/oinp-express-entry-skilled-trades-stream""",
}

@mcp.tool()
def get_immigration_program_summary(program_code: str) -> str:
    """Returns detailed summary of a specific Canadian immigration program,
including eligibility requirements and processing time.

USE THIS WHEN:
- User asks about BCPNP Tech, EE CEC, or OINP Tech Draw programs
- User mentions a specific program code (e.g., BC_PNP_Tech, EE_CEC, OINP_Tech_Draw)

DO NOT USE WHEN:
- User asks a general question not tied to a specific program (e.g., "What immigration options do I have?")
- User asks about a program not in the knowledge base (e.g., SINP, AINP, Quebec skilled worker)

Returns a multi-line string with program details. Raises ValueError if program_code is not recognized."""
    query_map = {
        "BC_PNP_Tech": "BC PNP Tech stream requirements and processing time",
        "EE_CEC": "Express Entry Canadian Experience Class requirements",
        "OINP_Tech_Draw": "Ontario OINP Tech Draw Express Entry requirements",
    }

    if program_code not in PROGRAMS:
        raise ValueError(
            f"Unknown program_code: '{program_code}'. "
            f"Available codes: {list(PROGRAMS.keys())}"
        )
    query = query_map[program_code]

    candidates = hybrid_retriever(query, k = 6)
    top_docs = rerank_docs(query, candidates, top_n = 3)
    parts = [f"# {program_code}\n"]
    for doc in top_docs:
        source = doc.metadata.get("source", "unknown")
        chunk_idx = doc.metadata.get("chunk_index", "?")
        parts.append(f"## 来源: {source} 第{chunk_idx}块\n{doc.page_content}\n")
    return "\n".join(parts)


@mcp.tool()
def retrieve_documents(question: str) -> str:
    """Retrieves the most relevant passages from the Canadian immigration policy knowledge base for a given question.

USE THIS WHEN:
- User asks about immigration topics not tied to a specific program code
- User asks general questions: eligibility, documents, processing times, policy updates
- Examples: "What documents do I need for PR?", "How long does spousal sponsorship take?"

DO NOT USE WHEN:
- User asks about a specific program by name (use get_immigration_program_summary instead)
- User asks for the list of available programs (use programs://list resource)

Returns retrieved passages with inline source citations. Returns an empty-result message if nothing relevant is found."""
    
    candidates = hybrid_retriever(question, k=6)
    if not candidates:
        return "知识库中没有找到相关内容。"
    
    top_docs = rerank_docs(question, candidates, top_n=3)
    
    parts = ["# Retrieved passages\n"]
    for doc in top_docs:
        source = doc.metadata.get("source", "unknown")
        chunk_idx = doc.metadata.get("chunk_index", "?")
        parts.append(f"[来源:{source}, 第{chunk_idx}块]\n{doc.page_content}\n")
    
    return "\n".join(parts)


@mcp.resource("programs://list")
def list_programs() -> str:
    """Returns a json string listing all available immigration programs.
    USE THIS WHEN:
    - User asks "What programs are available?"
    - User asks for a list of programs
    DO NOT USE WHEN:
    - User asks about a specific program (e.g., "Tell me about BC PNP Tech")
    Returns a JSON string with program codes and names."""
    programs = [
        {"code": code, "name": content.split("\n")[0]}
        for code, content in PROGRAMS.items()
    ]
    return json.dumps({"programs": programs})

@mcp.prompt()
def evaluate_case(program_code: str, client_profile: str) -> str:
    """Generates a structured prompt for evaluating whether a client fits a specific Canadian immigration program.

    USE THIS WHEN:
    - User provides a client profile and asks to evaluate fit for a specific program
    - User wants a structured eligibility assessment with reasoning and next steps

    DO NOT USE WHEN:
    - User asks general questions about immigration not tied to a specific client case
    - User has not provided any client information
    - program_code is not in the knowledge base

    Returns a formatted Chinese prompt string. Raises KeyError if program_code unknown."""
    
    program_details = PROGRAMS[program_code]
    
    return f"""你是资深加拿大移民顾问,拥有多年案例处理经验。你的任务是根据客户档案,评估其是否符合 {program_code} 项目的申请要求。

# 项目要求
{program_details}

# 客户档案
{client_profile}

# 输出要求
请严格按以下结构输出评估结果:

1. **资格初判**:符合 / 不符合 / 信息不足(三选一)
2. **关键依据**:逐条对照项目要求,引用客户档案中具体内容作为支持
3. **缺失信息**:如果是"信息不足",列出还需要客户补充哪些信息才能判断
4. **下一步建议**:基于当前判断,客户应采取的具体行动

# 严格约束
- 只根据"客户档案"中明确提供的信息判断,不要假设、推测、或补充任何未提供的信息
- 如某条要求无法从档案中验证,标注为"信息不足",不要凭直觉判断
- 用专业但客户能理解的语言,避免过度堆砌法律术语"""


if __name__ == "__main__":
    mcp.run()