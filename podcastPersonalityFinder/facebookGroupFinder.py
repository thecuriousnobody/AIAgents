from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import re
from datetime import datetime
from langchain.tools import Tool
from usefulTools.llm_repository import ClaudeSonnet
from usefulTools.search_tools import facebook_serper_tool, facebook_group_search_tool, us_serper_tool, uk_serper_tool, canada_serper_tool, australia_serper_tool

# Set up environment variables
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

def get_user_search_focus():
    """
    Interactive function to get the user's specific search focus for Facebook groups.
    Makes the tool extensible for any product/service/topic.
    """
    print("=" * 80)
    print("FACEBOOK GROUP FINDER - INTERACTIVE CONFIGURATION")
    print("=" * 80)
    print()
    
    print("This tool will help you find Facebook groups relevant to your product/service.")
    print("Please provide the following information:")
    print()
    
    # Get product/service details
    product_name = input("1. What is your product/service name? (e.g., podcastbots.ai): ").strip()
    
    print()
    product_description = input("2. Briefly describe what your product/service does: ").strip()
    
    print()
    print("3. What type of Facebook groups are you looking for? Choose from:")
    print("   a) General communities (broad audience)")
    print("   b) Professional/Business groups")
    print("   c) Niche/specialized communities")
    print("   d) Regional/local groups")
    print("   e) Mixed (combination of above)")
    group_type = input("   Enter your choice (a/b/c/d/e): ").strip().lower()
    
    print()
    target_audience = input("4. Who is your target audience? (e.g., podcasters, content creators, marketers): ").strip()
    
    print()
    value_proposition = input("5. What value does your product provide? (e.g., saves time, improves quality): ").strip()
    
    print()
    print("6. Select search regions (you can choose multiple):")
    print("   1) Global English-speaking communities")
    print("   2) North America (US/Canada)")
    print("   3) Europe (UK/EU)")
    print("   4) Asia-Pacific (Australia/NZ/India)")
    print("   5) All regions")
    region_choice = input("   Enter your choice(s) separated by commas (1,2,3,4 or 5): ").strip()
    
    print()
    num_groups = input("7. How many groups would you like to find per focus area? (default: 15-20): ").strip()
    if not num_groups:
        num_groups = "15-20"
    
    print()
    print("Configuration complete! Starting Facebook group research...")
    print("=" * 80)
    
    return {
        "product_name": product_name,
        "product_description": product_description,
        "group_type": group_type,
        "target_audience": target_audience,
        "value_proposition": value_proposition,
        "region_choice": region_choice,
        "num_groups": num_groups
    }

def generate_research_focuses(config):
    """
    Generate research focuses based on user configuration.
    """
    product_name = config["product_name"]
    product_description = config["product_description"]
    target_audience = config["target_audience"]
    value_proposition = config["value_proposition"]
    num_groups = config["num_groups"]
    
    # Map group type to focus areas
    group_type_mapping = {
        'a': 'General communities and broad audience groups',
        'b': 'Professional and business-focused groups',
        'c': 'Niche and specialized communities',
        'd': 'Regional and local communities',
        'e': 'Mixed communities (general, professional, niche, and regional)'
    }
    
    # Map regions
    region_mapping = {
        '1': 'Global English-speaking communities',
        '2': 'North America (US/Canada)',
        '3': 'Europe (UK/EU)',
        '4': 'Asia-Pacific (Australia/NZ/India)',
        '5': 'All regions globally'
    }
    
    selected_regions = []
    if '5' in config["region_choice"]:
        selected_regions = ['Global English-speaking communities']
    else:
        for region_num in config["region_choice"].split(','):
            region_num = region_num.strip()
            if region_num in region_mapping:
                selected_regions.append(region_mapping[region_num])
    
    group_focus = group_type_mapping.get(config["group_type"], 'Mixed communities')
    
    research_focuses = []
    
    # Generate focus areas based on configuration
    for i, region in enumerate(selected_regions, 1):
        focus = f"""
Research Focus {i}: {group_focus} - {region}
- Product/Service: {product_name}
- Description: {product_description}
- Target: Facebook groups focused on {target_audience} and related communities
- Geographic Scope: {region}
- Audience: {target_audience} who would benefit from {product_description}
- Product Relevance: Groups where members would be interested in tools/services that {value_proposition}
- Business Context: {product_name} - {product_description}
- Value Proposition: {value_proposition}
- Group Count Target: Find approximately {num_groups} relevant groups
- Group Types: Focus on {group_focus.lower()}
"""
        research_focuses.append(focus)
    
    return research_focuses

def save_results_to_file(results, config, filename=None):
    """
    Save all research results to a comprehensive text file.
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_product_name = re.sub(r'[^\w\-_\.]', '_', config["product_name"])
        filename = f"facebook_groups_research_{safe_product_name}_{timestamp}.txt"
    
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        # Write header
        f.write("=" * 100 + "\n")
        f.write("FACEBOOK GROUP RESEARCH RESULTS\n")
        f.write("=" * 100 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Product/Service: {config['product_name']}\n")
        f.write(f"Description: {config['product_description']}\n")
        f.write(f"Target Audience: {config['target_audience']}\n")
        f.write(f"Value Proposition: {config['value_proposition']}\n")
        f.write(f"Search Regions: {config['region_choice']}\n")
        f.write(f"Groups per Focus: {config['num_groups']}\n")
        f.write("=" * 100 + "\n\n")
        
        # Write results for each focus area
        for i, result in enumerate(results, 1):
            f.write(f"\nRESEARCH FOCUS AREA {i}:\n")
            f.write("-" * 50 + "\n")
            f.write(str(result))
            f.write("\n" + "=" * 50 + "\n")
        
        # Write summary
        f.write(f"\n\nSUMMARY:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total Focus Areas Researched: {len(results)}\n")
        f.write(f"Research completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Results saved to: {filename}\n")
        f.write("\nNext Steps:\n")
        f.write("1. Review the group quality scores and recommendations\n")
        f.write("2. Prioritize high-scoring groups for engagement\n")
        f.write("3. Follow the compliance guidelines before posting\n")
        f.write("4. Implement the suggested engagement strategies\n")
        f.write("5. Track engagement metrics and adjust approach as needed\n")
    
    return filepath

# Facebook Group Researcher Agent
facebook_group_researcher = Agent(
    role='Facebook Group Researcher',
    goal='Find active Facebook groups related to podcasting, broadcasting, and content creation',
    backstory="""You are an expert at finding and researching online communities, particularly Facebook groups. 
    Your task is to search for and compile information about Facebook groups where podcasters, broadcasters, 
    and content creators gather. You focus on groups that would be receptive to tools and services that help 
    with podcast production, guest finding, and content enhancement. You prioritize active, engaged communities 
    with clear posting guidelines and professional networking opportunities.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[facebook_serper_tool],
    reasoning=True,
    max_reasoning_attempts=3
)

# Group Quality Analyzer Agent
group_quality_analyzer = Agent(
    role='Group Quality Analyzer',
    goal='Analyze and evaluate the quality and suitability of Facebook groups for promotion',
    backstory="""You are skilled at analyzing online communities to determine their engagement levels, 
    member quality, and suitability for business promotion. You evaluate factors like group activity, 
    member count, posting frequency, admin responsiveness, and community guidelines. You can identify 
    which groups are most likely to be receptive to podcast-related tools and services while avoiding 
    spam-heavy or inactive communities.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[facebook_serper_tool],
    reasoning=True,
    max_reasoning_attempts=3
)

# Engagement Strategy Agent
engagement_strategy_agent = Agent(
    role='Engagement Strategy Specialist',
    goal='Develop appropriate engagement strategies for each Facebook group',
    backstory="""You are an expert in community engagement and social media marketing ethics. 
    Your role is to analyze each Facebook group's culture, rules, and community guidelines to develop 
    appropriate engagement strategies. You understand how to provide value to communities while 
    appropriately introducing relevant tools and services. You focus on building genuine relationships 
    and providing helpful content rather than aggressive promotion.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[facebook_serper_tool],
    reasoning=True,
    max_reasoning_attempts=3
)

# Compliance and Ethics Agent
compliance_ethics_agent = Agent(
    role='Compliance and Ethics Advisor',
    goal='Ensure all group engagement follows platform rules and ethical marketing practices',
    backstory="""You are an expert in Facebook's community standards, group policies, and ethical 
    marketing practices. Your role is to review the identified groups and proposed engagement strategies 
    to ensure compliance with Facebook's terms of service and best practices for community engagement. 
    You provide guidance on how to engage authentically and add value to communities while appropriately 
    sharing relevant tools and services.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[facebook_serper_tool],
    reasoning=True,
    max_reasoning_attempts=3
)

# Define tasks
research_facebook_groups = Task(
    description="""Research and compile a list of Facebook groups related to podcasting, broadcasting, 
    and content creation. Focus on groups that would be interested in podcast production tools, guest finding 
    services, and content enhancement solutions. Look for both general podcasting groups and niche communities 
    (e.g., specific podcast genres, regional podcasting communities, podcast marketing groups).""",
    agent=facebook_group_researcher,
    expected_output="""A structured report containing:
    1. Group Name: [Name of the Facebook group]
    2. Group URL: [Direct link to the group if available]
    3. Member Count: [Approximate number of members]
    4. Group Type: [Public/Private/Closed]
    5. Primary Focus: [Main topic/purpose of the group]
    6. Target Audience: [Who the group serves - podcasters, beginners, professionals, etc.]
    7. Activity Level: [High/Medium/Low based on visible posting frequency]
    8. Group Description: [Brief description of what the group is about]
    9. Admin Information: [Names or details of group administrators if visible]
    10. Recent Post Topics: [Examples of recent discussions/posts]
    11. Relevance Score: [1-10 rating for how relevant this group is to podcastbots.ai]
    12. Sources: [Where you found information about this group]

    Aim to find at least 15-20 groups with a mix of large general groups and smaller niche communities."""
)

analyze_group_quality = Task(
    description="""Analyze the quality and engagement levels of the Facebook groups found by the researcher. 
    Evaluate factors like member engagement, posting frequency, spam levels, admin activity, and overall 
    community health. Prioritize groups that show high engagement and professional discussions.""",
    agent=group_quality_analyzer,
    context=[research_facebook_groups],  # This task depends on the research task
    expected_output="""A quality analysis report for each group including:
    1. Group Name: [Name]
    2. Quality Score: [1-10 overall quality rating]
    3. Engagement Analysis:
       a. Posting Frequency: [Daily/Weekly/Monthly]
       b. Member Interaction: [High/Medium/Low commenting and discussion]
       c. Content Quality: [Professional/Mixed/Low quality posts]
    4. Community Health Indicators:
       a. Spam Level: [None/Low/Medium/High]
       b. Admin Activity: [Active/Moderate/Inactive]
       c. Rule Enforcement: [Strict/Moderate/Lax]
    5. Member Demographics:
       a. Experience Level: [Beginners/Intermediate/Advanced/Mixed]
       b. Geographic Distribution: [Global/Regional/Local]
    6. Promotion Receptivity: [High/Medium/Low likelihood of accepting tool promotions]
    7. Best Posting Times: [When the group is most active]
    8. Recommended Priority: [High/Medium/Low for outreach efforts]

    Provide clear recommendations on which groups to prioritize for engagement."""
)

develop_engagement_strategy = Task(
    description="""Develop specific engagement strategies for each high-priority Facebook group. 
    Create approaches that focus on providing value to the community while appropriately introducing 
    podcastbots.ai as a helpful tool. Consider the group's culture, rules, and member needs.""",
    agent=engagement_strategy_agent,
    context=[research_facebook_groups, analyze_group_quality],  # Depends on both research and quality analysis
    expected_output="""An engagement strategy report for each priority group including:
    1. Group Name: [Name]
    2. Engagement Approach:
       a. Value-First Strategy: [How to provide value before promoting]
       b. Content Types: [Helpful posts, tutorials, tips that would benefit the community]
       c. Introduction Method: [How to naturally introduce podcastbots.ai]
    3. Posting Strategy:
       a. Frequency: [How often to post]
       b. Timing: [Best times to post based on group activity]
       c. Content Mix: [Ratio of helpful content to promotional content]
    4. Community Contribution Ideas:
       a. [Specific ways to help the community]
       b. [Topics or discussions you could start]
       c. [Resources or tips you could share]
    5. Relationship Building:
       a. Key Members to Connect With: [Active, influential members]
       b. Admin Outreach Strategy: [How to introduce yourself to admins]
    6. Success Metrics: [How to measure engagement success]
    7. Timeline: [Suggested timeline for implementation]

    Focus on authentic, value-driven engagement that builds trust and positions podcastbots.ai as a helpful resource."""
)

assess_compliance_ethics = Task(
    description="""Review the identified Facebook groups and proposed engagement strategies to ensure 
    compliance with Facebook's community standards and ethical marketing practices. Provide guidance 
    on staying within platform rules while effectively promoting podcastbots.ai.""",
    agent=compliance_ethics_agent,
    context=[research_facebook_groups, analyze_group_quality, develop_engagement_strategy],  # Depends on all previous tasks
    expected_output="""A compliance and ethics assessment including:
    1. Platform Compliance Review:
       a. Facebook Community Standards: [Compliance status]
       b. Group-Specific Rules: [Analysis of each group's posting guidelines]
       c. Promotion Policies: [What each group allows regarding business promotion]
    2. Ethical Marketing Assessment:
       a. Value-to-Promotion Ratio: [Recommended balance]
       b. Transparency Requirements: [How to disclose business interests]
       c. Authenticity Guidelines: [How to engage genuinely]
    3. Risk Assessment:
       a. High-Risk Groups: [Groups with strict anti-promotion policies]
       b. Medium-Risk Groups: [Groups requiring careful approach]
       c. Low-Risk Groups: [Groups more open to business discussions]
    4. Best Practices Recommendations:
       a. [List of do's and don'ts for each group type]
       b. [Templates for appropriate introductions and promotions]
       c. [Warning signs to watch for that might indicate policy violations]
    5. Long-term Relationship Strategy:
       a. [How to build lasting relationships in these communities]
       b. [Ways to become a valued community member beyond promotion]
    6. Crisis Management: [What to do if posts are removed or warnings are received]

    Provide clear, actionable guidance to ensure all engagement is ethical and compliant."""
)

# Function to process group research for a specific niche or region
def process_group_research(research_focus):
    """
    Process research for a single focus area using the crew of agents.
    """
    print(f"\n🔍 Processing research focus...")
    print("-" * 50)
    
    crew = Crew(
        agents=[facebook_group_researcher, group_quality_analyzer, engagement_strategy_agent, compliance_ethics_agent],
        tasks=[research_facebook_groups, analyze_group_quality, develop_engagement_strategy, assess_compliance_ethics],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff(inputs={"research_focus": research_focus})
    print(f"✅ Research focus completed!")
    return result

# Main function to research Facebook groups
def find_facebook_groups_interactive():
    """
    Interactive function to find Facebook groups based on user configuration.
    """
    # Get user configuration
    config = get_user_search_focus()
    
    # Generate research focuses based on configuration
    research_focuses = generate_research_focuses(config)
    
    print(f"\n🚀 Starting research with {len(research_focuses)} focus area(s)...")
    
    results = []
    for i, focus in enumerate(research_focuses, 1):
        print(f"\n📋 Research Focus {i} of {len(research_focuses)}")
        print("=" * 60)
        result = process_group_research(focus)
        results.append(result)
        print(f"✅ Completed focus {i} of {len(research_focuses)}")
    
    # Save results to file
    print(f"\n💾 Saving results to file...")
    filepath = save_results_to_file(results, config)
    
    # Print completion summary
    print("\n" + "=" * 80)
    print("🎉 FACEBOOK GROUP RESEARCH COMPLETED!")
    print("=" * 80)
    print(f"✅ Total focus areas researched: {len(research_focuses)}")
    print(f"✅ Results saved to: {filepath}")
    print(f"✅ Research completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📝 Next Steps:")
    print("1. Review the saved file for detailed group analysis")
    print("2. Prioritize high-scoring groups for engagement")
    print("3. Follow compliance guidelines before posting")
    print("4. Implement suggested engagement strategies")
    print("5. Track engagement metrics and adjust approach")
    print("=" * 80)
    
    return results, filepath

# Legacy function for backward compatibility
def find_facebook_groups(research_focuses):
    """
    Legacy function that takes predefined research focuses.
    """
    results = []
    for i, focus in enumerate(research_focuses, 1):
        print(f"\n📋 Processing Research Focus {i} of {len(research_focuses)}")
        result = process_group_research(focus)
        results.append(result)
    return results

# Example predefined research focuses for podcastbots.ai (kept for reference)
example_research_focuses = [
    """
    Research Focus: General Podcasting and Broadcasting Communities
    - Target: Large, active Facebook groups focused on podcasting, radio broadcasting, and digital audio content
    - Geographic Scope: Global, English-speaking communities
    - Audience: Mix of beginner and experienced podcasters, radio hosts, and digital content creators
    - Product Relevance: Groups interested in podcast production tools, guest finding, and content enhancement
    - Business Context: podcastbots.ai is a tool that helps podcasters and broadcasters find and contact potential guests using AI agents
    - Value Proposition: Saves time in guest research and outreach, provides professional contact information
    """,
    """
    Research Focus: Business and Professional Broadcasting/Podcasting
    - Target: Facebook groups focused on business podcasting, professional broadcasting, B2B content, and thought leadership
    - Geographic Scope: Global, primarily US/UK/Canada/Australia
    - Audience: Business professionals, radio hosts, and corporate content creators using podcasts/broadcasts for marketing and thought leadership
    - Product Relevance: Groups where members would value tools for finding expert guests and industry contacts
    - Business Context: podcastbots.ai helps identify and connect with industry experts and thought leaders for interviews
    - Value Proposition: Enhances podcast/broadcast quality by connecting with high-caliber guests and subject matter experts
    """,
    """
    Research Focus: Content Creator, Broadcasting, and Marketing Communities
    - Target: Facebook groups for content creators, digital marketers, radio broadcasters, and social media professionals
    - Geographic Scope: Global, English-speaking
    - Audience: Content creators, radio personalities, and digital marketers who use podcasts/broadcasts as part of their content strategy
    - Product Relevance: Groups interested in content creation tools, broadcasting equipment, and automation
    - Business Context: podcastbots.ai as part of a broader content creation and broadcasting toolkit
    - Value Proposition: Streamlines the guest booking process for content creators and broadcast professionals
    """,
    """
    Research Focus: Radio Broadcasting and Traditional Media Communities
    - Target: Facebook groups for radio professionals, broadcast journalists, and traditional media transitioning to digital
    - Geographic Scope: Global, with focus on English-speaking markets
    - Audience: Radio hosts, broadcast journalists, station managers, and media professionals exploring podcasting
    - Product Relevance: Groups where traditional broadcasters are expanding into podcasting and need guest booking solutions
    - Business Context: podcastbots.ai helps traditional broadcasters leverage their interview skills in the podcasting space
    - Value Proposition: Bridges traditional broadcasting expertise with modern podcast guest discovery and outreach
    """
]

# Main execution
if __name__ == "__main__":
    print("🚀 Welcome to the Facebook Group Finder Tool!")
    print()
    
    # Ask user if they want to use interactive mode or example mode
    print("Choose your mode:")
    print("1) Interactive mode (customize search for your product/service)")
    print("2) Example mode (use predefined podcastbots.ai search)")
    print("3) Exit")
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    if choice == "1":
        # Interactive mode
        results, filepath = find_facebook_groups_interactive()
        
    elif choice == "2":
        # Example mode with predefined focuses
        print("\n🔄 Running example search for podcastbots.ai...")
        results = find_facebook_groups(example_research_focuses)
        
        # Save example results
        example_config = {
            "product_name": "podcastbots.ai",
            "product_description": "AI-powered podcast guest finding and contact tool",
            "target_audience": "podcasters, broadcasters, content creators",
            "value_proposition": "saves time in guest research and outreach",
            "region_choice": "5",  # All regions
            "num_groups": "15-20"
        }
        filepath = save_results_to_file(results, example_config)
        
        print("\n" + "=" * 80)
        print("🎉 EXAMPLE FACEBOOK GROUP RESEARCH COMPLETED!")
        print("=" * 80)
        print(f"✅ Results saved to: {filepath}")
        print("=" * 80)
        
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Please run the script again.")
