from versatileBusinessSearch import VersatileBusinessSearch, save_results
import sys

# Get query from command line or use default
if len(sys.argv) > 1:
    query = ' '.join(sys.argv[1:])
else:
    # Default to problem-solving demo
    query = "Find restaurant staffing solutions in Peoria"

print(f"\n🔍 Running Business Intelligence Search")
print(f"Query: {query}")
print("="*60)

# Create searcher and analyze query
searcher = VersatileBusinessSearch()
analysis = searcher.analyze_query(query)

print(f"\n✅ Query Analysis:")
print(f"   - Type: {analysis['query_type']}")
print(f"   - Industry: {analysis['industry']}")
print(f"   - Location: {analysis['location'] or 'Not specified'}")
print(f"\n🚀 Executing search (this may take 30-60 seconds)...\n")

# Run search
try:
    raw_output, markdown_report = searcher.search(query)
    
    # Save results
    md_file, raw_file = save_results(query, raw_output, markdown_report)
    
    print(f"\n✅ Search Complete!")
    print(f"   - Markdown report: {md_file}")
    print(f"   - Raw output: {raw_file}")
    
    # Show the markdown report
    print("\n" + "="*60)
    print("📄 GENERATED REPORT")
    print("="*60)
    print(markdown_report)
    
except Exception as e:
    print(f"\n❌ Error during search: {e}")
    import traceback
    traceback.print_exc()