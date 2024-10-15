import React, { useState } from 'react';

export default function AIResearchAssistant() {
  const [topic, setTopic] = useState('');
  const [agents, setAgents] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const generateAgents = async () => {
    if (!topic.trim()) {
      setError('Please enter a research topic');
      return;
    }
    setError('');
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/generate_agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });
      if (!response.ok) {
        throw new Error('Failed to generate agents');
      }
      const data = await response.json();
      setAgents(data.agents);
      setTasks(data.tasks);
    } catch (error) {
      console.error('Error generating agents:', error);
      setError('Failed to generate agents. Please try again.');
    }
    setIsLoading(false);
  };

  const runResearch = async () => {
    setError('');
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/run_research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ agents, tasks }),
      });
      if (!response.ok) {
        throw new Error('Failed to run research');
      }
      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.error('Error running research:', error);
      setError('Failed to run research. Please try again.');
    }
    setIsLoading(false);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">AI Research Assistant</h1>
      <div className="mb-4">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter research topic"
          className="border p-2 mr-2"
        />
        <button
          onClick={generateAgents}
          className="bg-blue-500 text-white p-2 rounded"
          disabled={isLoading}
        >
          Generate Agents
        </button>
      </div>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      {isLoading && <p className="mb-4">Loading...</p>}
      {agents.length > 0 && (
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Generated Agents and Tasks</h2>
          {agents.map((agent, index) => (
            <div key={index} className="mb-2 p-4 border rounded">
              <h3 className="font-semibold">{agent.role}</h3>
              <p><strong>Goal:</strong> {agent.goal}</p>
              <p><strong>Backstory:</strong> {agent.backstory}</p>
              <p><strong>Task:</strong> {tasks[index].description}</p>
            </div>
          ))}
          <button
            onClick={runResearch}
            className="bg-green-500 text-white p-2 rounded mt-2"
            disabled={isLoading}
          >
            Run Research
          </button>
        </div>
      )}
      {result && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Research Results</h2>
          <pre className="bg-gray-100 p-4 rounded whitespace-pre-wrap">{result}</pre>
        </div>
      )}
    </div>
  );
}
