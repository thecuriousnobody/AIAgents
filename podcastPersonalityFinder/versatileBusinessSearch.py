from crewai import Agent, Task, Crew, Process
import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Tuple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import serper_search_tool
from usefulTools.llm_repository import ClaudeSonnet

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY


class VersatileBusinessSearch:
    """A versatile business intelligence search system that adapts to different query types"""
    
    def __init__(self):
        self.query_type = None
        self.industry = None
        self.location = None
        self.specific_need = None
        
    def analyze_query(self, query: str) -> Dict[str, str]:
        """Analyze the query to determine type, industry, location, and specific need"""
        query_lower = query.lower()
        
        # Determine query type
        if any(word in query_lower for word in ['find', 'help me', 'solutions', 'consultants', 'services']):
            self.query_type = 'problem_solving'
        elif any(word in query_lower for word in ['trends', 'emerging', 'latest', 'innovations', 'technologies']):
            self.query_type = 'trend_analysis'
        elif any(word in query_lower for word in ['suppliers', 'vendors', 'sources', 'dealers', 'providers']):
            self.query_type = 'resource_finding'
        elif any(word in query_lower for word in ['compliance', 'regulations', 'legal', 'certification']):
            self.query_type = 'compliance'
        else:
            self.query_type = 'general'
            
        # Determine industry
        if any(word in query_lower for word in ['restaurant', 'food service', 'dining', 'chef', 'kitchen']):
            self.industry = 'restaurant'
        elif any(word in query_lower for word in ['farm', 'agriculture', 'crop', 'soil', 'organic', 'seed']):
            self.industry = 'agriculture'
        else:
            self.industry = 'general'
            
        # Extract location
        location_patterns = [
            r'in (\w+(?:\s+\w+)*?)(?:\s|$)',
            r'near (\w+(?:\s+\w+)*?)(?:\s|$)',
            r'around (\w+(?:\s+\w+)*?)(?:\s|$)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                self.location = match.group(1)
                break
        
        # Extract specific need
        self.specific_need = query
        
        return {
            'query_type': self.query_type,
            'industry': self.industry,
            'location': self.location,
            'specific_need': self.specific_need
        }
    
    def create_problem_solving_agents(self) -> List[Agent]:
        """Create agents for problem-solving queries"""
        problem_analyzer = Agent(
            role=f"{self.industry.title()} Problem Analyst",
            goal=f"Deeply understand the specific problem and its impact on {self.industry} businesses",
            backstory=f"You are an expert in {self.industry} operations who understands the real pain points and their cascading effects on business success.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet
        )
        
        solution_finder = Agent(
            role=f"{self.industry.title()} Solution Researcher",
            goal=f"Find proven solutions, consultants, and services that address the specific problem",
            backstory=f"You know every solution provider in the {self.industry} space and can identify which ones actually deliver results.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[serper_search_tool]
        )
        
        roi_validator = Agent(
            role="ROI and Success Validator",
            goal="Find concrete evidence of success, ROI metrics, and implementation timelines",
            backstory="You dig deep to find real results and can distinguish between marketing claims and actual business impact.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[serper_search_tool]
        )
        
        implementation_strategist = Agent(
            role="Implementation Strategist",
            goal="Create actionable implementation plans with contacts, templates, and timelines",
            backstory=f"You understand how {self.industry} businesses actually work and can create realistic implementation strategies.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[serper_search_tool]
        )
        
        return [problem_analyzer, solution_finder, roi_validator, implementation_strategist]
    
    def create_trend_analysis_agents(self) -> List[Agent]:
        """Create agents for trend analysis queries"""
        trend_researcher = Agent(
            role=f"{self.industry.title()} Trend Researcher",
            goal=f"Identify emerging trends, technologies, and innovations in the {self.industry} sector",
            backstory=f"You track every innovation and trend in the {self.industry} space, from early adopters to mainstream movements.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[serper_search_tool]
        )
        
        impact_analyst = Agent(
            role="Business Impact Analyst",
            goal="Analyze how trends affect business operations, costs, and competitive advantage",
            backstory="You understand the practical implications of trends and can predict their business impact.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[serper_search_tool]
        )
        
        adoption_strategist = Agent(
            role="Adoption Strategy Expert",
            goal="Create strategies for adopting trends with timelines, costs, and implementation steps",
            backstory=f"You help {self.industry} businesses successfully adopt new trends without disrupting operations.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet
        )
        
        return [trend_researcher, impact_analyst, adoption_strategist]
    
    def create_resource_finding_agents(self) -> List[Agent]:
        """Create agents for resource/supplier finding queries"""
        resource_locator = Agent(
            role=f"{self.industry.title()} Resource Specialist",
            goal=f"Find suppliers, vendors, and service providers for {self.industry} businesses",
            backstory=f"You have comprehensive knowledge of {self.industry} suppliers and can match businesses with the right providers.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[serper_search_tool]
        )
        
        vendor_evaluator = Agent(
            role="Vendor Evaluation Expert",
            goal="Evaluate vendors on quality, pricing, reliability, and customer satisfaction",
            backstory="You can assess vendor capabilities and identify the best options for specific business needs.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[serper_search_tool]
        )
        
        return [resource_locator, vendor_evaluator]
    
    def create_tasks_for_query_type(self, agents: List[Agent]) -> List[Task]:
        """Create tasks based on query type"""
        tasks = []
        
        if self.query_type == 'problem_solving':
            tasks.append(Task(
                description=f"Analyze the problem: '{self.specific_need}'. Understand root causes, business impact, and urgency.",
                agent=agents[0],
                expected_output="Comprehensive problem analysis with business impact assessment"
            ))
            
            tasks.append(Task(
                description=f"Find solutions for: '{self.specific_need}' {f'in {self.location}' if self.location else ''}. Include consultants, services, and technology solutions.",
                agent=agents[1],
                expected_output="List of 10-15 solutions with descriptions and capabilities",
                context=[tasks[0]]
            ))
            
            tasks.append(Task(
                description="For each solution, find ROI metrics, case studies, implementation timelines, and real client results.",
                agent=agents[2],
                expected_output="Validated success metrics and evidence for each solution",
                context=[tasks[1]]
            ))
            
            tasks.append(Task(
                description="Create implementation plans with contact info, outreach templates, evaluation questions, and action steps.",
                agent=agents[3],
                expected_output="Complete implementation guide with templates and timelines",
                context=[tasks[1], tasks[2]]
            ))
            
        elif self.query_type == 'trend_analysis':
            tasks.append(Task(
                description=f"Research: '{self.specific_need}' in the {self.industry} industry. Identify key trends, adoption rates, and innovations.",
                agent=agents[0],
                expected_output="Comprehensive trend analysis with examples and statistics"
            ))
            
            tasks.append(Task(
                description="Analyze business impact of identified trends including costs, benefits, risks, and competitive advantages.",
                agent=agents[1],
                expected_output="Impact analysis with ROI projections and risk assessment",
                context=[tasks[0]]
            ))
            
            tasks.append(Task(
                description="Create adoption strategies including implementation steps, required resources, and success metrics.",
                agent=agents[2],
                expected_output="Practical adoption roadmap with timelines and resource requirements",
                context=[tasks[0], tasks[1]]
            ))
            
        elif self.query_type == 'resource_finding':
            tasks.append(Task(
                description=f"Find: '{self.specific_need}' {f'in {self.location}' if self.location else ''}. Include all relevant suppliers and vendors.",
                agent=agents[0],
                expected_output="Comprehensive list of suppliers with contact information and offerings"
            ))
            
            tasks.append(Task(
                description="Evaluate each supplier on quality, pricing, reliability, customer reviews, and unique advantages.",
                agent=agents[1],
                expected_output="Detailed vendor comparison with pros, cons, and recommendations",
                context=[tasks[0]]
            ))
            
        return tasks
    
    def generate_markdown_report(self, query: str, analysis: Dict, crew_output: str) -> str:
        """Generate a professional markdown report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown = f"""# Business Intelligence Report

**Generated:** {timestamp}  
**Query:** {query}  
**Type:** {analysis['query_type'].replace('_', ' ').title()}  
**Industry:** {analysis['industry'].title()}  
{'**Location:** ' + analysis['location'] if analysis['location'] else ''}

---

## Executive Summary

{self._extract_summary(crew_output)}

---

## Detailed Findings

{crew_output}

---

## Key Takeaways

{self._extract_takeaways(crew_output)}

---

## Next Steps

1. Review the findings and identify top 3 solutions/opportunities
2. Use provided contact information to reach out
3. Implement evaluation criteria before making decisions
4. Track results against projected ROI/benefits

---

*Report generated by Versatile Business Intelligence Search System*
"""
        return markdown
    
    def _extract_summary(self, output: str) -> str:
        """Extract a summary from the crew output"""
        lines = output.split('\n')
        summary_lines = []
        for i, line in enumerate(lines[:10]):  # Look at first 10 lines
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
            if len(summary_lines) >= 3:
                break
        return '\n'.join(summary_lines) if summary_lines else "Analysis complete. See detailed findings below."
    
    def _extract_takeaways(self, output: str) -> str:
        """Extract key takeaways"""
        takeaways = []
        lines = output.split('\n')
        
        # Look for numbered lists or bullet points
        for line in lines:
            if re.match(r'^\d+\.', line.strip()) or line.strip().startswith('•') or line.strip().startswith('-'):
                if any(word in line.lower() for word in ['recommend', 'suggest', 'consider', 'important']):
                    takeaways.append(line.strip())
        
        if not takeaways:
            takeaways = [
                "• Multiple solutions identified with proven track records",
                "• Implementation strategies provided for each option",
                "• Contact information and outreach templates included"
            ]
            
        return '\n'.join(takeaways[:5])  # Limit to 5 takeaways
    
    def search(self, query: str) -> Tuple[str, str]:
        """Main search method that returns both raw output and markdown report"""
        # Analyze query
        analysis = self.analyze_query(query)
        print(f"\nQuery Analysis: {analysis}")
        
        # Create appropriate agents
        if analysis['query_type'] == 'problem_solving':
            agents = self.create_problem_solving_agents()
        elif analysis['query_type'] == 'trend_analysis':
            agents = self.create_trend_analysis_agents()
        else:  # resource_finding or general
            agents = self.create_resource_finding_agents()
        
        # Create tasks
        tasks = self.create_tasks_for_query_type(agents)
        
        # Create and run crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        
        print(f"\nExecuting {analysis['query_type']} search...")
        crew_output = crew.kickoff()
        
        # Generate markdown report
        markdown_report = self.generate_markdown_report(query, analysis, str(crew_output))
        
        return str(crew_output), markdown_report


def save_results(query: str, raw_output: str, markdown_report: str):
    """Save both raw output and markdown report"""
    # Create results directory
    directory = "/Users/rajeevkumar/Documents/GIT_Repos/AIAgents/podcastPersonalityFinder/results"
    os.makedirs(directory, exist_ok=True)
    
    # Create safe filename
    safe_query = re.sub(r'[^\w\s-]', '', query)[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw output
    raw_filename = f"raw_{safe_query.replace(' ', '_')}_{timestamp}.txt"
    raw_path = os.path.join(directory, raw_filename)
    with open(raw_path, "w") as f:
        f.write(raw_output)
    
    # Save markdown report
    md_filename = f"report_{safe_query.replace(' ', '_')}_{timestamp}.md"
    md_path = os.path.join(directory, md_filename)
    with open(md_path, "w") as f:
        f.write(markdown_report)
    
    return md_filename, raw_filename


if __name__ == '__main__':
    print("\n=== Versatile Business Intelligence Search ===\n")
    print("Example queries:")
    print("1. Find restaurant staffing solutions in Peoria")
    print("2. What are emerging precision agriculture technologies?")
    print("3. Find organic seed suppliers near Peoria")
    print("4. Help me reduce food waste in my restaurant")
    print("5. Latest trends in restaurant automation")
    
    query = input("\nEnter your search query: ")
    
    if query:
        searcher = VersatileBusinessSearch()
        raw_output, markdown_report = searcher.search(query)
        
        print("\n" + "="*50)
        print("SEARCH COMPLETE")
        print("="*50)
        
        # Save results
        md_file, raw_file = save_results(query, raw_output, markdown_report)
        
        print(f"\n✅ Results saved:")
        print(f"   - Markdown report: {md_file}")
        print(f"   - Raw output: {raw_file}")
        
        # Show preview of markdown report
        print("\n📄 Report Preview:")
        print("-"*30)
        print(markdown_report[:500] + "...")
        print("-"*30)
        print("\nFull report saved to results folder!")