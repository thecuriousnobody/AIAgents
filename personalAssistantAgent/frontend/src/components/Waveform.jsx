import React, { useEffect, useState } from 'react'

const Waveform = ({ isRecording, audioLevels = [] }) => {
  const [staticLevels, setStaticLevels] = useState([])

  // Initialize static levels for when not recording
  useEffect(() => {
    const levels = Array.from({ length: 20 }, () => Math.random() * 20 + 10)
    setStaticLevels(levels)
  }, [])

  // Use real levels when recording, static when not
  const displayLevels = isRecording && audioLevels.length > 0 ? audioLevels.slice(0, 20) : staticLevels

  // Don't show waveform when not recording
  if (!isRecording) {
    return null
  }

  return (
    <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl p-4 backdrop-blur-sm border border-white/30 shadow-lg">
      <div className="flex items-center justify-center space-x-1">
        {displayLevels.length > 0 ? (
          displayLevels.map((level, index) => (
            <div
              key={index}
              className="waveform-bar bg-gradient-to-t from-blue-400 to-purple-400 rounded-full transition-all duration-75"
              style={{
                height: `${Math.max(8, Math.min(level, 50))}px`,
                width: '4px',
                opacity: isRecording ? 1 : 0.3
              }}
            />
          ))
        ) : (
          // Fallback static bars
          Array.from({ length: 20 }).map((_, index) => (
            <div
              key={index}
              className="waveform-bar bg-gradient-to-t from-blue-400 to-purple-400 rounded-full"
              style={{
                height: `${Math.random() * 30 + 8}px`,
                width: '4px',
                opacity: 0.8
              }}
            />
          ))
        )}
      </div>
      
      <div className="text-center mt-3">
        <div className="flex items-center justify-center space-x-2">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-white/80">Recording...</span>
        </div>
      </div>
    </div>
  )
}

export default Waveform
