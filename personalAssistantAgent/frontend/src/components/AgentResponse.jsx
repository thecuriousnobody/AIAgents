import React from 'react'
import { Bot, Loader2 } from 'lucide-react'

const AgentResponse = ({ response, isLoading = false }) => {
  return (
    <div className="bg-blue-500/10 rounded-xl p-6 border border-blue-500/20">
      <div className="flex items-center space-x-2 mb-4">
        <Bot className="w-5 h-5 text-blue-300" />
        <h3 className="text-lg font-semibold text-white">Agent Response</h3>
      </div>
      
      <div className="min-h-[120px] bg-blue-500/5 rounded-lg p-4 border border-blue-500/10">
        {isLoading ? (
          <div className="flex items-center justify-center space-x-2 text-blue-200">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Agent is thinking...</span>
          </div>
        ) : response ? (
          <div className="text-white text-lg leading-relaxed">
            {response}
          </div>
        ) : (
          <div className="text-blue-200/50 text-center italic">
            Agent response will appear here...
          </div>
        )}
      </div>
      
      {response && !isLoading && (
        <div className="mt-3">
          <span className="text-blue-200/60 text-sm">
            Personal Assistant • Conversational Response
          </span>
        </div>
      )}
    </div>
  )
}

export default AgentResponse
