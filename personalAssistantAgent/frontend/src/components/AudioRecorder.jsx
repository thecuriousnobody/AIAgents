import React, { useState, useRef, useEffect } from 'react'
import { Mic, MicOff } from 'lucide-react'

const AudioRecorder = ({ 
  isRecording, 
  onRecordingChange, 
  onAudioRecorded, 
  onAudioLevels, 
  disabled = false 
}) => {
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [audioStream, setAudioStream] = useState(null)
  const [audioChunks, setAudioChunks] = useState([])
  const [permissionGranted, setPermissionGranted] = useState(false)
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)
  const animationFrameRef = useRef(null)

  // Initialize audio permissions on mount
  useEffect(() => {
    checkAudioPermissions()
    return () => {
      cleanup()
    }
  }, [])

  // Check audio permissions
  const checkAudioPermissions = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true })
      setPermissionGranted(true)
    } catch (err) {
      console.error('Microphone permission denied:', err)
      setPermissionGranted(false)
    }
  }

  // Cleanup function
  const cleanup = () => {
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop())
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
    }
  }

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })
      
      setAudioStream(stream)
      
      // Set up MediaRecorder
      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      const chunks = []
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data)
        }
      }
      
      recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' })
        onAudioRecorded(audioBlob)
        setAudioChunks([])
      }
      
      recorder.start()
      setMediaRecorder(recorder)
      setAudioChunks(chunks)
      onRecordingChange(true)
      
      // Set up audio visualization
      setupAudioVisualization(stream)
      
    } catch (err) {
      console.error('Failed to start recording:', err)
      alert('Failed to access microphone. Please check permissions.')
    }
  }

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
      setMediaRecorder(null)
    }
    
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop())
      setAudioStream(null)
    }
    
    onRecordingChange(false)
    
    // Stop visualization
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
    }
  }

  // Set up audio visualization
  const setupAudioVisualization = (stream) => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const analyser = audioContext.createAnalyser()
      const source = audioContext.createMediaStreamSource(stream)
      
      analyser.fftSize = 256
      source.connect(analyser)
      
      audioContextRef.current = audioContext
      analyserRef.current = analyser
      
      visualizeAudio()
    } catch (err) {
      console.error('Audio visualization setup failed:', err)
    }
  }

  // Visualize audio levels
  const visualizeAudio = () => {
    if (!analyserRef.current) return
    
    const bufferLength = analyserRef.current.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    
    const updateLevels = () => {
      if (!isRecording) return
      
      analyserRef.current.getByteFrequencyData(dataArray)
      
      // Generate levels for visualization (simplified)
      const levels = []
      const step = Math.floor(bufferLength / 30) // 30 bars
      
      for (let i = 0; i < 30; i++) {
        const start = i * step
        const end = start + step
        const slice = dataArray.slice(start, end)
        const average = slice.reduce((sum, val) => sum + val, 0) / slice.length
        levels.push(Math.max(10, average / 2)) // Minimum height of 10
      }
      
      onAudioLevels(levels)
      animationFrameRef.current = requestAnimationFrame(updateLevels)
    }
    
    updateLevels()
  }

  // Handle button click
  const handleClick = () => {
    if (disabled) return
    
    if (!permissionGranted) {
      checkAudioPermissions()
      return
    }
    
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  return (
    <div className="flex flex-col items-center space-y-4">
      <button
        onClick={handleClick}
        disabled={disabled}
        className={`mic-button ${isRecording ? 'recording' : ''} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        title={isRecording ? 'Stop recording' : 'Start recording'}
      >
        {isRecording ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
      </button>
      
      {!permissionGranted && (
        <p className="text-white/70 text-sm text-center">
          Microphone access required. Click to grant permission.
        </p>
      )}
    </div>
  )
}

export default AudioRecorder
