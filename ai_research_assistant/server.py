from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

@app.route('/create_agent', methods=['POST'])
def create_agent():
    data = request.json
    # Simulate agent creation and execution
    time.sleep(2)  # Simulate some processing time
    return jsonify({
        "message": f"Agent created and executed for topic: {data.get('topic')}",
        "results": "Here are the simulated research results..."
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)