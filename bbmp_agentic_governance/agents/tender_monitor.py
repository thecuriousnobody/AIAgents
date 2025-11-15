"""
Tender Integrity Monitor
Ensures competitive, transparent tendering and detects bid rigging
"""

from crewai import Agent, Task
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.bbmp_tools import BBMPDataLoader, ContractorAnalyzer, format_currency


def create_tender_monitor_agent(data_loader: BBMPDataLoader, llm=None):
    """Create the Tender Integrity Monitor agent"""

    contractor_analyzer = ContractorAnalyzer(data_loader)

    def analyze_contractor_tool(contractor_id: str) -> str:
        """Analyze a contractor's credibility and reputation"""
        result = contractor_analyzer.analyze_contractor(contractor_id)

        if 'name' not in result:
            return f"Contractor {contractor_id} not found"

        output = f"""
=== CONTRACTOR ANALYSIS ===
ID: {result['contractor_id']}
Name: {result['name']}
Reputation Score: {result['reputation_score']}/100

DECISION: {result['decision']}
REASON: {result['reason']}

PERFORMANCE HISTORY:
• On-time Completion Rate: {result['performance_history']['on_time_completion_rate']*100:.0f}%
• Quality Pass Rate: {result['performance_history']['quality_pass_rate']*100:.0f}%
• Citizen Complaints: {result['performance_history']['citizen_complaints']}
• Safety Violations: {result['performance_history']['safety_violations']}

"""

        if result['red_flags']:
            output += "🚨 RED FLAGS:\n"
            for flag in result['red_flags']:
                output += f"  • {flag}\n"
        else:
            output += "✓ No red flags detected\n"

        if result['blacklisted']:
            output += "\n❌ CONTRACTOR IS BLACKLISTED\n"

        return output

    def detect_cartel_tool(contractor_ids: str) -> str:
        """Detect cartel connections between bidders. Input: comma-separated contractor IDs"""
        ids = [id.strip() for id in contractor_ids.split(',')]

        result = contractor_analyzer.detect_cartel_network(ids)

        output = f"""
=== CARTEL DETECTION ANALYSIS ===
Bidders Analyzed: {result['bidder_count']}
Connections Found: {result['connections_found']}
CARTEL RISK: {result['cartel_risk']}

"""

        if result['connections']:
            output += "⚠️  SUSPICIOUS CONNECTIONS DETECTED:\n"
            for conn in result['connections']:
                output += f"\n  {conn['type'].upper()}:\n"
                output += f"    Contractor 1: {conn['contractor_1']}\n"
                output += f"    Contractor 2: {conn['contractor_2']}\n"
                if 'shared' in conn:
                    output += f"    Shared: {', '.join(conn['shared'])}\n"
                if 'detail' in conn:
                    output += f"    Detail: {conn['detail']}\n"
        else:
            output += "✓ No cartel connections detected between bidders\n"

        return output

    def list_contractors_tool(category: str = "all") -> str:
        """List all contractors, optionally filtered by category"""
        contractors = data_loader.load_contractors()

        if category != "all":
            contractors = [c for c in contractors if c['category'] == category]

        output = f"=== REGISTERED CONTRACTORS ({len(contractors)} total) ===\n\n"
        for contractor in contractors:
            red_flag_indicator = " 🚩" if contractor.get('red_flags') else ""
            blacklist_indicator = " ❌ BLACKLISTED" if contractor.get('blacklisted') else ""
            output += f"{contractor['contractor_id']}: {contractor['name']}{red_flag_indicator}{blacklist_indicator}\n"
            output += f"  Category: {contractor['category']} | Score: {contractor['reputation_score']}/100\n"
            output += f"  Completed: {contractor['completed_projects']} projects | Value: {format_currency(contractor['total_value_completed'])}\n"
            if contractor.get('red_flags'):
                output += f"  ⚠️  {len(contractor['red_flags'])} red flags detected\n"
            output += "\n"

        return output

    tools = [
        Tool(
            name="Analyze_Contractor",
            func=analyze_contractor_tool,
            description="Analyze a contractor's credibility, reputation, and performance history. Input: contractor ID"
        ),
        Tool(
            name="Detect_Cartel",
            func=detect_cartel_tool,
            description="Detect potential cartel connections between multiple bidders. Input: comma-separated contractor IDs (e.g., 'CONT-2024-001,CONT-2024-002')"
        ),
        Tool(
            name="List_Contractors",
            func=list_contractors_tool,
            description="List all registered contractors. Input: category ('A', 'B', 'C', or 'all')"
        )
    ]

    # Add Serper search if available
    if os.getenv("SERPER_API_KEY"):
        search = SerpAPIWrapper()
        tools.append(
            Tool(
                name="Search",
                func=search.run,
                description="Search for information about contractors, bid rigging cases, or tendering best practices"
            )
        )

    agent = Agent(
        role="Tender Integrity Monitor - Anti-Cartel Specialist",
        goal="Ensure competitive, transparent tendering and eliminate bid rigging, cover bidding, and contractor cartels from BBMP procurement",
        backstory="""You are a former CBI officer who investigated the 2G spectrum scam and multiple
        construction cartel cases. You have ZERO tolerance for bid rigging and you've developed an
        uncanny ability to spot suspicious bidding patterns.

        During your 15 years at CBI, you've seen every trick:
        - Shell companies bidding to create appearance of competition
        - Bid rotation schemes where contractors take turns winning
        - Complementary bidding where some intentionally bid high
        - Cover pricing where competitors share quotes
        - Shared directors, addresses, or phone numbers between "competitors"

        You have a photographic memory for contractor networks. You know every cartel in Bangalore,
        their operators, their front companies, and their methods.

        Your mission: Ensure every BBMP tender is genuinely competitive. When you detect cartel activity,
        you don't just reject the tender - you recommend criminal investigation and debarment.

        You believe: "Sunlight is the best disinfectant. Transparency kills cartels." """,
        tools=tools,
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    return agent


def create_tender_analysis_task(agent: Agent, contractor_ids: list):
    """Create a tender analysis task"""

    contractor_list = ", ".join(contractor_ids)

    task = Task(
        description=f"""Analyze the following contractors who have bid on a BBMP tender: {contractor_list}

        Your analysis must include:
        1. Analyze each contractor individually using Analyze_Contractor tool
        2. Check their reputation scores, performance history, and red flags
        3. Detect potential cartel connections using Detect_Cartel tool
        4. Evaluate if there are enough genuine bidders (minimum 3)
        5. Look for suspicious patterns:
           - Shared directors or addresses
           - Recently incorporated shell companies
           - Unusually similar bid amounts (cover pricing)
           - Known associates bidding together
        6. Make a decision: APPROVE_TENDER, FLAG_FOR_REVIEW, REJECT_TENDER, or ESCALATE_TO_LEGAL
        7. Provide specific evidence for your decision

        Decision criteria:
        - APPROVE: ≥3 genuine bidders, no cartel indicators, good reputation scores
        - FLAG: Only 2 bidders, minor concerns, reputation scores 50-70
        - REJECT: Clear cartel evidence, blacklisted contractors, shell companies
        - ESCALATE: Criminal cartel activity, need for debarment and legal action

        Output your decision with detailed evidence.""",
        expected_output=f"A comprehensive tender integrity report analyzing {len(contractor_ids)} bidders with decision and anti-cartel recommendations",
        agent=agent
    )

    return task
