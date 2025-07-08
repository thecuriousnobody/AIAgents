import React, { useState } from 'react'
import { CheckCircle, XCircle, Edit3, Send, Mic, MicOff } from 'lucide-react'
import AudioRecorder from './AudioRecorder'

const ApprovalSection = ({ 
  onApprove, 
  onReject, 
  onRefine, 
  disabled = false,
  isRefining = false 
}) => {
  const [showRefinement, setShowRefinement] = useState(false)
  const [refinementText, setRefinementText] = useState('')
  const [isRecordingRefinement, setIsRecordingRefinement] = useState(false)

  const handleRefinementSubmit = () => {
    if (refinementText.trim()) {
      onRefine(refinementText.trim())
      setRefinementText('')
      setShowRefinement(false)
    }
  }

  const handleRefinementCancel = () => {
    setRefinementText('')
    setShowRefinement(false)
    setIsRecordingRefinement(false)
  }

  const handleRefineClick = () => {
    setShowRefinement(true)
  }

  const handleRefinementRecording = async (audioBlob) => {
    try {
      // Create form data for transcription
      const formData = new FormData()
      formData.append('audio', audioBlob, 'refinement.wav')
      
      // Send to transcription endpoint
      const response = await fetch('http://localhost:8000/transcribe', {
        method: 'POST',
        body: formData
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          // Add transcribed text to the existing text (append mode)
          setRefinementText(prev => {
            const newText = result.transcription
            return prev ? `${prev}\n\n${newText}` : newText
          })
        }
      }
    } catch (error) {
      console.error('Refinement recording error:', error)
    }
  }

  return (
    <div className="bg-yellow-500/10 rounded-xl p-6 border border-yellow-500/20">
      <h4 className="text-lg font-semibold text-white mb-3">
        {isRefining ? "Refining understanding..." : "Does this capture your thoughts correctly?"}
      </h4>
      <p className="text-white/80 mb-4">
        {isRefining 
          ? "The agent is incorporating your additional details..."
          : "Review the agent's understanding. You can refine it with more details or approve to continue."
        }
      </p>
      
      {!showRefinement ? (
        <div className="flex flex-wrap gap-3">
          <button
            onClick={onApprove}
            disabled={disabled || isRefining}
            className="button-primary flex items-center space-x-2"
          >
            <CheckCircle className="w-5 h-5" />
            <span>Approve & Continue</span>
          </button>
          
          <button
            onClick={handleRefineClick}
            disabled={disabled || isRefining}
            className="button-secondary flex items-center space-x-2"
          >
            <Edit3 className="w-5 h-5" />
            <span>Add More Details</span>
          </button>
          
          <button
            onClick={onReject}
            disabled={disabled || isRefining}
            className="button-danger flex items-center space-x-2"
          >
            <XCircle className="w-5 h-5" />
            <span>Start Over</span>
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-black/20 rounded-lg p-4 border border-white/10">
            <label className="block text-white/80 text-sm font-medium mb-2">
              Add more details to refine the agent's understanding:
            </label>
            
            <div className="flex gap-2 mb-3">
              <textarea
                value={refinementText}
                onChange={(e) => setRefinementText(e.target.value)}
                placeholder="Type additional details or use the microphone to record..."
                className="flex-1 bg-black/30 border border-white/20 rounded-lg p-3 text-white placeholder-white/40 focus:border-blue-400 focus:outline-none resize-none"
                rows={4}
                autoFocus
              />
              
              <div className="flex-shrink-0">
                <AudioRecorder
                  isRecording={isRecordingRefinement}
                  onRecordingChange={setIsRecordingRefinement}
                  onAudioRecorded={handleRefinementRecording}
                  disabled={disabled}
                />
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <div className="text-xs text-white/50">
                💡 Tip: Use voice or text to add what the agent missed
              </div>
              {isRecordingRefinement && (
                <div className="text-xs text-red-300 animate-pulse">
                  🔴 Recording additional details...
                </div>
              )}
            </div>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={handleRefinementSubmit}
              disabled={!refinementText.trim() || disabled}
              className="button-primary flex items-center space-x-2"
            >
              <Send className="w-4 h-4" />
              <span>Refine Understanding</span>
            </button>
            
            <button
              onClick={handleRefinementCancel}
              disabled={disabled}
              className="button-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ApprovalSection
