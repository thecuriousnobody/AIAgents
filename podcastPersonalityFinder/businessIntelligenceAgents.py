from crewai import Agent, Task, Crew, Process
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import serper_search_tool
from usefulTools.llm_repository import ClaudeSonnet

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY


def create_agricultural_consultant_agents():
    """Create agents for finding regenerative agriculture experts and soil health consultants"""
    
    # Agent 1: Market Analyzer - understands the agricultural landscape
    market_analyzer = Agent(
        role="Agricultural Market Analyst",
        goal="Analyze the regenerative agriculture and soil health consulting market in Illinois, identifying key trends, certifications, and specializations",
        backstory="You are an expert in agricultural markets with deep knowledge of regenerative farming practices, soil science, and the Illinois agricultural ecosystem. You understand what farmers need and what makes consultants valuable.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )
    
    # Agent 2: Expert Finder - finds the actual consultants
    expert_finder = Agent(
        role="Agricultural Consultant Researcher",
        goal="Find regenerative agriculture experts and soil health consultants specifically serving Illinois farmers",
        backstory="You specialize in finding agricultural professionals across various channels - from university extensions to private consultants, from well-known experts to emerging practitioners making real impact.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )
    
    # Agent 3: Credential Verifier - validates expertise and gathers details
    credential_verifier = Agent(
        role="Agricultural Credential Specialist",
        goal="Verify credentials, certifications, and track records of identified consultants, gathering detailed information about their expertise and client results",
        backstory="You are meticulous about verifying agricultural credentials, understanding certifications like CCA, CPSS, and regenerative agriculture certifications. You dig deep to find real results and case studies.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )
    
    # Agent 4: Contact Strategist - finds contact info and outreach strategies
    contact_strategist = Agent(
        role="Agricultural Business Development Specialist",
        goal="Find contact information and develop personalized outreach strategies for connecting with each consultant",
        backstory="You understand how agricultural consultants prefer to be contacted, the seasonal nature of farming, and how to craft messages that resonate with agricultural professionals.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )
    
    return [market_analyzer, expert_finder, credential_verifier, contact_strategist]


def create_agricultural_tasks(location="Illinois"):
    """Create tasks for the agricultural consultant search"""
    
    analyze_market_task = Task(
        description=f"""Analyze the regenerative agriculture and soil health consulting market in {location}. 
        Identify:
        1. Key regenerative agriculture practices being adopted
        2. Major soil health challenges in the region
        3. Types of consultants farmers are seeking (soil testing, cover crops, carbon credits, etc.)
        4. Important certifications and qualifications
        5. Typical consultant fee structures and ROI expectations""",
        expected_output="A comprehensive market analysis including trends, challenges, consultant types, and key qualifications to look for"
    )
    
    find_consultants_task = Task(
        description=f"""Find regenerative agriculture experts and soil health consultants serving {location} farmers.
        Include:
        1. University extension specialists
        2. Private consultants and consulting firms
        3. Non-profit organization experts
        4. Regenerative agriculture practitioners who also consult
        5. Soil testing lab consultants
        
        For each consultant provide:
        - Name and organization
        - Specialization areas
        - Geographic coverage
        - Years of experience
        - Notable projects or clients""",
        expected_output="A list of 15-20 consultants across different categories with basic information about each"
    )
    
    verify_credentials_task = Task(
        description="""For each identified consultant, research and verify:
        1. Educational background and degrees
        2. Professional certifications (CCA, CPSS, etc.)
        3. Published research or articles
        4. Speaking engagements or workshops
        5. Client testimonials or case studies
        6. Measurable results (yield improvements, soil health metrics, cost savings)
        7. Awards or recognition
        8. Professional affiliations""",
        expected_output="Detailed credential profiles for each consultant including verified qualifications and documented results"
    )
    
    develop_outreach_task = Task(
        description="""For each consultant, provide:
        1. Direct contact information (email, phone, LinkedIn)
        2. Best method and timing for contact
        3. Personalized outreach template mentioning:
           - Specific aspect of their work that's relevant
           - Clear value proposition for the farmer
           - Appropriate technical language level
        4. Follow-up strategy
        5. Red flags or things to avoid when contacting""",
        expected_output="Complete outreach packages for each consultant with contact info, templates, and strategic guidance"
    )
    
    return [analyze_market_task, find_consultants_task, verify_credentials_task, develop_outreach_task]


def create_restaurant_staffing_agents():
    """Create agents for finding restaurant staff retention consultants and staffing solutions"""
    
    # Agent 1: Industry Analyst - understands restaurant staffing challenges
    industry_analyst = Agent(
        role="Restaurant Industry Analyst",
        goal="Analyze the restaurant staffing crisis, retention challenges, and emerging solutions in the market",
        backstory="You are an expert in restaurant operations with deep understanding of why turnover exceeds 100% annually, the true costs of staffing issues, and what solutions actually work.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )
    
    # Agent 2: Solution Finder - finds consultants and platforms
    solution_finder = Agent(
        role="Restaurant Staffing Solution Researcher",
        goal="Find staff retention consultants, on-demand staffing platforms, and innovative staffing solutions for restaurants",
        backstory="You know every player in the restaurant staffing space - from traditional recruiters to AI-powered platforms, from retention specialists to gig economy solutions.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )
    
    # Agent 3: Success Validator - finds real results and case studies
    success_validator = Agent(
        role="Restaurant Success Story Specialist",
        goal="Find and validate real success stories, case studies, and ROI data for each staffing solution",
        backstory="You dig deep to find actual results - not just marketing claims. You understand restaurant metrics and can identify genuine success stories versus fluff.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )
    
    # Agent 4: Implementation Strategist - provides practical guidance
    implementation_strategist = Agent(
        role="Restaurant Operations Strategist",
        goal="Develop implementation strategies and contact approaches for each staffing solution",
        backstory="You understand restaurant operations intimately - the daily chaos, budget constraints, and why solutions fail. You know how to present solutions that restaurant owners will actually implement.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )
    
    return [industry_analyst, solution_finder, success_validator, implementation_strategist]


def create_restaurant_tasks(location=""):
    """Create tasks for the restaurant staffing solution search"""
    
    analyze_industry_task = Task(
        description=f"""Analyze the restaurant staffing crisis {f'in {location}' if location else ''}. 
        Research:
        1. Current turnover rates and root causes
        2. True cost of turnover (hiring, training, lost productivity)
        3. Emerging retention strategies that work
        4. Technology solutions making an impact
        5. Gig economy and on-demand staffing trends
        6. Budget ranges restaurants allocate for staffing solutions""",
        expected_output="A comprehensive analysis of staffing challenges and solution categories with cost-benefit insights"
    )
    
    find_solutions_task = Task(
        description=f"""Find restaurant staffing consultants and solutions {f'serving {location}' if location else ''}.
        Include:
        1. Staff retention consultants and HR specialists
        2. Restaurant-specific recruiting firms
        3. On-demand staffing platforms (Qwick, Instawork, etc.)
        4. Employee engagement and culture consultants
        5. Training and development specialists
        6. Compensation and benefits consultants
        
        For each provide:
        - Company/consultant name
        - Specialization and approach
        - Target restaurant types (QSR, casual, fine dining)
        - Pricing model
        - Geographic coverage""",
        expected_output="A categorized list of 15-20 staffing solutions with detailed descriptions of each"
    )
    
    validate_success_task = Task(
        description="""For each identified solution, find and validate:
        1. Specific client success stories with metrics
        2. Reduction in turnover rates achieved
        3. ROI calculations and payback periods
        4. Client testimonials from similar restaurants
        5. Any failed implementations and lessons learned
        6. Time to see results
        7. Integration with existing operations
        8. Hidden costs or challenges""",
        expected_output="Validated success metrics and case studies for each solution with honest assessment of results"
    )
    
    create_implementation_task = Task(
        description="""For each solution, provide:
        1. Direct contact information and best person to reach
        2. Customized outreach templates that:
           - Acknowledge specific restaurant pain points
           - Reference relevant success stories
           - Include clear next steps
        3. Questions to ask during evaluation
        4. Red flags to watch for
        5. Implementation timeline and resource requirements
        6. Tips for getting buy-in from existing staff""",
        expected_output="Complete implementation guides for each solution with templates, timelines, and practical tips"
    )
    
    return [analyze_industry_task, find_solutions_task, validate_success_task, create_implementation_task]


def run_agricultural_consultant_search(location="Illinois"):
    """Run the agricultural consultant search"""
    agents = create_agricultural_consultant_agents()
    tasks = create_agricultural_tasks(location)
    
    # Assign agents to tasks
    tasks[0].agent = agents[0]  # market_analyzer
    tasks[1].agent = agents[1]  # expert_finder
    tasks[2].agent = agents[2]  # credential_verifier
    tasks[3].agent = agents[3]  # contact_strategist
    
    # Set task dependencies
    tasks[1].context = [tasks[0]]
    tasks[2].context = [tasks[1]]
    tasks[3].context = [tasks[1], tasks[2]]
    
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()


def run_restaurant_staffing_search(location=""):
    """Run the restaurant staffing solution search"""
    agents = create_restaurant_staffing_agents()
    tasks = create_restaurant_tasks(location)
    
    # Assign agents to tasks
    tasks[0].agent = agents[0]  # industry_analyst
    tasks[1].agent = agents[1]  # solution_finder
    tasks[2].agent = agents[2]  # success_validator
    tasks[3].agent = agents[3]  # implementation_strategist
    
    # Set task dependencies
    tasks[1].context = [tasks[0]]
    tasks[2].context = [tasks[1]]
    tasks[3].context = [tasks[1], tasks[2]]
    
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()


if __name__ == '__main__':
    print("Business Intelligence Agent System")
    print("1. Find regenerative agriculture experts in Illinois")
    print("2. Find restaurant staffing solutions")
    
    choice = input("\nSelect option (1 or 2): ")
    
    if choice == "1":
        location = input("Enter location (default: Illinois): ") or "Illinois"
        result = run_agricultural_consultant_search(location)
        
        # Save results
        directory = "/Users/rajeevkumar/Documents/GIT_Repos/AIAgents/podcastPersonalityFinder/results"
        os.makedirs(directory, exist_ok=True)
        file_name = f"agricultural_consultants_{location.replace(' ', '_')}.txt"
        
    elif choice == "2":
        location = input("Enter location (optional): ")
        result = run_restaurant_staffing_search(location)
        
        # Save results
        directory = "/Users/rajeevkumar/Documents/GIT_Repos/AIAgents/podcastPersonalityFinder/results"
        os.makedirs(directory, exist_ok=True)
        file_name = f"restaurant_staffing_solutions{'_' + location.replace(' ', '_') if location else ''}.txt"
    
    else:
        print("Invalid choice")
        exit()
    
    print("\n" + "="*50)
    print("SEARCH RESULTS:")
    print("="*50)
    print(result)
    
    # Write results to file
    full_path = os.path.join(directory, file_name)
    try:
        with open(full_path, "w") as file:
            file.write(str(result))
        print(f"\nResults saved to {file_name}")
    except Exception as e:
        print(f"Error saving results: {e}")