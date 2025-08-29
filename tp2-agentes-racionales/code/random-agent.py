import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_agent import BaseAgent

class RandomAgent(BaseAgent):
    def __init__(self, server_url="http://localhost:5000", **kwargs):
        super().__init__(server_url, "RandomAgent", **kwargs)
    
    def get_strategy_description(self):
        return "Random Agent: Moves randomly and cleans dirt when encountered."
    
    def think(self):
        if not self.is_connected():
            return False
        
        perception = self.get_perception()
        if not perception or perception.get('is_finished', True):
            return False
        
        import random
        if perception.get('is_dirty', False):
            return self.suck()
        else:
            actions = [self.up, self.down, self.left, self.right]
            return random.choice(actions)()