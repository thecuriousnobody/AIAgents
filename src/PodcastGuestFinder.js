import React, { useState } from 'react';
import { Mic, MicOff, Plus, Brain, Star, BookOpen, Users, Compass, DollarSign } from 'lucide-react';

const PodcastGuestFinder = () => {
  const [niche, setNiche] = useState('');
  const [podcastGuestFinderOutput, setPodcastGuestFinderOutput] = useState('');

  const handleNicheChange = (e) => {
    setNiche(e.target.value);
  };

  const handleSubmit = () => {
    // Fetch the output from the agents/podcastGuestFinderWithNicheProvided.py script
    fetch(`/Volumes/Samsung/GIT_Repos/potentiator-proto-dev/agents/podcastGuestFinderWithNicheProvided.py?niche=${encodeURIComponent(niche)}`)
      .then(response => response.text())
      .then(output => {
        setPodcastGuestFinderOutput(output);
      });
  };

  return (
    <div className="min-h-screen w-full bg-orange-500 fixed inset-0 overflow-auto flex">
      <div className="absolute top-8 left-8">
        <h1 className="text-2xl font-extralight tracking-wider text-white">potentiator<span className="text-black">.ai</span></h1>
      </div>
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        <div className="mb-8">
          <Brain size={48} className="text-white mb-4 mx-auto" />
        </div>
        <div className="w-full max-w-md">
          <input
            type="text"
            placeholder="Enter a niche"
            value={niche}
            onChange={handleNicheChange}
            className="w-full p-4 rounded-xl bg-black/30 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
          />
          <button
            onClick={handleSubmit}
            className="w-full mt-4 p-4 rounded-xl bg-black/30 hover:bg-black/40 text-white transition-all"
          >
            Find Podcast Guests
          </button>
        </div>
        {podcastGuestFinderOutput && (
          <div className="mt-8 w-full max-w-md bg-black/30 p-6 rounded-xl text-white font-mono whitespace-pre-wrap">
            {podcastGuestFinderOutput}
          </div>
        )}
      </div>
    </div>
  );
};

export default PodcastGuestFinder;
