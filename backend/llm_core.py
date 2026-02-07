"""
LLM Core Service for TRACEPOINT
Handles communication with LLM Providers (OpenAI/Gemini/Anthropic)
Includes a MOCK mode for demonstration without API keys.
"""

import json
import os
import random
from typing import Dict, Any, List

# Simulating an LLM response for the Hackathon Demo
class MockLLM:
    @staticmethod
    def generate(prompt: str, system_prompt: str = "") -> str:
        """
        Simulate intelligent agent responses based on keywords in the prompt.
        This allows the system to be 'demonstrable' out of the box.
        """
        # 1. FRICTION AGENT SIMULATION
        if "FrictionAccumulationAgent" in system_prompt:
            return json.dumps({
                "risk": 0.85,
                "confidence": 0.9,
                "reasoning": "Detected stacking of 3 distinct bureaucratic failures over 45 days. Scholarship delay (critical) is compounded by Hostel uncertainty.",
                "key_signals": ["Scholarship pending > 45 days", "Hostel allocation unresolved", "Multiple department failures"],
                "duration_days": 45,
                "is_stuck": True
            })

        # 2. RECOVERY AGENT SIMULATION
        if "RecoveryCapacityAgent" in system_prompt:
            return json.dumps({
                "capacity_score": 0.3, # Low capacity
                "confidence": 0.85,
                "reasoning": "Student resilience is depleted. Financial buffer is likely exhausted due to scholarship delay. Time window to fix hostel issue is < 7 days before semester starts.",
                "remaining_buffer": "Critical (< 1 week)",
                "support_access": "Low"
            })

        # 3. INERTIA AGENT SIMULATION
        if "InstitutionalInertiaAgent" in system_prompt:
            return json.dumps({
                "inertia_score": 0.9, # High inertia (very slow)
                "confidence": 0.95,
                "reasoning": "Administrative backlog is high. Average resolution time for Hostel issues is 14 days, but student needs it in 7. System is too slow to save this trajectory naturally.",
                "estimated_resolution_days": 14,
                "system_load": "High"
            })
            
        # 4. ETHICS AGENT SIMULATION
        if "EthicsAgent" in system_prompt:
             return json.dumps({
                "veto": False,
                "veto_reasons": [],
                "recommendation": "URGENT_HUMAN_ESCALATION",
                "ethical_assessment": "High risk of irreversible harm. Automated intervention is insufficient and potentially stigmatizing. Human advocate required immediately to bypass bureaucracy.",
                "dignity_check": "Passed"
            })

        # 5. IRREVERSIBILITY ARBITER (META AGENT)
        if "IrreversibilityArbiter" in system_prompt:
            return json.dumps({
                "posture": "URGENT_HUMAN_ESCALATION",
                "distance_to_irreversibility": 15, # 15% remaining (very close to Point of No Return)
                "headline": "Irreversibility Imminent (~5 days)",
                "synthesis": "The system is moving too slowly (14 days) to solve the problem before the student crashes (7 days). Recovery capacity is critical. Intervention required immediately.",
                "debate_summary": "Inertia Agent argues resolution is impossible in time. Recovery Agent confirms student cannot wait. Friction Agent notes compounding stress.",
                "point_of_no_return_days": 5
            })

        return json.dumps({"error": "Unknown agent context"})

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.provider = "mock" if not self.api_key else "openai" # Default to Mock if no key
        
    def query_agent(self, agent_name: str, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generic method to query an agent.
        """
        system_prompt = f"You are the {agent_name} in the TRACEPOINT system. {context.get('role_description', '')}"
        
        # If no API key, use Mock
        if self.provider == "mock":
            response_json = MockLLM.generate(prompt, system_prompt)
            return json.loads(response_json)
            
        # TODO: Implement real OpenAI/Gemini call here
        # return self._call_openai(system_prompt, prompt)
        return {"error": "Real LLM not implemented yet"}

