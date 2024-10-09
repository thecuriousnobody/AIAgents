import sys
import os

# Ensure this path points to the directory containing your agent_generator.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_generator import generate_agents_and_tasks, run_research_crew

def simulate_user_interaction():
    research_topic = input("Enter a research topic: ")
    
    print(f"\nGenerating agents and tasks for: '{research_topic}'")
    agents, tasks = generate_agents_and_tasks(research_topic)
    
    print("\nGenerated Agents and Tasks:")
    for i, (agent, task) in enumerate(zip(agents, tasks), 1):
        print(f"\nAgent {i}:")
        print(f"Role: {agent.role}")
        print(f"Goal: {agent.goal}")
        print(f"Backstory: {agent.backstory}")
        print(f"\nTask {i}:")
        print(f"Description: {task.description}")
        print(f"Expected Output: {task.expected_output}")
    
    approval = input("\nAre you satisfied with these agents and tasks? (yes/no): ").lower()
    
    if approval == 'yes':
        print("\nRunning the research process...")
        result = run_research_crew(research_topic)
        print("\nResearch Results:")
        print(result)
    else:
        print("Research process cancelled. You can start over with a new topic.")

if __name__ == "__main__":
    while True:
        simulate_user_interaction()
        
        continue_testing = input("\nDo you want to test another topic? (yes/no): ").lower()
        if continue_testing != 'yes':
            print("Exiting test script.")
            break