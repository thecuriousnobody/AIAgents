from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_research_assistant.agent_generator import generate_agents_and_tasks
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
import config

app = Flask(__name__)
CORS(app)

@app.route('/generate_agents', methods=['POST'])
def generate_agents():
    try:
        data = request.json
        if not data or 'topic' not in data:
            return jsonify({'error': 'Missing topic in request'}), 400
        
        topic = data['topic'].strip()
        if not topic:
            return jsonify({'error': 'Topic cannot be empty'}), 400

        agents, tasks = generate_agents_and_tasks(topic)
        return jsonify({
            'agents': [{'role': a.role, 'goal': a.goal, 'backstory': a.backstory} for a in agents],
            'tasks': [{'description': t.description, 'expected_output': t.expected_output} for t in tasks]
        }), 200
    except Exception as e:
        app.logger.error(f"Error in generate_agents: {str(e)}")
        return jsonify({'error': 'An error occurred while generating agents'}), 500

@app.route('/run_research', methods=['POST'])
def run_research():
    try:
        data = request.json
        if not data or 'agents' not in data or 'tasks' not in data:
            return jsonify({'error': 'Missing agents or tasks in request'}), 400

        agents_data = data['agents']
        tasks_data = data['tasks']

        if len(agents_data) != len(tasks_data):
            return jsonify({'error': 'Mismatch in number of agents and tasks'}), 400

        # Recreate Agent objects
        llm = ChatAnthropic(model="claude-3-sonnet-20240229", anthropic_api_key=config.ANTHROPIC_API_KEY)
        agents = [
            Agent(
                role=a['role'],
                goal=a['goal'],
                backstory=a['backstory'],
                llm=llm,
                verbose=True,
                allow_delegation=False
            ) for a in agents_data
        ]

        # Recreate Task objects
        tasks = [
            Task(
                description=t['description'],
                agent=agents[i],
                expected_output=t['expected_output']
            ) for i, t in enumerate(tasks_data)
        ]

        # Create and run Crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        result = crew.kickoff()
        return jsonify({'result': result}), 200
    except Exception as e:
        app.logger.error(f"Error in run_research: {str(e)}")
        return jsonify({'error': 'An error occurred while running the research'}), 500

if __name__ == '__main__':
    app.run(debug=True)
