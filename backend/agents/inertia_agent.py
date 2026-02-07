"""
Institutional Inertia Agent
Models how SLOW the system is.
Asks: "Even if we act today, will it matter in time?"
"""

from typing import List, Dict
from models import StudentEvent
from llm_core import LLMService

class InstitutionalInertiaAgent:
    def __init__(self):
        self.name = "InstitutionalInertiaAgent"
        self.llm = LLMService()
        self.role_description = "You are the cynic. You know the bureaucracy is slow. You measure SYSTEM LATENCY and BACKLOG."

    def evaluate(self, events: List[StudentEvent]) -> Dict:
        # In a real app, this agent would check Admin Queues/Backlogs.
        # Here, we infer inertia from the history of delays in the events.
        event_log = "\n".join([f"- [{e.timestamp}] {e.event_type}: {e.description}" for e in events])
        
        prompt = f"""
        Analyze the SYSTEM INERTIA (Slowness) demonstrated in these events.
        
        Events:
        {event_log}
        
        Task:
        1. How long does the system typically take to resolve these types of issues?
        2. Is the "Administrative Backlog" likely high?
        3. Compare System Speed vs Student Needs.
        
        Return JSON details: inertia_score (0=fast, 1=frozen), confidence, reasoning, estimated_resolution_days.
        """
        
        return self.llm.query_agent(self.name, prompt, {"role_description": self.role_description})
