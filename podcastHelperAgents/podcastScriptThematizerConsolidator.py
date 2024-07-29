import os
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620"
)
def create_thematizer_agent():
    return Agent(
        role="Meticulous Content Organizer",
        goal="Organize all content into logical themes while preserving every unique question and point",
        backstory="You are an expert at identifying themes and organizing information without losing any original content. Your primary focus is on preserving every unique question and point while creating a logical structure.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
def preprocess_content(content):
    # Split content into individual questions/points
    items = content.split('\n')
    # Remove any empty items
    items = [item.strip() for item in items if item.strip()]
    # Remove exact duplicates while preserving order
    unique_items = []
    seen = set()
    for item in items:
        if item not in seen:
            unique_items.append(item)
            seen.add(item)
    return unique_items


def read_content(input_path):
    if os.path.isdir(input_path):
        file_contents = []
        for filename in os.listdir(input_path):
            if filename.endswith(".txt"):
                try:
                    with open(os.path.join(input_path, filename), 'r', encoding='utf-8') as file:
                        file_contents.append(file.read())
                except UnicodeDecodeError:
                    try:
                        with open(os.path.join(input_path, filename), 'r', encoding='iso-8859-1') as file:
                            file_contents.append(file.read())
                    except UnicodeDecodeError:
                        print(f"Unable to read file {filename} with UTF-8 or ISO-8859-1 encoding. Skipping.")
        return "\n\n".join(file_contents)
    elif os.path.isfile(input_path):
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(input_path, 'r', encoding='iso-8859-1') as file:
                return file.read()
    else:
        raise ValueError("Input path is neither a file nor a directory")

def thematize_content_task(agent, content):
    return Task(
        description=f"""Organize the following content into themes, creating a logically progressive format for a podcast interview. 
        Your primary objective is to preserve EVERY SINGLE UNIQUE QUESTION AND POINT. Do not exclude, modify, or summarize any unique content.

        Rules:
        1. Create themes that progress from introductory concepts to more in-depth research topics.
        2. For each theme, provide a brief description.
        3. Group all relevant questions and points under each theme.
        4. Do not change the wording of any question or point.
        5. Include every unique item from the input in your output.
        6. If a question or point could fit under multiple themes, include it in all relevant themes.
        7. If you're unsure where a question or point fits, create a "Miscellaneous" theme at the end.

        Content to organize:
        {content}

        Format your response as follows:
        Theme 1: [Theme Name]
        Description: [Brief theme description]
        - [Question/Point 1]
        - [Question/Point 2]
        ...

        Theme 2: [Theme Name]
        Description: [Brief theme description]
        - [Question/Point 3]
        - [Question/Point 4]
        ...

        [Continue for all themes]

        Miscellaneous:
        - [Any questions/points that don't fit clearly into other themes]

        CRITICAL: Verify that every single unique item from the input is included in your output.""",
        agent=agent,
        expected_output="A comprehensive, structured outline of themes with every single unique question and point from the input preserved and organized."
    )
def kickoff_crew(crew):
    output = crew.kickoff()
    if hasattr(output, 'result'):
        return output.result
    elif isinstance(output, str):
        return output
    else:
        return str(output)

def main(input_path, output_file):
    thematizer_agent = create_thematizer_agent()

    # Read content
    content = read_content(input_path)

    # Preprocess content to identify unique items
    unique_items = preprocess_content(content)
    preprocessed_content = "\n".join(unique_items)

    # Thematize content
    thematize_task = thematize_content_task(thematizer_agent, preprocessed_content)
    thematize_crew = Crew(
        agents=[thematizer_agent],
        tasks=[thematize_task],
        verbose=2,
        process=Process.sequential
    )
    thematized_content = kickoff_crew(thematize_crew)

    # Write the thematized content to a file
    with open(output_file, 'w') as f:
        f.write(thematized_content)

    print(f"Thematized content has been written to {output_file}")

if __name__ == "__main__":
    input_path = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Amber Case/Amber Case.txt"  # This can be either a directory or a single file
    output_file = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Amber Case/Amber Case Thematized V3.txt"
    main(input_path, output_file)