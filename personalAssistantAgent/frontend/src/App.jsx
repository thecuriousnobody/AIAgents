import React, { useState, useEffect } from 'react'
import { Mic, MicOff, Send, CheckCircle, XCircle, Edit3 } from 'lucide-react'
import AudioRecorder from './components/AudioRecorder'
import Waveform from './components/Waveform'
import TranscriptionDisplay from './components/TranscriptionDisplay'
import AgentResponse from './components/AgentResponse'
import ApprovalSection from './components/ApprovalSection'
import SessionInfo from './components/SessionInfo'
import { generateSessionId } from './utils/helpers'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  // State management
  const [sessionId, setSessionId] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [transcription, setTranscription] = useState('')
  const [agentResponse, setAgentResponse] = useState('')
  const [currentStatus, setCurrentStatus] = useState('ready')
  const [showApproval, setShowApproval] = useState(false)
  const [audioLevels, setAudioLevels] = useState([])
  const [error, setError] = useState('')
  const [conversationHistory, setConversationHistory] = useState([])
  const [isRefining, setIsRefining] = useState(false)

  // Initialize session on mount
  useEffect(() => {
    const newSessionId = generateSessionId()
    setSessionId(newSessionId)
    console.log('Session initialized:', newSessionId)
  }, [])

  // Handle recording state changes
  const handleRecordingChange = (recording) => {
    setIsRecording(recording)
    if (recording) {
      setCurrentStatus('recording')
      setError('')
    } else {
      // When recording stops, we'll get the audio and process it
      setCurrentStatus('ready')
    }
  }

  // Handle audio recording completion
  const handleAudioRecorded = async (audioBlob) => {
    try {
      setCurrentStatus('transcribing')
      setError('')
      
      // Create form data
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.wav')
      formData.append('session_id', sessionId)
      
      // Send to backend
      const response = await fetch(`${API_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        setTranscription(result.transcription)
        setCurrentStatus('getting_response')
        
        // Get agent response
        await getAgentResponse(result.transcription)
      } else {
        throw new Error(result.message || 'Transcription failed')
      }
      
    } catch (err) {
      console.error('Transcription error:', err)
      setError(`Transcription failed: ${err.message}`)
      setCurrentStatus('error')
    }
  }

  // Get conversational response from agent
  const getAgentResponse = async (text) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          session_id: sessionId
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        setAgentResponse(result.response)
        setShowApproval(true)
        setCurrentStatus('awaiting_approval')
      } else {
        throw new Error(result.message || 'Agent response failed')
      }
      
    } catch (err) {
      console.error('Agent response error:', err)
      setError(`Agent response failed: ${err.message}`)
      setCurrentStatus('error')
    }
  }

  // Handle approval
  const handleApprove = async () => {
    try {
      setCurrentStatus('executing')
      
      const response = await fetch(`${API_BASE_URL}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          action: 'approve'
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        setCurrentStatus('completed')
        console.log('Workflow completed:', result)
        
        // Reset after a delay
        setTimeout(() => {
          resetSession()
        }, 3000)
      } else {
        throw new Error(result.message || 'Approval failed')
      }
      
    } catch (err) {
      console.error('Approval error:', err)
      setError(`Approval failed: ${err.message}`)
      setCurrentStatus('error')
    }
  }

  // Handle rejection
  const handleReject = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          reason: 'User rejected the response'
        })
      })
      
      if (response.ok) {
        console.log('Response rejected')
      }
      
    } catch (err) {
      console.error('Rejection error:', err)
    }
    
    resetSession()
  }

  // Handle feedback
  const handleFeedback = async (feedback) => {
    try {
      const response = await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          feedback: feedback
        })
      })
      
      if (response.ok) {
        console.log('Feedback submitted')
        resetSession()
      }
      
    } catch (err) {
      console.error('Feedback error:', err)
      setError(`Feedback failed: ${err.message}`)
    }
  }

  // Handle refinement
  const handleRefine = async (refinementText) => {
    try {
      setIsRefining(true)
      setCurrentStatus('refining')
      setError('')
      
      // Build the conversation context
      const conversationContext = [
        `Original input: "${transcription}"`,
        `Previous agent response: "${agentResponse}"`,
        `Additional details: "${refinementText}"`
      ].join('\n\n')
      
      // Add to conversation history
      setConversationHistory(prev => [...prev, {
        type: 'user_refinement',
        content: refinementText,
        timestamp: new Date().toISOString()
      }])
      
      // Send refinement to agent
      const response = await fetch(`${API_BASE_URL}/refine`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          conversation_context: conversationContext,
          refinement: refinementText
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        // Update agent response with refined understanding
        setAgentResponse(result.refined_response)
        setCurrentStatus('awaiting_approval')
        
        // Add agent response to conversation history
        setConversationHistory(prev => [...prev, {
          type: 'agent_refined_response',
          content: result.refined_response,
          timestamp: new Date().toISOString()
        }])
        
        console.log('Refinement successful')
      } else {
        throw new Error(result.message || 'Refinement failed')
      }
      
    } catch (err) {
      console.error('Refinement error:', err)
      setError(`Refinement failed: ${err.message}`)
      setCurrentStatus('error')
    } finally {
      setIsRefining(false)
    }
  }

  // Reset session
  const resetSession = () => {
    setTranscription('')
    setAgentResponse('')
    setShowApproval(false)
    setCurrentStatus('ready')
    setError('')
    setAudioLevels([])
    setConversationHistory([])
    setIsRefining(false)
    
    // Generate new session ID
    const newSessionId = generateSessionId()
    setSessionId(newSessionId)
  }

  // Status messages
  const getStatusMessage = () => {
    switch (currentStatus) {
      case 'ready':
        return 'Click the microphone to start recording'
      case 'recording':
        return 'Recording... Click microphone again to stop and transcribe'
      case 'transcribing':
        return 'Processing your audio...'
      case 'getting_response':
        return 'Getting agent response...'
      case 'awaiting_approval':
        return 'Review the response and choose an action'
      case 'executing':
        return 'Executing workflow...'
      case 'completed':
        return 'Complete! Check sessions folder for results.'
      case 'error':
        return error || 'An error occurred'
      default:
        return 'Ready'
    }
  }

  const getStatusColor = () => {
    switch (currentStatus) {
      case 'recording':
        return 'text-red-500'
      case 'transcribing':
      case 'getting_response':
      case 'executing':
        return 'text-blue-500'
      case 'completed':
        return 'text-green-500'
      case 'error':
        return 'text-red-500'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glassmorphism max-w-4xl w-full p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🤖 Personal Assistant
          </h1>
          <p className="text-white/80 text-lg">
            Your intelligent multi-agent assistant for managing your four project lanes
          </p>
        </div>

        {/* Session Info */}
        <SessionInfo 
          sessionId={sessionId}
          status={currentStatus}
        />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Recording & Transcription */}
          <div className="space-y-6">
            {/* Audio Recording Section */}
            <div className="text-center">
              {/* Microphone and Waveform Row */}
              <div className="flex items-center justify-center space-x-6 mb-6">
                <AudioRecorder
                  isRecording={isRecording}
                  onRecordingChange={handleRecordingChange}
                  onAudioRecorded={handleAudioRecorded}
                  onAudioLevels={setAudioLevels}
                  disabled={currentStatus !== 'ready' && currentStatus !== 'recording'}
                />
                
                {/* Waveform appears to the right when recording */}
                <div className={`transition-all duration-300 ${isRecording ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>
                  <Waveform 
                    isRecording={isRecording}
                    audioLevels={audioLevels}
                  />
                </div>
              </div>
              
              {/* Status */}
              <div className={`text-lg font-medium ${getStatusColor()}`}>
                {getStatusMessage()}
              </div>
            </div>

            {/* Transcription Display */}
            <TranscriptionDisplay 
              transcription={transcription}
              isLoading={currentStatus === 'transcribing'}
            />
          </div>

          {/* Right Column - Agent Response & Approval */}
          <div className="space-y-6">
            {/* Agent Response */}
            {(agentResponse || currentStatus === 'getting_response') && (
              <AgentResponse 
                response={agentResponse}
                isLoading={currentStatus === 'getting_response'}
              />
            )}

            {/* Approval Section */}
            {showApproval && (
              <ApprovalSection
                onApprove={handleApprove}
                onReject={handleReject}
                onRefine={handleRefine}
                disabled={currentStatus === 'executing'}
                isRefining={isRefining}
              />
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4">
                <div className="flex items-center space-x-2 text-red-200">
                  <XCircle className="w-5 h-5" />
                  <span className="font-medium">Error</span>
                </div>
                <p className="text-red-100 mt-1">{error}</p>
                <button
                  onClick={resetSession}
                  className="mt-3 text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition-colors"
                >
                  Reset
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
