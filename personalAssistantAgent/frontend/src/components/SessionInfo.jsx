import React from 'react'
import { Clock, Activity } from 'lucide-react'
import { formatTimestamp } from '../utils/helpers'

const SessionInfo = ({ sessionId, status }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'recording':
        return <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
      case 'transcribing':
      case 'getting_response':
      case 'executing':
        return <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
      case 'completed':
        return <div className="w-3 h-3 bg-green-500 rounded-full" />
      case 'error':
        return <div className="w-3 h-3 bg-red-500 rounded-full" />
      default:
        return <div className="w-3 h-3 bg-gray-500 rounded-full" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'ready':
        return 'Ready'
      case 'recording':
        return 'Recording'
      case 'transcribing':
        return 'Transcribing'
      case 'getting_response':
        return 'Processing'
      case 'awaiting_approval':
        return 'Awaiting Approval'
      case 'executing':
        return 'Executing'
      case 'completed':
        return 'Completed'
      case 'error':
        return 'Error'
      default:
        return 'Unknown'
    }
  }

  return (
    <div className="bg-white/5 rounded-lg p-4 mb-6 border border-white/10">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-white/60" />
            <span className="text-white/60">Session:</span>
            <span className="text-white font-mono text-xs">
              {sessionId.split('_').pop()}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="text-white/80 font-medium">
              {getStatusText()}
            </span>
          </div>
        </div>
        
        <div className="flex items-center space-x-2 text-white/40">
          <Clock className="w-4 h-4" />
          <span>{formatTimestamp(new Date())}</span>
        </div>
      </div>
    </div>
  )
}

export default SessionInfo
