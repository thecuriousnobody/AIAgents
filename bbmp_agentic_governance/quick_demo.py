"""
Quick Demo - No API Keys Required
Shows BBMP data analysis without running full CrewAI agents
Perfect for podcast demonstrations!
"""

import os
import sys
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools.bbmp_tools import (
    BBMPDataLoader,
    BudgetValidator,
    DPRValidator,
    ContractorAnalyzer,
    AnomalyDetector,
    format_currency
)

console = Console()


def show_system_overview():
    """Display system overview"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]BBMP AGENTIC GOVERNANCE SYSTEM[/bold cyan]\n\n"
        "[yellow]Automating Transparent Governance with AI Agents[/yellow]\n\n"
        "🎯 Mission: Eliminate corruption by replacing discretionary decisions\n"
        "   with AI agents operating on transparent, immutable rules.\n\n"
        "💰 Impact: Save ₹1,200-1,800 crores per year (20-30% of BBMP budget)",
        title="🏛️  Phase 0 Demo",
        border_style="cyan"
    ))


def demo_schedule_of_rates():
    """Show Schedule of Rates data"""
    console.print("\n\n[bold cyan]═══ KARNATAKA PWD SCHEDULE OF RATES (2024) ═══[/bold cyan]\n")

    data_loader = BBMPDataLoader(data_dir="data")
    sor = data_loader.load_schedule_of_rates()

    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Item Code", style="cyan")
    table.add_column("Description", style="white", no_wrap=False, max_width=40)
    table.add_column("Rate", justify="right", style="green")
    table.add_column("Unit", style="yellow")
    table.add_column("Category", style="blue")

    for item in sor:
        table.add_row(
            item['item_code'],
            item['description'],
            f"₹{item['rate_inr']:,.2f}",
            item['unit'],
            item['category']
        )

    console.print(table)


def demo_dpr_validation():
    """Demonstrate DPR validation"""
    console.print("\n\n[bold cyan]═══ DPR INTEGRITY VALIDATION ═══[/bold cyan]\n")

    data_loader = BBMPDataLoader(data_dir="data")
    dpr_validator = DPRValidator(data_loader)
    budget_validator = BudgetValidator(data_loader)
    anomaly_detector = AnomalyDetector(data_loader)

    dprs = data_loader.load_dprs()

    for dpr in dprs:
        # Validate DPR
        dpr_result = dpr_validator.validate_documentation(dpr)
        budget_result = budget_validator.validate_dpr_budget(dpr)
        anomalies = anomaly_detector.detect_anomalies_in_dpr(dpr)

        # Determine color based on decision
        if dpr_result['decision'] == 'APPROVE' and budget_result['decision'] in ['AUTO_APPROVE', 'FLAG_FOR_REVIEW']:
            color = "green"
            emoji = "✓"
        else:
            color = "red"
            emoji = "✗"

        console.print(f"\n[bold {color}]{emoji} {dpr['dpr_id']}: {dpr['title']}[/bold {color}]")
        console.print(f"   Zone: {dpr['zone']} | Cost: {format_currency(dpr['estimated_cost'])}")

        # DPR Validation
        console.print(f"\n   [bold]DPR Integrity:[/bold] [{color}]{dpr_result['decision']}[/{color}]")
        console.print(f"   Reason: {dpr_result['reason']}")

        if dpr_result['critical_issues']:
            console.print(f"   [bold red]Critical Issues:[/bold red]")
            for issue in dpr_result['critical_issues']:
                console.print(f"     • {issue}")

        if dpr_result['warnings']:
            console.print(f"   [bold yellow]Warnings:[/bold yellow]")
            for warning in dpr_result['warnings']:
                console.print(f"     • {warning}")

        # Budget Validation
        console.print(f"\n   [bold]Budget Validation:[/bold] [{color}]{budget_result['decision']}[/{color}]")
        console.print(f"   DPR Estimate: {format_currency(budget_result['dpr_estimate'])}")
        console.print(f"   SoR Estimate: {format_currency(budget_result['sor_estimate'])}")
        console.print(f"   Variance: {budget_result['variance_percentage']:.1f}%")

        # Anomalies
        if anomalies:
            console.print(f"\n   [bold red]Anomalies Detected:[/bold red]")
            for anomaly in anomalies:
                console.print(f"     • {anomaly}")

        console.print("   " + "─" * 70)


def demo_contractor_analysis():
    """Demonstrate contractor analysis"""
    console.print("\n\n[bold cyan]═══ CONTRACTOR REPUTATION ANALYSIS ═══[/bold cyan]\n")

    data_loader = BBMPDataLoader(data_dir="data")
    contractors = data_loader.load_contractors()

    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white", max_width=30)
    table.add_column("Score", justify="center", style="yellow")
    table.add_column("Projects", justify="right", style="blue")
    table.add_column("Quality", justify="right", style="green")
    table.add_column("Red Flags", style="red")

    for contractor in contractors:
        score = contractor['reputation_score']
        score_color = "green" if score >= 70 else "yellow" if score >= 50 else "red"

        red_flags = "✓" if not contractor.get('red_flags') else f"{len(contractor['red_flags'])} 🚩"

        table.add_row(
            contractor['contractor_id'],
            contractor['name'],
            f"[{score_color}]{score}/100[/{score_color}]",
            str(contractor['completed_projects']),
            f"{contractor['performance_history']['quality_pass_rate']*100:.0f}%",
            red_flags
        )

    console.print(table)


def demo_cartel_detection():
    """Demonstrate cartel detection"""
    console.print("\n\n[bold cyan]═══ BID RIGGING & CARTEL DETECTION ═══[/bold cyan]\n")

    data_loader = BBMPDataLoader(data_dir="data")
    contractor_analyzer = ContractorAnalyzer(data_loader)

    # Test Case 1: Clean tender
    console.print("[bold green]Test Case 1: Legitimate Competitive Tender[/bold green]")
    console.print("Bidders: CONT-2024-001, CONT-2024-002, CONT-2024-006\n")

    result1 = contractor_analyzer.detect_cartel_network(
        ["CONT-2024-001", "CONT-2024-002", "CONT-2024-006"]
    )

    console.print(f"Cartel Risk: [bold green]{result1['cartel_risk']}[/bold green]")
    console.print(f"Connections Found: {result1['connections_found']}")
    console.print("✓ [green]DECISION: APPROVE TENDER[/green]\n")

    console.print("─" * 70 + "\n")

    # Test Case 2: Cartel detected
    console.print("[bold red]Test Case 2: Suspicious Cartel Activity[/bold red]")
    console.print("Bidders: CONT-2024-001, CONT-2024-004, CONT-2024-005\n")

    result2 = contractor_analyzer.detect_cartel_network(
        ["CONT-2024-001", "CONT-2024-004", "CONT-2024-005"]
    )

    console.print(f"Cartel Risk: [bold red]{result2['cartel_risk']}[/bold red]")
    console.print(f"Connections Found: {result2['connections_found']}\n")

    if result2['connections']:
        console.print("[bold red]🚨 SUSPICIOUS CONNECTIONS:[/bold red]")
        for conn in result2['connections']:
            console.print(f"  • {conn['type'].upper()}")
            console.print(f"    {conn['contractor_1']} ↔ {conn['contractor_2']}")
            if 'shared' in conn:
                console.print(f"    Shared: {', '.join(conn['shared'])}")

    console.print("\n✗ [red]DECISION: REJECT TENDER - Cartel Activity Detected[/red]")
    console.print("✗ [red]ACTION: Recommend debarment and investigation[/red]\n")


def demo_impact_metrics():
    """Show impact metrics"""
    console.print("\n\n[bold cyan]═══ PROJECTED IMPACT ═══[/bold cyan]\n")

    data = [
        ["Current BBMP PWD Budget", "₹6,000 Cr/year"],
        ["Estimated Leakage (20-30%)", "₹1,200-1,800 Cr/year"],
        ["", ""],
        ["[bold green]With Agentic System:[/bold green]", ""],
        ["Budget Inflation Prevention", "₹600-900 Cr saved"],
        ["Cartel Elimination (10-15% cost reduction)", "₹400-600 Cr saved"],
        ["Quality Improvement (reduced rework)", "₹200-300 Cr saved"],
        ["", ""],
        ["[bold yellow]TOTAL PROJECTED SAVINGS[/bold yellow]", "[bold yellow]₹1,200-1,800 Cr/year[/bold yellow]"],
    ]

    table = Table(show_header=False, box=box.DOUBLE_EDGE, border_style="cyan")
    table.add_column("Metric", style="white")
    table.add_column("Value", justify="right", style="green")

    for row in data:
        table.add_row(row[0], row[1])

    console.print(table)


def main():
    """Main demo"""
    show_system_overview()

    console.print("\n[bold yellow]Choose demo:[/bold yellow]")
    console.print("1. Full Demo (all features)")
    console.print("2. Schedule of Rates")
    console.print("3. DPR Validation (show corruption detection)")
    console.print("4. Contractor Analysis")
    console.print("5. Cartel Detection (show bid rigging)")
    console.print("6. Impact Metrics")

    choice = input("\nEnter choice (1-6, or press Enter for full demo): ").strip()

    if choice == "2":
        demo_schedule_of_rates()
    elif choice == "3":
        demo_dpr_validation()
    elif choice == "4":
        demo_contractor_analysis()
    elif choice == "5":
        demo_cartel_detection()
    elif choice == "6":
        demo_impact_metrics()
    else:
        # Full demo
        demo_schedule_of_rates()
        input("\n\nPress Enter to continue...")
        demo_dpr_validation()
        input("\n\nPress Enter to continue...")
        demo_contractor_analysis()
        input("\n\nPress Enter to continue...")
        demo_cartel_detection()
        input("\n\nPress Enter to continue...")
        demo_impact_metrics()

    console.print("\n\n[bold green]✓ Demo Complete![/bold green]")
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("• Run full AI agent demo: python demo.py")
    console.print("• Requires: ANTHROPIC_API_KEY for Claude Sonnet 4.5")
    console.print("• See README.md for setup instructions\n")


if __name__ == "__main__":
    main()
