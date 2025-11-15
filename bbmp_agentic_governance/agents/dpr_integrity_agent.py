"""
DPR Integrity Agent
Verifies Detailed Project Reports have legitimate need, proper surveys, and realistic estimates
"""

from crewai import Agent, Task
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.bbmp_tools import BBMPDataLoader, DPRValidator, AnomalyDetector, format_currency


def create_dpr_integrity_agent(data_loader: BBMPDataLoader, llm=None):
    """Create the DPR Integrity agent"""

    dpr_validator = DPRValidator(data_loader)
    anomaly_detector = AnomalyDetector(data_loader)

    def validate_dpr_tool(dpr_id: str) -> str:
        """Validate a DPR's completeness and authenticity"""
        dprs = data_loader.load_dprs()
        dpr = next((d for d in dprs if d['dpr_id'] == dpr_id), None)

        if not dpr:
            return f"DPR {dpr_id} not found"

        validation_result = dpr_validator.validate_documentation(dpr)
        anomalies = anomaly_detector.detect_anomalies_in_dpr(dpr)

        output = f"""
=== DPR INTEGRITY VALIDATION REPORT ===
DPR ID: {validation_result['dpr_id']}
Project: {dpr['title']}
Zone: {dpr['zone']}, Ward: {dpr['ward']}
Type: {dpr['project_type']}

DOCUMENTATION STATUS:
✓ Critical Issues: {len(validation_result['critical_issues'])}
⚠ Warnings: {len(validation_result['warnings'])}
✓ Justification Quality: {validation_result['justification_quality']}

DECISION: {validation_result['decision']}
REASON: {validation_result['reason']}
"""

        if validation_result['critical_issues']:
            output += "\n❌ CRITICAL ISSUES:\n"
            for issue in validation_result['critical_issues']:
                output += f"  • {issue}\n"

        if validation_result['warnings']:
            output += "\n⚠️  WARNINGS:\n"
            for warning in validation_result['warnings']:
                output += f"  • {warning}\n"

        if anomalies:
            output += "\n🚨 ANOMALIES DETECTED:\n"
            for anomaly in anomalies:
                output += f"  • {anomaly}\n"

        output += f"""
PROJECT DETAILS:
• Estimated Cost: {format_currency(dpr['estimated_cost'])}
• Timeline: {dpr['estimated_timeline_days']} days
• Citizen Complaints: {dpr['citizen_complaints']}
• Ward Committee Approval: {dpr.get('ward_committee_approval', 'MISSING')}

JUSTIFICATION:
{dpr['justification']}
"""

        return output

    def check_duplicates_tool(dpr_id: str) -> str:
        """Check for duplicate or overlapping projects"""
        dprs = data_loader.load_dprs()
        dpr = next((d for d in dprs if d['dpr_id'] == dpr_id), None)

        if not dpr:
            return f"DPR {dpr_id} not found"

        duplicates = dpr_validator.check_duplicate_projects(dpr)

        if duplicates:
            output = f"⚠️  DUPLICATE PROJECT DETECTED for {dpr_id}:\n"
            for dup in duplicates:
                output += f"  • {dup}\n"
        else:
            output = f"✓ No duplicate projects found for {dpr_id}"

        return output

    def list_all_dprs_tool(zone: str = "all") -> str:
        """List all DPRs, optionally filtered by zone"""
        dprs = data_loader.load_dprs()

        if zone != "all":
            dprs = [d for d in dprs if d['zone'].lower() == zone.lower()]

        output = f"=== DPRs IN SYSTEM ({len(dprs)} total) ===\n\n"
        for dpr in dprs:
            flags_indicator = " 🚩" if dpr.get('flags') else ""
            output += f"{dpr['dpr_id']}: {dpr['title']}{flags_indicator}\n"
            output += f"  Zone: {dpr['zone']} | Cost: {format_currency(dpr['estimated_cost'])} | Complaints: {dpr['citizen_complaints']}\n"
            if dpr.get('flags'):
                output += f"  ⚠️  Flags: {len(dpr['flags'])} issues detected\n"
            output += "\n"

        return output

    tools = [
        Tool(
            name="Validate_DPR",
            func=validate_dpr_tool,
            description="Validate a DPR's documentation completeness and authenticity. Input: DPR ID"
        ),
        Tool(
            name="Check_Duplicate_Projects",
            func=check_duplicates_tool,
            description="Check if a DPR is a duplicate of existing projects. Input: DPR ID"
        ),
        Tool(
            name="List_DPRs",
            func=list_all_dprs_tool,
            description="List all DPRs in the system. Input: zone name or 'all'"
        )
    ]

    # Add Serper search if available
    if os.getenv("SERPER_API_KEY"):
        search = SerpAPIWrapper()
        tools.append(
            Tool(
                name="Search",
                func=search.run,
                description="Search for information about BBMP projects, citizen complaints, or infrastructure standards"
            )
        )

    agent = Agent(
        role="DPR Integrity Agent - Project Validation Specialist",
        goal="Verify that every Detailed Project Report has legitimate need, proper surveys, realistic costs, and genuine community demand before sanctioning",
        backstory="""You are a civil engineer with 20 years of experience in urban infrastructure. You've worked
        on hundreds of road projects across Karnataka and you've seen it all - inflated DPRs with fake traffic studies,
        duplicate projects proposed multiple times, and unnecessary works pushed by political pressure without citizen need.

        You built your reputation on calling out manufactured justifications. You insist on REAL data: actual traffic
        counts, genuine soil tests, documented citizen complaints, and ward committee approvals.

        You have a particular nose for detecting:
        - Projects with no citizen complaints (who asked for this?)
        - Missing or outdated surveys
        - Duplicate projects within 500m radius
        - Vague justifications that don't cite specific problems

        Your mission: Ensure BBMP only builds infrastructure that citizens actually need and want.""",
        tools=tools,
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    return agent


def create_dpr_validation_task(agent: Agent, dpr_id: str):
    """Create a DPR validation task"""
    task = Task(
        description=f"""Thoroughly validate DPR {dpr_id} for integrity and authenticity.

        Your analysis must include:
        1. Use Validate_DPR tool to get complete DPR details
        2. Check for duplicate projects using Check_Duplicate_Projects
        3. Analyze the justification quality - is it specific and evidence-based?
        4. Verify required documentation:
           - Traffic study (if applicable)
           - Soil tests
           - Citizen complaints data
           - Ward committee approval
        5. Assess if this project addresses genuine community need
        6. Make a decision: APPROVE, FLAG_FOR_REVIEW, or REJECT
        7. Provide specific reasons

        Red flags to watch for:
        - Zero citizen complaints (why is this being built?)
        - Missing traffic study or soil tests
        - Vague justifications ("road maintenance required")
        - Duplicate projects in same area
        - No ward committee involvement

        Output your decision with detailed reasoning.""",
        expected_output=f"A comprehensive DPR integrity validation report for {dpr_id} with decision and evidence-based justification",
        agent=agent
    )

    return task
