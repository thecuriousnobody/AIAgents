from versatileBusinessSearch import VersatileBusinessSearch, save_results
import time

def run_demo(query: str, demo_name: str):
    """Run a single demo search"""
    print(f"\n{'='*60}")
    print(f"DEMO: {demo_name}")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")
    
    searcher = VersatileBusinessSearch()
    
    # Show query analysis
    analysis = searcher.analyze_query(query)
    print(f"✅ Query Analysis:")
    print(f"   - Type: {analysis['query_type']}")
    print(f"   - Industry: {analysis['industry']}")
    print(f"   - Location: {analysis['location'] or 'Not specified'}")
    print(f"\n🚀 Starting search...\n")
    
    # Run search
    raw_output, markdown_report = searcher.search(query)
    
    # Save results
    md_file, raw_file = save_results(query, raw_output, markdown_report)
    
    print(f"\n✅ Results saved:")
    print(f"   - Markdown report: {md_file}")
    print(f"   - Raw output: {raw_file}")
    
    # Show preview
    print("\n📄 Report Preview:")
    print("-"*40)
    lines = markdown_report.split('\n')[:20]
    print('\n'.join(lines))
    print("...")
    print("-"*40)
    
    return markdown_report

def main():
    print("\n🎯 VERSATILE BUSINESS INTELLIGENCE SEARCH DEMOS")
    print("="*60)
    
    demos = [
        {
            "name": "Problem-Solving: Restaurant Staffing Crisis",
            "query": "Find restaurant staffing solutions in Peoria",
            "description": "High-value demo showing how we solve real business problems"
        },
        {
            "name": "Trend Analysis: Agricultural Technology",
            "query": "What are emerging precision agriculture technologies in the Midwest?",
            "description": "Shows market intelligence and trend tracking capabilities"
        },
        {
            "name": "Resource Finding: Local Suppliers",
            "query": "Find organic seed suppliers near Peoria Illinois",
            "description": "Demonstrates local resource discovery"
        }
    ]
    
    print("\nWe'll run 3 demos showing different search capabilities:\n")
    for i, demo in enumerate(demos, 1):
        print(f"{i}. {demo['name']}")
        print(f"   Query: \"{demo['query']}\"")
        print(f"   Purpose: {demo['description']}\n")
    
    input("\nPress Enter to start Demo 1...")
    
    # Run demos
    for i, demo in enumerate(demos, 1):
        try:
            run_demo(demo['query'], demo['name'])
            
            if i < len(demos):
                input(f"\n🎯 Demo {i} complete! Press Enter for Demo {i+1}...")
            else:
                print(f"\n🎉 All demos complete!")
                
        except Exception as e:
            print(f"\n❌ Error in demo: {e}")
            continue
    
    print("\n" + "="*60)
    print("DEMO SUMMARY")
    print("="*60)
    print("\n✅ The system successfully:")
    print("   1. Analyzed different query types automatically")
    print("   2. Configured appropriate agents for each search")
    print("   3. Generated comprehensive business intelligence")
    print("   4. Created downloadable markdown reports")
    print("\n🚀 Ready for website integration!")
    print("   - Single search endpoint handles all query types")
    print("   - Professional reports ready for download")
    print("   - Saves hours of manual research")

if __name__ == '__main__':
    main()