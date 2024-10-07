import React, { useState } from 'react';
import { Mic, Play, Save, Key, List, ChevronDown } from 'lucide-react';

export default function AIResearchAssistantLanding() {
  const [activeTab, setActiveTab] = useState('home');

  return (
    <div className="bg-gray-900 text-white min-h-screen">
      <header className="p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">AI Research Assistant</h1>
        <nav>
          <button className="px-4 py-2 bg-blue-600 rounded-md hover:bg-blue-700 transition">Try Now</button>
        </nav>
      </header>

      <main className="container mx-auto mt-10">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-bold mb-4">Revolutionize Your Research</h2>
          <p className="text-xl">Harness the power of AI to supercharge your research process</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 mb-10">
          <div className="flex mb-4">
            <button 
              className={`mr-4 ${activeTab === 'home' ? 'text-blue-500 border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('home')}
            >
              Home
            </button>
            <button 
              className={`mr-4 ${activeTab === 'agents' ? 'text-blue-500 border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('agents')}
            >
              Agents
            </button>
            <button 
              className={`mr-4 ${activeTab === 'api' ? 'text-blue-500 border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('api')}
            >
              API Keys
            </button>
            <button 
              className={`mr-4 ${activeTab === 'history' ? 'text-blue-500 border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              History
            </button>
          </div>

          {activeTab === 'home' && (
            <div>
              <div className="flex justify-center items-center mb-6">
                <button className="bg-blue-600 p-4 rounded-full hover:bg-blue-700 transition">
                  <Mic size={24} />
                </button>
                <span className="ml-4">Click to speak your research query</span>
              </div>
              <div className="bg-gray-700 p-4 rounded-lg mb-6">
                <h3 className="font-bold mb-2">Active Agents</h3>
                <ul>
                  <li className="mb-2">Requirement Analyzer</li>
                  <li className="mb-2">Research Expert</li>
                  <li className="mb-2">Information Consolidator</li>
                  <li>Summary Generator</li>
                </ul>
              </div>
              <button className="bg-green-600 px-6 py-3 rounded-md hover:bg-green-700 transition flex items-center justify-center w-full">
                <Play size={20} className="mr-2" />
                Run Research
              </button>
            </div>
          )}

          {activeTab === 'agents' && (
            <div>
              <h3 className="font-bold mb-4">Configure Agents</h3>
              {/* Agent configuration interface would go here */}
              <p>Agent configuration interface placeholder</p>
            </div>
          )}

          {activeTab === 'api' && (
            <div>
              <h3 className="font-bold mb-4">API Key Management</h3>
              <div className="flex items-center mb-4">
                <input type="text" placeholder="Enter API Key" className="bg-gray-700 p-2 rounded-md flex-grow mr-2" />
                <button className="bg-blue-600 p-2 rounded-md hover:bg-blue-700 transition">
                  <Save size={20} />
                </button>
              </div>
              <ul>
                <li className="flex justify-between items-center bg-gray-700 p-2 rounded-md mb-2">
                  <span>OpenAI API Key</span>
                  <Key size={20} />
                </li>
                <li className="flex justify-between items-center bg-gray-700 p-2 rounded-md">
                  <span>Anthropic API Key</span>
                  <Key size={20} />
                </li>
              </ul>
            </div>
          )}

          {activeTab === 'history' && (
            <div>
              <h3 className="font-bold mb-4">Research History</h3>
              <ul>
                <li className="bg-gray-700 p-2 rounded-md mb-2 flex justify-between items-center">
                  <span>South Asian History Research</span>
                  <ChevronDown size={20} />
                </li>
                <li className="bg-gray-700 p-2 rounded-md mb-2 flex justify-between items-center">
                  <span>AI Ethics Study</span>
                  <ChevronDown size={20} />
                </li>
                <li className="bg-gray-700 p-2 rounded-md flex justify-between items-center">
                  <span>Climate Change Analysis</span>
                  <ChevronDown size={20} />
                </li>
              </ul>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}