# utils/context_manager.py

from collections import deque
from typing import Dict, List, Optional
import time
import json

class ContextManager:
    def __init__(self, config):
        self.config = config
        self.command_history = deque(maxlen=config.CONTEXT_SETTINGS['max_history'])
        self.current_context = {}
        self.last_command_time = 0
        
    def add_command(self, command: str, results: Dict):
        """Add a command and its results to history."""
        self.command_history.append({
            'command': command,
            'results': results,
            'timestamp': time.time()
        })
        self.last_command_time = time.time()
        
    def get_recent_context(self) -> List[Dict]:
        """Get recent commands within context timeout."""
        current_time = time.time()
        timeout = self.config.CONTEXT_SETTINGS['context_timeout']
        
        return [
            cmd for cmd in self.command_history
            if current_time - cmd['timestamp'] < timeout
        ]
    
    def should_chain_command(self, command: str) -> bool:
        """Determine if command should be chained with previous context."""
        chain_indicators = ['and', 'also', 'additionally', 'then', 'next']
        return (
            self.config.CONTEXT_SETTINGS['chain_commands'] and
            any(indicator in command.lower() for indicator in chain_indicators)
        )
    
    def get_search_mode(self, command: str) -> Dict:
        """Determine appropriate search mode based on command."""
        if any(word in command.lower() for word in ['quick', 'fast', 'brief']):
            return self.config.SEARCH_MODES['quick']
        elif any(word in command.lower() for word in ['detailed', 'comprehensive', 'full']):
            return self.config.SEARCH_MODES['detailed']
        elif any(word in command.lower() for word in ['academic', 'scholarly', 'research']):
            return self.config.SEARCH_MODES['academic']
        return self.config.SEARCH_MODES['quick']  # Default to quick mode
    
    def save_context(self, filepath: str):
        """Save current context to file."""
        context_data = {
            'command_history': list(self.command_history),
            'current_context': self.current_context,
            'last_command_time': self.last_command_time
        }
        with open(filepath, 'w') as f:
            json.dump(context_data, f)
    
    def load_context(self, filepath: str):
        """Load context from file."""
        try:
            with open(filepath, 'r') as f:
                context_data = json.load(f)
                self.command_history = deque(context_data['command_history'], 
                                          maxlen=self.config.CONTEXT_SETTINGS['max_history'])
                self.current_context = context_data['current_context']
                self.last_command_time = context_data['last_command_time']
        except FileNotFoundError:
            print("No previous context found.")