"""
Friction Accumulation Agent
Tracks the DURATION and STACKING of unresolved bureaucratic issues.
Focuses on "How long has this been stuck?" and "How many issues are piling up?"
"""

from typing import List, Dict
from models import StudentEvent
from llm_core import LLMService

class FrictionAccumulationAgent:
    def __init__(self):
        self.name = "FrictionAccumulationAgent"
        self.llm = LLMService()
        self.role_description = "You track the accumulation of bureaucratic friction. You care about DURATION (how long pending) and STACKING (how many simultaneous issues)."

    def evaluate(self, events: List[StudentEvent]) -> Dict:
        # Convert events to simple readable format for LLM
        event_log = "\n".join([f"- [{e.timestamp}] {e.event_type}: {e.description} (Severity: {e.severity})" for e in events])
        
        prompt = f"""
        Analyze these student events for FRICTION ACCUMULATION.
        
        Events:
        {event_log}
        
        Task:
        1. Identify issues that are UNRESOLVED or PENDING for a long time.
        2. Count how many distinct bureaucratic failure types are active.
        3. Determine if the friction is "Compounding" (getting worse).
        
        Return JSON details: risk (0-1), confidence, reasoning, key_signals, duration_days.
        """
        
        return self.llm.query_agent(self.name, prompt, {"role_description": self.role_description})
