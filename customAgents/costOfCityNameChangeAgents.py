from crewai import Agent, Task, Crew, Process
from langchain.agents import Tool
from langchain_openai import ChatOpenAI

# Assume these are properly imported and set up
from usefulTools.llm_repository import ClaudeOpus, ClaudeSonnet
from usefulTools.search_tools import search_tool, search_api_tool

llm = ClaudeSonnet

def create_indian_city_rename_cost_crew(city_name, new_name, population):
    # Define the agents
    research_agent = Agent(
        role="Indian City Infrastructure Researcher",
        goal=f"Research the various infrastructure and systems that would be affected by renaming {city_name} to {new_name} in India",
        backstory="You are an expert in Indian urban planning and city infrastructure. Your job is to identify all the systems and entities that would need to update their information due to a city name change, considering the Indian context.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_api_tool]
    )

    cost_estimation_agent = Agent(
        role="Indian Cost Estimation Specialist",
        goal=f"Estimate the costs in Indian Rupees associated with changing each identified system for an Indian city of {population} people",
        backstory="You are a financial analyst specializing in large-scale urban projects in India. You can estimate costs based on the scale of changes required, the size of the population affected, and the Indian economic context.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_api_tool]
    )

    impact_analysis_agent = Agent(
        role="Indian Socioeconomic Impact Analyzer",
        goal="Analyze the broader socioeconomic and cultural impacts of the name change in the Indian context",
        backstory="You are a socioeconomic researcher who understands the ripple effects of large-scale changes in Indian urban environments. You consider factors like business disruption, tourism impacts, and cultural implications specific to India.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    error_checking_agent = Agent(
        role="Data Verification Specialist",
        goal="Verify and cross-check all data and calculations provided by other agents",
        backstory="You are a meticulous data analyst with expertise in urban planning and Indian economics. Your role is to ensure accuracy in all estimates and analyses provided by the team.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    cultural_impact_agent = Agent(
        role="Cultural and Historical Impact Assessor",
        goal="Evaluate the non-financial impacts of the city name change on cultural identity and shared history",
        backstory="You are a cultural anthropologist specializing in Indian urban communities. Your expertise lies in assessing the intangible effects of changes on community identity and historical narrative.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    research_task = Task(
        description=f"Identify all systems, entities, and infrastructure that would need to be updated if {city_name} changed its name to {new_name}. Consider government, transportation, business, education, and other sectors in the Indian context.",
        agent=research_agent,
        expected_output="A comprehensive list of affected systems and entities, categorized by sector, specific to Indian urban infrastructure."
    )

    cost_estimation_task = Task(
        description=f"For each system identified, estimate the cost in Indian Rupees of implementing the name change. Consider factors like physical changes (signs, documents) and digital updates (databases, websites) for an Indian city of {population} people. Factor in the relatively lower labor costs in India.",
        agent=cost_estimation_agent,
        expected_output="A detailed breakdown of estimated costs in Indian Rupees for each affected system, with subtotals for each category and a grand total.",
        context=[research_task]
    )

    impact_analysis_task = Task(
        description=f"Analyze potential indirect costs and socioeconomic impacts of changing {city_name} to {new_name} in the Indian context. Consider effects on local businesses, tourism, cultural identity, and any potential benefits or drawbacks specific to India.",
        agent=impact_analysis_agent,
        expected_output="A report on the broader socioeconomic impacts in India, including potential long-term costs or benefits not captured in the direct cost estimation.",
        context=[cost_estimation_task]
    )

    error_checking_task = Task(
        description="Review all data, calculations, and analyses provided by other agents. Verify the accuracy of cost estimates, ensure all relevant systems have been considered, and cross-check impact assessments.",
        agent=error_checking_agent,
        expected_output="A verification report highlighting any discrepancies, errors, or areas needing further investigation, along with corrected figures where necessary.",
        context=[research_task, cost_estimation_task, impact_analysis_task]
    )

    cultural_impact_task = Task(
        description=f"Evaluate the non-financial impacts of changing {city_name} to {new_name} on cultural identity, shared history, and community sentiment. Consider both positive and negative effects on the local population's sense of belonging and historical continuity.",
        agent=cultural_impact_agent,
        expected_output="A qualitative assessment of cultural and historical impacts, including potential effects on community identity and historical narrative.",
        context=[impact_analysis_task, error_checking_task]
    )

    final_report_task = Task(
        description=f"Compile a comprehensive final report on the estimated costs and impacts of renaming {city_name} to {new_name}. Include financial breakdowns in Indian Rupees, socioeconomic impacts, and cultural considerations.",
        agent=error_checking_agent,
        expected_output="A detailed final report with cost breakdowns, impact assessments, and cultural considerations, all verified for accuracy.",
        context=[research_task, cost_estimation_task, impact_analysis_task, error_checking_task, cultural_impact_task]
    )

    # Create and return the crew
    return Crew(
        agents=[research_agent, cost_estimation_agent, impact_analysis_agent, error_checking_agent, cultural_impact_agent],
        tasks=[research_task, cost_estimation_task, impact_analysis_task, error_checking_task, cultural_impact_task, final_report_task],
        verbose=True,
        process=Process.sequential
    )

# Usage remains the same
city_name = "Bangalore"
new_name = "Bengaluru"
population = 12000000
crew = create_indian_city_rename_cost_crew(city_name, new_name, population)
result = crew.kickoff()

print(result)
