import os
import sys
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('podcast_outreach.log'),
        logging.StreamHandler()
    ]
)

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from crewai import Agent, Task, Crew, Process
from usefulTools.search_tools import serper_search_tool
from usefulTools.llm_repository import ClaudeSonnet
from podcastPersonalityFinder.podcastHostParser import PodcastHostParser

class PodcastOutreachEmailCrew:
    def __init__(self, input_file):
        """
        Initialize the podcast outreach email crew
        
        :param input_file: Path to the markdown or text file with podcast host information
        """
        self.input_file = input_file
        self.podcasts = self._parse_input_file()
        self.founder_context = {
            'name': 'Rajeev Kumar',
            'email': 'rajeev@theideasandbox.com',
            'website': 'tisb.world',
            'podcast': 'The Idea Sandbox',
            'mission': 'Bringing technological solutions to expand podcast reach'
        }

    def _parse_input_file(self):
        """
        Parse input file using PodcastHostParser
        
        :return: Parsed podcast information
        """
        parser = PodcastHostParser(self.input_file)
        return parser.parse()

    def create_agents(self):
        """
        Create agents for podcast outreach email generation
        
        :return: List of agents
        """
        # Podcast Context Analysis Agent
        context_agent = Agent(
            role="Podcast Context Specialist",
            goal="Understand the unique context and potential needs of each podcast",
            backstory="You are an expert at identifying the core essence of podcasts and their potential challenges in guest discovery.",
            verbose=True,
            allow_delegation=True,
            tools=[serper_search_tool],
            llm=ClaudeSonnet
        )

        # Email Crafting Agent
        email_agent = Agent(
            role="Precision Outreach Composer",
            goal="Create concise, compelling emails that clearly communicate Podcast Bots' value proposition",
            backstory="You are a master of crafting targeted, professional communication that resonates with podcast creators.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet
        )

        return [context_agent, email_agent]

    def create_tasks(self, agents, podcast):
        """
        Create tasks for email generation
        
        :param agents: List of agents
        :param podcast: Dictionary of podcast details
        :return: List of tasks
        """
        context_agent, email_agent = agents

        # Podcast Context Analysis Task
        context_task = Task(
            description=f"Analyze the context and potential needs of {podcast['name']} podcast",
            agent=context_agent,
            expected_output="""Detailed podcast profile including:
            1. Podcast's core focus
            2. Potential guest discovery challenges
            3. Key communication points
            4. Unique aspects of the podcast"""
        )

        # Email Crafting Task
        email_task = Task(
            description=f"Craft a precise, value-driven email for {podcast['name']} podcast host",
            agent=email_agent,
            expected_output="""Comprehensive email draft with:
            1. Personalized subject line
            2. Clear value proposition
            3. Founder's personal connection
            4. Soft call-to-action for beta program
            5. Professional and engaging tone""",
            context=[context_task]
        )

        return [context_task, email_task]

    def _extract_email_content(self, output):
        """
        Robust method to extract email content from CrewAI output
        
        :param output: CrewAI output object
        :return: Tuple of (subject, body) or (None, None)
        """
        try:
            # Convert output to string
            output_str = str(output)
            
            # More flexible parsing
            subject_patterns = [
                r'Personalized subject line:\s*(.+?)(?=\n|$)',
                r'1\. Personalized subject line:\s*(.+?)(?=\n|$)',
                r'Subject:\s*(.+?)(?=\n|$)'
            ]
            
            body_patterns = [
                r'2\. Focused value proposition:\s*(.+?)(?=3\.|\n\n|$)',
                r'Comprehensive email draft with:.+?2\. Clear value proposition:\s*(.+?)(?=3\.|\n\n|$)',
                r'Value Proposition:\s*(.+?)(?=\n\n|$)'
            ]
            
            # Try multiple subject extraction patterns
            subject = None
            for pattern in subject_patterns:
                match = re.search(pattern, output_str, re.DOTALL | re.IGNORECASE)
                if match:
                    subject = match.group(1).strip()
                    break
            
            # Try multiple body extraction patterns
            body = None
            for pattern in body_patterns:
                match = re.search(pattern, output_str, re.DOTALL | re.IGNORECASE)
                if match:
                    body = match.group(1).strip()
                    break
            
            return subject, body
        
        except Exception as e:
            logging.error(f"Error extracting email content: {e}")
            logging.debug(f"Full output: {output}")
            return None, None

    def generate_emails(self, output_dir='podcast_outreach_emails'):
        """
        Generate personalized emails for all podcasts
        
        :param output_dir: Directory to save generated emails
        """
        os.makedirs(output_dir, exist_ok=True)

        # Iterate through tiers
        for tier, tier_podcasts in self.podcasts.items():
            for podcast in tier_podcasts:
                # Skip if no verified email
                if not podcast.get('verified_emails') or 'not found' in str(podcast.get('verified_emails', '')).lower():
                    logging.warning(f"Skipping {podcast['name']}: No verified email")
                    continue

                # Create agents and tasks for this podcast
                agents = self.create_agents()
                tasks = self.create_tasks(agents, podcast)

                # Create and run crew
                try:
                    crew = Crew(
                        agents=agents,
                        tasks=tasks,
                        verbose=True,
                        process=Process.sequential
                    )

                    # Generate email
                    output = crew.kickoff()
                    
                    # Extract email content
                    subject, body = self._extract_email_content(output)
                    
                    if subject and body:
                        # Sanitize filename
                        safe_filename = re.sub(r'[^\w\-_\. ]', '_', podcast['name'])
                        email_file_path = os.path.join(output_dir, f'{safe_filename}_outreach_email.txt')
                        
                        # Construct full email with founder's context
                        full_email = f"""To: {podcast.get('verified_emails', 'N/A')}
Subject: {subject}

Dear Podcast Host,

{body}

A Personal Note from Our Founder:
I'm Rajeev Kumar, an engineer with two decades of engineering experience who started The Idea Sandbox podcast. Like you, I understand the challenges of creating and growing a podcast. I deeply believe podcasting is becoming a critical medium for social discourse, and I'm passionate about bringing technological solutions to help podcasters expand their reach.

Our mission at Podcast Bots is to empower creators like you with tools that make guest discovery and podcast growth easier.

Best regards,
{self.founder_context['name']}
Founder, Podcast Bots
{self.founder_context['email']}
{self.founder_context['website']}
"""
                        
                        with open(email_file_path, 'w', encoding='utf-8') as email_file:
                            email_file.write(full_email)
                        
                        logging.info(f"Generated email for {podcast['name']}")
                    else:
                        logging.error(f"Could not extract email content for {podcast['name']}")
                
                except Exception as e:
                    logging.error(f"Error generating email for {podcast['name']}: {e}")

def main():
    input_file = input("Enter the path to the podcast hosts text file: ")
    email_crew = PodcastOutreachEmailCrew(input_file)
    email_crew.generate_emails()

if __name__ == '__main__':
    main()
