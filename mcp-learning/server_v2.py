from mcp.server.fastmcp import FastMCP

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
    if program_code not in PROGRAMS:
        raise ValueError(
            f"Unknown program_code: '{program_code}'. "
            f"Available codes: {list(PROGRAMS.keys())}"
        )
    return PROGRAMS[program_code]


if __name__ == "__main__":
    mcp.run()