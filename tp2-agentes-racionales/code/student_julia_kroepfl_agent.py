import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_agent import BaseAgent

class SimpleReflexAgent(BaseAgent):
    """
    Your vacuum cleaner agent implementation.
    """
    
    def __init__(self, server_url="http://localhost:5000", **kwargs):
        super().__init__(server_url, "SimpleReflexAgent", **kwargs)
        # Add your initialization code here
    
    def get_strategy_description(self):
        return "Simple Reflex Agent: Cleans dirt immediately and sweeps the grid in a serpentine pattern. Uses the first column for returning to the top like an escalator."

    def _grid_size(self):
        state = self.get_environment_state()
        grid = state.get("grid", [])
        if not grid:
            return 0, 0
        h = len(grid)
        return h, h


    def think(self):
        if not self.is_connected():
            return False

        p = self.get_perception()
        if not p or p.get("is_finished", False):
            return False

        w, h = self._grid_size()
        x, y = p.get("position", (0, 0))

        if p.get("is_dirty", False):
            self.suck()
            return True
        if x == 0:
            if y > 0:
                self.up(); return True
            else:
                self.right(); return True
        xprime = x - 1
        wprime = w - 1

        if y < h - 1:
            if y % 2 == 0:
                if xprime < wprime - 1:
                    self.right(); return True
                else:
                    # Rand erreicht -> eine Zeile tiefer
                    self.down(); return True
            else:
                if xprime > 0:
                    self.left(); return True
                else:
                    self.down(); return True
        if x > 0:
            self.left(); return True

        return True
