# config/command_config.py

class CommandConfig:
    # Wake word configuration
    WAKE_WORDS = {
        'primary': 'jamie',
        'alternates': ['jay', 'james', 'jimmy']
    }
    
    # Command confirmation phrases
    CONFIRMATION_PHRASES = {
        'standard': [
            'look this up',
            'search this',
            'find this',
            'get this'
        ],
        'casual': [
            'go ahead',
            'yes please',
            'thanks',
            'okay',
            'yep',
            'yeah'
        ],
        'task_specific': [
            'search now',
            'pull it up',
            'check this out'
        ]
    }
    
    # Command cancellation phrases
    CANCELLATION_PHRASES = [
        'cancel that',
        'never mind',
        'stop',
        'wait'
    ]
    
    # Context retention settings
    CONTEXT_SETTINGS = {
        'max_history': 5,        # Number of previous commands to remember
        'context_timeout': 300,  # Seconds before context is cleared
        'chain_commands': True   # Allow follow-up commands
    }
    
    # Command modes
    SEARCH_MODES = {
        'quick': {
            'depth': 'surface',
            'max_sources': 3,
            'timeout': 10
        },
        'detailed': {
            'depth': 'comprehensive',
            'max_sources': 10,
            'timeout': 30
        },
        'academic': {
            'depth': 'scholarly',
            'max_sources': 5,
            'timeout': 20
        }
    }