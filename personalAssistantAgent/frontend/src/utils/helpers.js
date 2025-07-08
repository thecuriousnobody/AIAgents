// Generate a unique session ID
export const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Format timestamp for display
export const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

// Debounce function for performance
export const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Check if browser supports required features
export const checkBrowserSupport = () => {
  const requirements = {
    mediaRecorder: typeof MediaRecorder !== 'undefined',
    getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
    webAudio: typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined'
  }
  
  const allSupported = Object.values(requirements).every(Boolean)
  
  return {
    supported: allSupported,
    requirements
  }
}

// Audio format utilities
export const convertBlobToArrayBuffer = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsArrayBuffer(blob)
  })
}
