from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from agent_generator import generate_agents, run_research
import logging
import os
import sys

app = Flask(__name__)
CORS(app)

# Set up logging with an absolute path
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend.log')
logging.basicConfig(filename=log_file_path, level=logging.DEBUG)

# Add console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(console_handler)

@app.route('/')
def home():
    return jsonify({"message": "AI Interns Backend is running"}), 200

@app.route('/generate_agents', methods=['POST'])
def generate_agents_route():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        agents = generate_agents(query)
        return jsonify({"agents": agents})
    except Exception as e:
        error_message = f"Error generating agents: {str(e)}"
        logging.error(error_message)
        print(error_message, file=sys.stderr)
        return jsonify({"error": "Failed to generate agents. Please try again."}), 500

@app.route('/run_research', methods=['POST'])
def run_research_route():
    data = request.json
    agents = data.get('agents')
    if not agents:
        return jsonify({"error": "No agents provided"}), 400
    
    def generate():
        try:
            for chunk in run_research(agents):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            error_message = f"Error running research: {str(e)}"
            logging.error(error_message)
            print(error_message, file=sys.stderr)
            yield f"data: Error: Failed to run research. Please try again.\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
