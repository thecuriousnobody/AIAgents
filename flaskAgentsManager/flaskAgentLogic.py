from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_agent', methods=['POST'])
def add_agent():
    # Get agent data from the request
    agent_name = request.form['agent_name']
    agent_role = request.form['agent_role']

    # Call your add_agent logic here
    # ...

    # Return a response or redirect
    return 'Agent added successfully'

if __name__ == '__main__':
    app.run(debug=True)
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent Manager</title>
</head>
<body>
    <h1>Add Agent</h1>
    <form action="{{ url_for('add_agent') }}" method="post">
        <label for="agent_name">Agent Name:</label>
        <input type="text" id="agent_name" name="agent_name" required>

        <label for="agent_role">Agent Role:</label>
        <input type="text" id="agent_role" name="agent_role" required>

        <button type="submit">Add Agent</button>
    </form>
</body>
</html>