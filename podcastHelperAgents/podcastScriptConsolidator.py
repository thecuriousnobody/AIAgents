import os
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from PyPDF2 import PdfReader
import requests
from io import BytesIO

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
from usefulTools.llm_repository import ClaudeOpus,ClaudeSonnet
from usefulTools.search_tools import search_tool, search_api_tool


# Initialize LLM and search tool
llm = ClaudeSonnet

def read_pdf_from_file(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

import os
from pathlib import Path

def create_thematic_organizer_agent():
    return Agent(
        role="Question Theme Organizer",
        goal="Organize existing questions and discussion points into clear thematic categories",
        backstory="""You are a skilled curator who respects original content while bringing 
        clarity through thoughtful organization. You understand the delicate interplay 
        between personal narratives and broader societal patterns, always maintaining 
        sensitivity to cultural nuance and lived experience.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_api_tool]
    )

def create_synthesis_agent():
    return Agent(
        role="Narrative Synthesizer",
        goal="Create a condensed, flowing narrative from the thematically organized content",
        backstory="""You weave together complex threads of thought into cohesive narratives 
        that honor both individual perspective and collective understanding. Your strength 
        lies in finding the subtle resonances between different voices and experiences.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def write_output_to_file(content, original_path):
    # Get the directory and filename from the original path
    directory = os.path.dirname(original_path)
    filename = os.path.splitext(os.path.basename(original_path))[0]
    
    # Create new filename with _processed suffix
    new_filename = f"{filename}_processed.txt"
    output_path = os.path.join(directory, new_filename)
    
    # Write content to new file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path

def create_thematic_organization_task(organizer_agent, content):
    return Task(
        description=f"""Organize the following content into clear thematic categories 
        while preserving all original questions and discussion points exactly as written. 
        Use your search capability to enrich understanding of context and current developments:
        
        {content}
        
        Focus on:
        - Identifying natural thematic groupings that emerge from the material
        - Preserving all original language while providing relevant context
        - Maintaining the integrity of complex ideas and their interconnections
        - Revealing organic patterns and resonances between different themes
        - Enriching understanding with relevant contemporary context""",
        agent=organizer_agent,
        expected_output="""A richly contextualized document with:
        - Original questions and discussion points grouped by emergent themes
        - Thoughtful theme headings that honor the content's complexity
        - All original language preserved intact
        - Relevant contemporary context and developments
        - Clear delineation between thematic areas while showing interconnections
        Present as a structured document that respects both original material and broader context."""
    )

def create_synthesis_task(synthesis_agent, organized_content):
    return Task(
        description=f"""Create a condensed narrative synthesis that captures the essence 
        of the organized content while honoring its complexity and nuance:
        
        {organized_content}
        
        Focus on:
        - Weaving together essential themes and patterns
        - Preserving crucial nuances and deeper meanings
        - Illuminating meaningful connections between ideas
        - Creating a flowing narrative that invites deeper exploration""",
        agent=synthesis_agent,
        expected_output="""A thoughtful synthesis including:
        - Key thematic threads and their subtle interconnections
        - Essential questions and their broader implications
        - Important contextual elements and their relevance
        - Potential pathways for deeper dialogue
        Present as a flowing narrative that complements and illuminates the detailed organization."""
    )

def main(guest_name, content_path):
    content = read_pdf_from_file(content_path)

    organizer = create_thematic_organizer_agent()
    synthesizer = create_synthesis_agent()

    organization_task = create_thematic_organization_task(organizer, content)
    synthesis_task = create_synthesis_task(synthesizer, "{{organization_task.output}}")

    crew = Crew(
        agents=[organizer, synthesizer],
        tasks=[organization_task, synthesis_task],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()

    # Format the output
    formatted_output = f"""Conversation Guide for Dialogue with: {guest_name}

    PART 1: THEMATICALLY ORGANIZED ORIGINAL CONTENT
    =============================================
    {organization_task.output}

    PART 2: NARRATIVE SYNTHESIS
    =========================
    {synthesis_task.output}"""

    # Write to file
    output_path = write_output_to_file(formatted_output, content_path)
    
    print(f"\nOutput has been written to: {output_path}")
    print("\nPreview of content:")
    print(formatted_output[:500] + "...")

if __name__ == "__main__":
    guest_name = "Rahul Mehrotra"
    content_path = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Rahul Mehrotra/Rahul Mehrotra Prep - Final Draft 1.pdf"
    main(guest_name, content_path)