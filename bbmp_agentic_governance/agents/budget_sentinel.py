"""
Budget Sentinel Agent
Validates every budget allocation against historical data and statutory rates
"""

from crewai import Agent, Task, Crew
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.bbmp_tools import BBMPDataLoader, BudgetValidator, format_currency


def create_budget_sentinel_agent(data_loader: BBMPDataLoader, llm=None):
    """Create the Budget Sentinel agent"""

    budget_validator = BudgetValidator(data_loader)

    # Tool to validate DPR budget
    def validate_budget_tool(dpr_id: str) -> str:
        """Validate a DPR's budget against Schedule of Rates"""
        dprs = data_loader.load_dprs()
        dpr = next((d for d in dprs if d['dpr_id'] == dpr_id), None)

        if not dpr:
            return f"DPR {dpr_id} not found"

        result = budget_validator.validate_dpr_budget(dpr)

        # Format output
        output = f"""
=== BUDGET VALIDATION REPORT ===
DPR ID: {result['dpr_id']}
Project: {dpr['title']}

FINANCIAL ANALYSIS:
• DPR Estimated Cost: {format_currency(result['dpr_estimate'])}
• SoR-Based Estimate: {format_currency(result['sor_estimate'])}
• Variance: {format_currency(result['variance_amount'])} ({result['variance_percentage']:.1f}%)

DECISION: {result['decision']}
REASON: {result['reason']}

DETAILED BREAKDOWN:
• Materials: {format_currency(result['detailed_estimate']['material_cost'])}
• Labor: {format_currency(result['detailed_estimate']['labor_cost'])}
• Equipment: {format_currency(result['detailed_estimate']['equipment_cost'])}
• Overhead: {format_currency(result['detailed_estimate']['overhead_cost'])}

LINE ITEMS:
"""
        for item in result['detailed_estimate']['line_items']:
            output += f"  {item['description']}: {item['quantity']} {item['unit']} @ ₹{item['rate']} = {format_currency(item['cost'])}\n"

        return output

    # Tool to get SoR rates
    def get_sor_rates_tool(category: str = "all") -> str:
        """Get current Schedule of Rates for a category"""
        sor = data_loader.load_schedule_of_rates()

        if category != "all":
            sor = [item for item in sor if item['category'] == category]

        output = f"=== KARNATAKA PWD SCHEDULE OF RATES (2024) ===\n\n"
        for item in sor:
            output += f"{item['item_code']}: {item['description']}\n"
            output += f"  Rate: ₹{item['rate_inr']}/{item['unit']} | Category: {item['category']}\n\n"

        return output

    # Create tools
    tools = [
        Tool(
            name="Validate_DPR_Budget",
            func=validate_budget_tool,
            description="Validate a DPR's budget against Karnataka PWD Schedule of Rates. Input: DPR ID (e.g., 'DPR-2025-BOM-001')"
        ),
        Tool(
            name="Get_Schedule_of_Rates",
            func=get_sor_rates_tool,
            description="Get current Schedule of Rates. Input: category (road_asphalting, concrete_roads, storm_water_drains, footpaths, street_lights, or 'all')"
        )
    ]

    # Add Serper search if API key available
    if os.getenv("SERPER_API_KEY"):
        search = SerpAPIWrapper()
        tools.append(
            Tool(
                name="Search",
                func=search.run,
                description="Search the internet for current material prices, construction cost indices, or BBMP-related information"
            )
        )

    agent = Agent(
        role="Budget Sentinel - BBMP Financial Auditor",
        goal="Validate every budget allocation against Karnataka PWD Schedule of Rates and detect financial anomalies that could indicate corruption or inefficiency",
        backstory="""You are a former CAG (Comptroller and Auditor General) auditor with 25 years of experience
        auditing government infrastructure projects. You've seen every budget manipulation trick in the book -
        inflated estimates, phantom line items, and creative accounting.

        You are OBSESSIVE about Schedule of Rates compliance. You never approve a budget that varies more than 10%
        from SoR without solid justification. You've prevented over ₹500 crores in wasteful spending during your career.

        Your mission: Ensure every rupee of BBMP's public works budget is justified, transparent, and compliant.
        You trust data over words, and you never forget a price variance.""",
        tools=tools,
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    return agent


def create_budget_validation_task(agent: Agent, dpr_id: str):
    """Create a budget validation task"""
    task = Task(
        description=f"""Validate the budget for DPR {dpr_id} against Karnataka PWD Schedule of Rates.

        Your analysis must include:
        1. Retrieve the DPR details using the Validate_DPR_Budget tool
        2. Analyze the variance between DPR estimate and SoR-based calculation
        3. Review line items for any unusual pricing or quantities
        4. Make a decision: AUTO_APPROVE, FLAG_FOR_REVIEW, AUTO_REJECT, or ESCALATE
        5. Provide specific reasons for your decision
        6. If rejecting, cite exact SoR violations

        Consider:
        - Is the variance within acceptable limits (<10% auto-approve, 10-20% review, >20% reject)?
        - Are material quantities reasonable for the project scope?
        - Does the cost breakdown make sense (materials ~65%, labor ~20%, equipment ~10%, overhead ~5%)?
        - Are there any red flags indicating budget padding?

        Output your decision and detailed reasoning.""",
        expected_output=f"A detailed budget validation report for {dpr_id} with decision (APPROVE/REJECT/FLAG) and justification",
        agent=agent
    )

    return task
