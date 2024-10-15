import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [topic, setTopic] = useState('');
  const [result, setResult] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/create_agent', { topic });
      setResult(response.data.message + '\n' + response.data.results);
    } catch (error) {
      setResult('Error: ' + error.message);
    }
  };

  return (
    <div className="App">
      <h1>AI Swiss Army Interns</h1>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={topic} 
          onChange={(e) => setTopic(e.target.value)} 
          placeholder="Enter research topic"
        />
        <button type="submit">Create Interns</button>
      </form>
      {result && <pre>{result}</pre>}
    </div>
  );
}

export default App;