"""
BBMP Agentic Governance System - Demo
Phase 0: Proof of Concept with Mock Data

This demo shows how AI agents can transform BBMP's Public Works Department
by automating corruption-vulnerable decision points.
"""

import os
import sys
from datetime import datetime
from crewai import Crew
from langchain_anthropic import ChatAnthropic

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.bbmp_tools import BBMPDataLoader
from agents.budget_sentinel import create_budget_sentinel_agent, create_budget_validation_task
from agents.dpr_integrity_agent import create_dpr_integrity_agent, create_dpr_validation_task
from agents.tender_monitor import create_tender_monitor_agent, create_tender_analysis_task


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_scenario(number, title, description):
    """Print scenario information"""
    print("\n" + "-" * 80)
    print(f"SCENARIO {number}: {title}")
    print("-" * 80)
    print(f"{description}\n")


def run_scenario_1_good_dpr():
    """Scenario 1: Legitimate project with proper documentation"""
    print_scenario(
        1,
        "LEGITIMATE PROJECT - HSR Layout Road Asphalting",
        """DPR-2025-BOM-001: Asphalting of 27th Main Road, HSR Layout
        • High citizen complaints (245)
        • Recent traffic study and soil tests
        • Ward committee approval
        • Cost within SoR limits

        EXPECTED: Agents should APPROVE this project"""
    )

    # Initialize
    data_loader = BBMPDataLoader(data_dir="data")

    # Use Claude Sonnet 4.5 via Anthropic
    llm = None
    if os.getenv("ANTHROPIC_API_KEY"):
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.1,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        print("✓ Using Claude Sonnet 4.5 via Anthropic API\n")
    else:
        print("⚠️  No ANTHROPIC_API_KEY found - using default LLM\n")

    # Create agents
    dpr_agent = create_dpr_integrity_agent(data_loader, llm=llm)
    budget_agent = create_budget_sentinel_agent(data_loader, llm=llm)

    # Create tasks
    dpr_task = create_dpr_validation_task(dpr_agent, "DPR-2025-BOM-001")
    budget_task = create_budget_validation_task(budget_agent, "DPR-2025-BOM-001")

    # Run crew
    crew = Crew(
        agents=[dpr_agent, budget_agent],
        tasks=[dpr_task, budget_task],
        verbose=True
    )

    print("\n🤖 LAUNCHING AI AGENTS...\n")
    result = crew.kickoff()

    print_header("SCENARIO 1 RESULTS")
    print(result)

    return result


def run_scenario_2_suspicious_dpr():
    """Scenario 2: Suspicious project with multiple red flags"""
    print_scenario(
        2,
        "SUSPICIOUS PROJECT - Service Road with Red Flags",
        """DPR-2025-BOM-002: Asphalting of Service Road, Hosur Road
        • NO citizen complaints (who asked for this?)
        • Old traffic study (>6 months)
        • NO soil test conducted
        • NO ward committee approval
        • Cost 35% HIGHER than SoR estimates

        EXPECTED: Agents should REJECT or FLAG this project"""
    )

    data_loader = BBMPDataLoader(data_dir="data")

    llm = None
    if os.getenv("ANTHROPIC_API_KEY"):
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.1,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    dpr_agent = create_dpr_integrity_agent(data_loader, llm=llm)
    budget_agent = create_budget_sentinel_agent(data_loader, llm=llm)

    dpr_task = create_dpr_validation_task(dpr_agent, "DPR-2025-BOM-002")
    budget_task = create_budget_validation_task(budget_agent, "DPR-2025-BOM-002")

    crew = Crew(
        agents=[dpr_agent, budget_agent],
        tasks=[dpr_task, budget_task],
        verbose=True
    )

    print("\n🤖 LAUNCHING AI AGENTS...\n")
    result = crew.kickoff()

    print_header("SCENARIO 2 RESULTS")
    print(result)

    return result


def run_scenario_3_duplicate_project():
    """Scenario 3: Duplicate project detection"""
    print_scenario(
        3,
        "DUPLICATE PROJECT DETECTION",
        """DPR-2025-BOM-004: Asphalting of 15th Cross, JP Nagar 7th Phase
        • Same road was proposed 8 months ago (DPR-2024-BOM-234)
        • NO citizen complaints
        • NO traffic study or soil tests
        • Vague justification

        EXPECTED: Agents should REJECT due to duplication"""
    )

    data_loader = BBMPDataLoader(data_dir="data")

    llm = None
    if os.getenv("ANTHROPIC_API_KEY"):
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.1,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    dpr_agent = create_dpr_integrity_agent(data_loader, llm=llm)

    dpr_task = create_dpr_validation_task(dpr_agent, "DPR-2025-BOM-004")

    crew = Crew(
        agents=[dpr_agent],
        tasks=[dpr_task],
        verbose=True
    )

    print("\n🤖 LAUNCHING AI AGENT...\n")
    result = crew.kickoff()

    print_header("SCENARIO 3 RESULTS")
    print(result)

    return result


def run_scenario_4_cartel_detection():
    """Scenario 4: Contractor cartel detection"""
    print_scenario(
        4,
        "BID RIGGING CARTEL DETECTION",
        """Analyzing tender with 3 bidders:
        • CONT-2024-001: Bangalore Infrastructure (Score: 82/100)
        • CONT-2024-004: Quick Build Construction (Score: 45/100)
        • CONT-2024-005: Fast Track Infra Solutions (Score: 42/100)

        Red flags:
        • CONT-2024-004 and CONT-2024-005 share director "Rajesh Gupta"
        • Both incorporated in 2023 (shell company indicators)
        • High complaint rates and poor performance

        EXPECTED: Agent should detect cartel and REJECT tender"""
    )

    data_loader = BBMPDataLoader(data_dir="data")

    llm = None
    if os.getenv("ANTHROPIC_API_KEY"):
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.1,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    tender_agent = create_tender_monitor_agent(data_loader, llm=llm)

    tender_task = create_tender_analysis_task(
        tender_agent,
        ["CONT-2024-001", "CONT-2024-004", "CONT-2024-005"]
    )

    crew = Crew(
        agents=[tender_agent],
        tasks=[tender_task],
        verbose=True
    )

    print("\n🤖 LAUNCHING AI AGENT...\n")
    result = crew.kickoff()

    print_header("SCENARIO 4 RESULTS")
    print(result)

    return result


def run_scenario_5_good_tender():
    """Scenario 5: Legitimate competitive tender"""
    print_scenario(
        5,
        "LEGITIMATE COMPETITIVE TENDER",
        """Analyzing tender with 3 reputable bidders:
        • CONT-2024-001: Bangalore Infrastructure (Score: 82/100)
        • CONT-2024-002: Karnataka Road Builders (Score: 88/100)
        • CONT-2024-006: Mega Infrastructure Corp (Score: 94/100)

        All contractors:
        • High reputation scores
        • Good performance history
        • No red flags
        • No shared directors or addresses

        EXPECTED: Agent should APPROVE tender"""
    )

    data_loader = BBMPDataLoader(data_dir="data")

    llm = None
    if os.getenv("ANTHROPIC_API_KEY"):
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.1,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    tender_agent = create_tender_monitor_agent(data_loader, llm=llm)

    tender_task = create_tender_analysis_task(
        tender_agent,
        ["CONT-2024-001", "CONT-2024-002", "CONT-2024-006"]
    )

    crew = Crew(
        agents=[tender_agent],
        tasks=[tender_task],
        verbose=True
    )

    print("\n🤖 LAUNCHING AI AGENT...\n")
    result = crew.kickoff()

    print_header("SCENARIO 5 RESULTS")
    print(result)

    return result


def main():
    """Main demo orchestrator"""
    print_header("BBMP AGENTIC GOVERNANCE SYSTEM - PHASE 0 DEMO")
    print("""
    🏛️  Automating Transparent Governance with AI Agents

    This demo showcases how AI agents can eliminate corruption at key decision points
    in BBMP's Public Works Department:

    1. DPR Integrity Agent - Validates project proposals
    2. Budget Sentinel - Ensures SoR compliance
    3. Tender Integrity Monitor - Detects bid rigging

    We'll run through 5 scenarios demonstrating both legitimate and suspicious cases.
    """)

    print("\nChoose demo mode:")
    print("1. Run all scenarios (takes ~10-15 minutes)")
    print("2. Scenario 1: Legitimate Project (APPROVE)")
    print("3. Scenario 2: Suspicious Project (REJECT)")
    print("4. Scenario 3: Duplicate Detection (REJECT)")
    print("5. Scenario 4: Cartel Detection (REJECT)")
    print("6. Scenario 5: Good Tender (APPROVE)")
    print("7. Quick demo (Scenarios 2 & 4 - show corruption detection)")

    choice = input("\nEnter choice (1-7): ").strip()

    scenarios = {
        '1': [run_scenario_1_good_dpr, run_scenario_2_suspicious_dpr,
              run_scenario_3_duplicate_project, run_scenario_4_cartel_detection,
              run_scenario_5_good_tender],
        '2': [run_scenario_1_good_dpr],
        '3': [run_scenario_2_suspicious_dpr],
        '4': [run_scenario_3_duplicate_project],
        '5': [run_scenario_4_cartel_detection],
        '6': [run_scenario_5_good_tender],
        '7': [run_scenario_2_suspicious_dpr, run_scenario_4_cartel_detection]
    }

    if choice in scenarios:
        for scenario_func in scenarios[choice]:
            scenario_func()
            if len(scenarios[choice]) > 1:
                input("\n\nPress Enter to continue to next scenario...")
    else:
        print("Invalid choice. Running quick demo (Scenarios 2 & 4)...")
        run_scenario_2_suspicious_dpr()
        input("\n\nPress Enter to continue to next scenario...")
        run_scenario_4_cartel_detection()

    print_header("DEMO COMPLETE")
    print("""
    🎯 KEY TAKEAWAYS:

    ✓ AI agents can automatically validate DPRs against objective criteria
    ✓ Budget violations are detected instantly using Schedule of Rates
    ✓ Duplicate projects are flagged before any money is allocated
    ✓ Contractor cartels are exposed through network analysis
    ✓ Every decision is transparent, auditable, and based on data

    💰 IMPACT: This system could save BBMP 20-30% of its ₹6,000 crore annual budget
              = ₹1,200-1,800 crores saved per year

    🚀 NEXT STEPS:
    - Integrate real BBMP data
    - Add blockchain for immutable audit trail
    - Build public dashboard
    - IoT sensors for quality verification
    - Deploy pilot in one zone

    📧 Contact: github.com/thecuriousnobody/AIAgents
    """)


if __name__ == "__main__":
    # Check for required API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  WARNING: ANTHROPIC_API_KEY not set!")
        print("The agents will use default LLM which may not work as well.")
        print("To use Claude Sonnet 4.5, set: export ANTHROPIC_API_KEY='your-key'\n")

    if not os.getenv("SERPER_API_KEY"):
        print("ℹ️  Info: SERPER_API_KEY not set - web search will be disabled")
        print("This is optional for the demo.\n")

    main()
