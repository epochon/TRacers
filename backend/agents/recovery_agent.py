"""
Recovery Capacity Agent
Estimates the student's remaining ability to bounce back.
Models financial buffer, time window, and psychological bandwidth.
"""

from typing import List, Dict
from models import StudentEvent
from llm_core import LLMService

class RecoveryCapacityAgent:
    def __init__(self):
        self.name = "RecoveryCapacityAgent"
        self.llm = LLMService()
        self.role_description = "You estimate the student's REMAINING CAPACITY to recover. You look for shrinking time windows and financial/emotional depletion."

    def evaluate(self, events: List[StudentEvent]) -> Dict:
        event_log = "\n".join([f"- [{e.timestamp}] {e.event_type}: {e.description}" for e in events])
        
        prompt = f"""
        Analyze the student's RECOVERY CAPACITY based on these events.
        
        Events:
        {event_log}
        
        Task:
        1. Estmate if they have financial buffer left (e.g. scholarship delays deplete this).
        2. Estimate time remaining before critical deadlines (e.g. semester start).
        3. Rate 'capacity_score' from 1.0 (Full resilient) to 0.0 (Collapsed).
        
        Return JSON details: capacity_score, confidence, reasoning, remaining_buffer.
        """
        
        return self.llm.query_agent(self.name, prompt, {"role_description": self.role_description})
