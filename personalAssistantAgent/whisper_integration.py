#!/usr/bin/env python3
"""
Whisper Integration for Personal Assistant
=========================================

Local Whisper integration for speech-to-text conversion.
Supports both real-time streaming and batch processing.
"""

import whisper
import numpy as np
import torch
import tempfile
import os
from typing import Optional, Dict, Any, Callable
import threading
import time
import queue
from datetime import datetime

class WhisperTranscriber:
    """Local Whisper transcriber for speech-to-text conversion"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper transcriber
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
                       - tiny: ~39MB, fastest, least accurate
                       - base: ~74MB, good balance (recommended for prototyping)
                       - small: ~244MB, better accuracy
                       - medium: ~769MB, very good accuracy
                       - large: ~1550MB, best accuracy
        """
        self.model_size = model_size
        self.model = None
        self.is_loaded = False
        self.transcription_queue = queue.Queue()
        
    def load_model(self) -> bool:
        """Load the Whisper model"""
        try:
            print(f"🔄 Loading Whisper {self.model_size} model...")
            self.model = whisper.load_model(self.model_size)
            self.is_loaded = True
            print(f"✅ Whisper {self.model_size} model loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            return False
    
    def transcribe_audio_file(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe an audio file
        
        Args:
            audio_file_path: Path to the audio file
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Dictionary with transcription results
        """
        if not self.is_loaded:
            if not self.load_model():
                return {"error": "Failed to load Whisper model"}
        
        try:
            print(f"🔄 Transcribing audio file: {audio_file_path}")
            
            # Transcribe the audio
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                verbose=False
            )
            
            transcription_result = {
                "text": result["text"].strip(),
                "language": result["language"],
                "segments": result["segments"],
                "timestamp": datetime.now().isoformat(),
                "confidence": self._calculate_confidence(result["segments"]),
                "duration": result.get("duration", 0)
            }
            
            print(f"✅ Transcription complete: '{transcription_result['text'][:100]}...'")
            return transcription_result
            
        except Exception as e:
            print(f"❌ Error transcribing audio: {e}")
            return {"error": str(e)}
    
    def transcribe_audio_data(self, audio_data: np.ndarray, sample_rate: int = 16000, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio data directly from numpy array
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            language: Language code
            
        Returns:
            Dictionary with transcription results
        """
        if not self.is_loaded:
            if not self.load_model():
                return {"error": "Failed to load Whisper model"}
        
        try:
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Save audio data to temporary file
                import soundfile as sf
                sf.write(temp_path, audio_data, sample_rate)
                
                # Transcribe the temporary file
                result = self.transcribe_audio_file(temp_path, language)
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                return result
                
        except Exception as e:
            print(f"❌ Error transcribing audio data: {e}")
            return {"error": str(e)}
    
    def _calculate_confidence(self, segments: list) -> float:
        """Calculate average confidence score from segments"""
        if not segments:
            return 0.0
        
        # Whisper doesn't provide confidence scores directly,
        # so we'll estimate based on segment consistency
        total_duration = sum(seg.get("end", 0) - seg.get("start", 0) for seg in segments)
        if total_duration == 0:
            return 0.8  # Default confidence
        
        # Simple heuristic: longer segments tend to be more confident
        avg_segment_length = total_duration / len(segments)
        confidence = min(0.5 + (avg_segment_length * 0.1), 1.0)
        return round(confidence, 2)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "is_loaded": self.is_loaded,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "model_path": getattr(self.model, 'model_path', None) if self.model else None
        }

def test_whisper_installation():
    """Test Whisper installation and basic functionality"""
    print("🧪 Testing Whisper installation...")
    
    # Test model loading
    try:
        transcriber = WhisperTranscriber("base")
        if transcriber.load_model():
            print("✅ Whisper model loaded successfully")
            print(f"Model info: {transcriber.get_model_info()}")
            return True
        else:
            print("❌ Failed to load Whisper model")
            return False
    except Exception as e:
        print(f"❌ Error testing Whisper: {e}")
        return False

if __name__ == "__main__":
    # Test the installation
    if test_whisper_installation():
        print("\n✅ Whisper integration ready!")
    else:
        print("\n❌ Whisper integration failed.")
