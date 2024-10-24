import time
from agent_generator import generate_agents, run_research

def simulate_frontend():
    print("Welcome to the AI Interns Research Assistant")
    
    while True:
        query = input("Enter your research query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break

        print("Generating agents...")
        supervisor, agents = generate_agents(query)

        print("\nGenerated Agents:")
        for agent in agents:
            print(f"Role: {agent['role']}")
            print(f"Description: {agent['description']}")
            print()

        proceed = input("Do you want to run the research? (yes/no): ")
        if proceed.lower() == 'yes':
            print("\nRunning research...")
            for result in run_research(supervisor):
                print(result)
                print(f"Status: {supervisor.get_status()}")
                time.sleep(1)  # Simulate some delay between updates

        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    simulate_frontend()
