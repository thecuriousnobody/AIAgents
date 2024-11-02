# config/audio_config.py

class AudioConfig:
    # Default audio settings
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_CHUNK_SIZE = 1024
    DEFAULT_ENERGY_THRESHOLD = 4000
    
    # Microphone configuration
    MIC_SETTINGS = {
        'adjust_ambient_duration': 2,
        'dynamic_energy_threshold': True,
        'pause_threshold': 0.8,
        'phrase_threshold': 0.3,
        'non_speaking_duration': 0.5
    }
    
    # Device selection
    PREFERRED_MIC_KEYWORDS = [
        'podcast',
        'yeti',
        'audio-technica',
        'rode',
        'shure'
    ]
    
    # Audio processing
    NOISE_REDUCTION = {
        'enabled': True,
        'reduction_strength': 0.15
    }
    
    # Voice activity detection
    VAD_CONFIG = {
        'silence_threshold': -35,  # dB
        'silence_duration': 0.5,   # seconds
        'speech_threshold': -25    # dB
    }