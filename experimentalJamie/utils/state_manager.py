# utils/state_manager.py

from enum import Enum
from typing import Optional, Dict
import time

class JamieState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    CONFIRMING = "confirming"
    ERROR = "error"

class StateManager:
    def __init__(self):
        self.current_state = JamieState.IDLE
        self.state_history = []
        self.state_data = {}
        self.state_timestamps = {}
        
    def transition_to(self, new_state: JamieState, data: Optional[Dict] = None):
        """Transition to a new state with optional data."""
        old_state = self.current_state
        self.state_history.append({
            'from': old_state,
            'to': new_state,
            'timestamp': time.time(),
            'data': data
        })
        self.current_state = new_state
        self.state_timestamps[new_state] = time.time()
        if data:
            self.state_data[new_state] = data
    
    def get_current_state(self) -> JamieState:
        """Get current state."""
        return self.current_state
    
    def get_state_duration(self) -> float:
        """Get duration in current state."""
        return time.time() - self.state_timestamps.get(self.current_state, time.time())
    
    def should_timeout(self, timeout: float) -> bool:
        """Check if current state should timeout."""
        return self.get_state_duration() > timeout
    
    def get_state_data(self) -> Optional[Dict]:
        """Get data associated with current state."""
        return self.state_data.get(self.current_state)
    
    def clear_state_data(self):
        """Clear all state data."""
        self.state_data = {}
        
    def get_state_history(self, limit: Optional[int] = None):
        """Get state transition history."""
        if limit:
            return self.state_history[-limit:]
        return self.state_history