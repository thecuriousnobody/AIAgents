import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from crewai import Agent, Task
from langchain_openai import ChatOpenAI

# Load environment variables
#load_dotenv()

# Initialize the language model
llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=config.GROQ_API_KEY,
    model_name="llama3-70b-8192"
)

def send_emails(agent, task):
    print("Starting email sending process...")
    print("Agent role:", agent.role)
    print("Agent goal:", agent.goal)
    print("Task description:", task.description)

    # Execute the task
    email_result = agent.execute_task(task)

    print("\nEmail Sending Results:")
    print(f"Emails sent: {email_result['sent']}")
    print(f"Emails failed: {email_result['failed']}")
    print(f"Open rate: {email_result['open_rate']}%")
    print(f"Click-through rate: {email_result['click_rate']}%")

    print("\nEmail sending process complete.")
    return email_result

def create_email_sender_agent():
    return Agent(
        role="Email Sender",
        goal="Send the AI newspaper to subscribers efficiently and track engagement",
        backstory="""You are an AI specialized in email communications and managing subscriber lists. 
        Your task is to send the AI newspaper to subscribers, ensure high deliverability, 
        and track engagement metrics. You understand email best practices and can optimize 
        for improved open rates and click-through rates.""",
        verbose=True,
        llm=llm
    )

def create_email_sending_task(newspaper_layout):
    return Task(
        description=f"""Send the AI newspaper to the subscriber list and track engagement. Your task includes:
        1. Prepare the email content based on the newspaper layout
        2. Segment the subscriber list if necessary
        3. Send the emails using an appropriate email service provider
        4. Track delivery status, open rates, and click-through rates
        5. Handle any bounce backs or delivery failures
        6. Provide a summary of the email campaign performance

        Ensure compliance with anti-spam regulations and email best practices.""",
        agent=create_email_sender_agent()
    )

if __name__ == "__main__":
    # For testing purposes
    import json
    with open("newspaper_layout.json", "r") as f:
        newspaper_layout = json.load(f)
    
    agent = create_email_sender_agent()
    task = create_email_sending_task(newspaper_layout)
    email_result = send_emails(agent, task)

    # Save the email sending results to a file
    with open("email_results.json", "w") as f:
        json.dump(email_result, f, indent=2)
    print("Email sending results saved to 'email_results.json'")