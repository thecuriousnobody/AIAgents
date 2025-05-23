from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import re
from langchain.tools import Tool
from usefulTools.llm_repository import ClaudeSonnet
from usefulTools.search_tools import facebook_serper_tool, facebook_group_search_tool, us_serper_tool, uk_serper_tool, canada_serper_tool, australia_serper_tool

# Set up environment variables
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

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
    crew = Crew(
        agents=[facebook_group_researcher, group_quality_analyzer, engagement_strategy_agent, compliance_ethics_agent],
        tasks=[research_facebook_groups, analyze_group_quality, develop_engagement_strategy, assess_compliance_ethics],
        verbose=True,
        process=Process.sequential
    )

    return crew.kickoff(inputs={"research_focus": research_focus})

# Main function to research Facebook groups for different podcast niches
def find_facebook_groups(research_focuses):
    results = []
    for focus in research_focuses:
        result = process_group_research(focus)
        results.append(result)
    return results

# Example usage:
research_focuses = [
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

# Run the research
if __name__ == "__main__":
    results = find_facebook_groups(research_focuses)
    
    # Print results in a structured format
    print("=" * 80)
    print("FACEBOOK GROUP RESEARCH RESULTS FOR PODCASTBOTS.AI PROMOTION")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n\nRESEARCH FOCUS {i}:")
        print("-" * 40)
        print(result)
        print("\n" + "=" * 40)
