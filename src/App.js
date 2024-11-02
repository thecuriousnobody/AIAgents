import React, { useState } from 'react';
import { Mic, MicOff, Plus, Brain, Star, BookOpen, Users, Compass, DollarSign } from 'lucide-react';
import { Link } from 'react-router-dom';

const App = () => {
  const [isButtonActive, setIsButtonActive] = useState(false);

  const agents = [
    {
      name: 'Scholar',
      icon: <BookOpen size={24} className="text-white" />,
      languages: ['Hindi', 'English']
    },
    {
      name: 'Navigator',
      icon: <Compass size={24} className="text-white" />,
      languages: ['Tamil', 'English']
    },
    {
      name: 'Podcast Guest Finder',
      icon: <Brain size={24} className="text-white" />,
      languages: ['English']
    }
  ];

  const handlePodcastGuestFinderClick = () => {
    // Navigate to the Podcast Guest Finder page
    window.location.href = '/podcast-guest-finder';
  };

  return (
    <div className="min-h-screen w-full bg-orange-500 fixed inset-0 overflow-auto flex">
      <div className="absolute top-8 left-8">
        <h1 className="text-2xl font-extralight tracking-wider text-white">potentiator<span className="text-black">.ai</span></h1>
      </div>
      <div className="flex-1 flex flex-col items-center justify-center p-8 border-b md:border-b-0 md:border-r border-white/20">
        <div className="mb-8">
          <Brain size={48} className="text-white mb-4 mx-auto" />
        </div>
        <button
          onClick={() => setIsButtonActive(!isButtonActive)}
          className={`w-32 h-32 rounded-full flex items-center justify-center transition-all ${isButtonActive ? 'bg-black animate-pulse' : 'bg-white hover:bg-gray-50'}`}
        >
          {isButtonActive ? <Mic size={48} className="text-white" /> : <MicOff size={48} className="text-black" />}
        </button>
      </div>
      <div className="flex-1 flex flex-col p-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-extralight tracking-wide text-white">Agent Army</h2>
          <Link to="/podcast-guest-finder" className="w-12 h-12 rounded-full bg-black flex items-center justify-center hover:bg-gray-900 transition-colors">
            <Brain size={24} className="text-white" />
          </Link>
        </div>
        <div className="grid gap-4">
          {agents.map((agent, index) => (
            <button
              key={index}
              className="p-6 rounded-2xl bg-black/30 hover:bg-black/40 transition-all flex items-center justify-between w-full group border border-white/20"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-black flex items-center justify-center">
                  {agent.icon}
                </div>
                <div className="text-left">
                  <h3 className="text-xl font-extralight tracking-wide text-white">{agent.name}</h3>
                  <p className="text-sm font-light tracking-wide text-white/70">{agent.languages.join(" \u2022 ")}</p>
                </div>
              </div>
              {agent.name === 'Podcast Guest Finder' && (
                <Link to="/podcast-guest-finder" className="p-4 rounded-full bg-black/30 hover:bg-black/40 transition-all">
                  <Brain size={20} className="text-white" />
                </Link>
              )}
            </button>
          ))}
        </div>
        <div className="mt-auto">
          <div className="p-4 rounded-xl bg-black/30 flex items-center justify-center gap-2 border border-white/20">
            <Brain size={20} className="text-white" />
            <span className="text-white font-light tracking-wide">Free for Everyone</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
