import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5002';

export default function AISwissArmyInterns() {
  const [query, setQuery] = useState('');
  const [refinedQuery, setRefinedQuery] = useState('');
  const [agents, setAgents] = useState([]);
  const [liveView, setLiveView] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const generateAgents = async () => {
    if (!query.trim()) {
      setError('Please enter a research query');
      return;
    }
    setError('');
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/generate_agents`, { query });
      setAgents(response.data.agents);
      setRefinedQuery(query);
    } catch (error) {
      console.error('Error generating agents:', error);
      setError('Failed to generate agents. Please try again.');
    }
    setIsLoading(false);
  };

  const runResearch = async () => {
    setError('');
    setIsLoading(true);
    setLiveView('');

    try {
      const response = await axios.post(`${API_URL}/run_research`, { agents }, {
        responseType: 'text',
        onDownloadProgress: (progressEvent) => {
          const newData = progressEvent.currentTarget.response;
          setLiveView((prevData) => prevData + newData);
        },
      });

      setLiveView(response.data);
    } catch (error) {
      console.error('Error running research:', error);
      setError('Failed to run research. Please try again.');
    }

    setIsLoading(false);
  };

  const saveToFile = () => {
    const blob = new Blob([liveView], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'research_results.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-orange-500 min-h-screen text-white">
      <header className="p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">AI Swiss Army Interns</h1>
        <nav>
          <button className="mx-2 text-white">Pricing</button>
          <button className="mx-2 text-white">Contact</button>
          <button className="mx-2 text-white">About</button>
        </nav>
      </header>
      <main className="container mx-auto p-4">
        <h2 className="text-4xl font-bold mb-4">Your On-Demand AI Research Team</h2>
        <div className="mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your research query here"
            className="w-full p-2 text-black"
          />
          <button
            onClick={generateAgents}
            className="bg-black text-white p-2 mt-2 w-full"
            disabled={isLoading}
          >
            Refine Query
          </button>
        </div>
        {refinedQuery && (
          <div className="mb-4">
            <h3 className="text-xl font-semibold mb-2">Refined Query:</h3>
            <input
              type="text"
              value={refinedQuery}
              onChange={(e) => setRefinedQuery(e.target.value)}
              className="w-full p-2 text-black"
            />
          </div>
        )}
        {error && <p className="text-red-300 mb-4">{error}</p>}
        {isLoading && <p className="mb-4">Loading...</p>}
        {agents.length > 0 && (
          <div className="mb-4">
            <h3 className="text-2xl font-semibold mb-2">Generated Agents</h3>
            <div className="grid grid-cols-3 gap-4">
              {agents.map((agent, index) => (
                <div key={index} className="bg-orange-400 p-4 rounded">
                  <h4 className="font-semibold">{agent.role}</h4>
                  <p>{agent.description}</p>
                  <label className="flex items-center mt-2">
                    <input
                      type="checkbox"
                      checked={agent.useGoogleSearch}
                      onChange={() => {
                        const updatedAgents = [...agents];
                        updatedAgents[index].useGoogleSearch = !updatedAgents[index].useGoogleSearch;
                        setAgents(updatedAgents);
                      }}
                      className="mr-2"
                    />
                    Add Google Search
                  </label>
                </div>
              ))}
            </div>
            <button
              onClick={runResearch}
              className="bg-black text-white p-2 mt-4 w-full"
              disabled={isLoading}
            >
              Run Research
            </button>
          </div>
        )}
        {liveView && (
          <div className="mb-4">
            <h3 className="text-2xl font-semibold mb-2">Research Progress</h3>
            <div className="bg-white text-black p-4 rounded h-64 overflow-auto">
              <pre className="whitespace-pre-wrap">{liveView}</pre>
            </div>
            <button
              onClick={saveToFile}
              className="bg-black text-white p-2 mt-2 w-full"
            >
              Save Research to File
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
