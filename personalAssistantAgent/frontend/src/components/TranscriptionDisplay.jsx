import React from 'react'
import { FileText, Loader2 } from 'lucide-react'

const TranscriptionDisplay = ({ transcription, isLoading = false }) => {
  return (
    <div className="bg-white/10 rounded-xl p-6 border border-white/20">
      <div className="flex items-center space-x-2 mb-4">
        <FileText className="w-5 h-5 text-white/80" />
        <h3 className="text-lg font-semibold text-white">Real-time Transcription</h3>
      </div>
      
      <div className="min-h-[120px] bg-white/5 rounded-lg p-4 border border-white/10">
        {isLoading ? (
          <div className="flex items-center justify-center space-x-2 text-white/60">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Processing audio...</span>
          </div>
        ) : transcription ? (
          <div className="text-white text-lg leading-relaxed">
            {transcription}
          </div>
        ) : (
          <div className="text-white/50 text-center italic">
            Your speech will appear here...
          </div>
        )}
      </div>
      
      {transcription && !isLoading && (
        <div className="mt-3 text-right">
          <span className="text-white/40 text-sm">
            {transcription.split(' ').length} words
          </span>
        </div>
      )}
    </div>
  )
}

export default TranscriptionDisplay
