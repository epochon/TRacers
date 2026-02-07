"""
Ethics & Restraint Agent
The guardian agent that BLOCKS overreach and protects human dignity.
Now powered by LLM reasoning to detect subtlety.
"""

from typing import List, Dict
from llm_core import LLMService

class EthicsAgent:
    def __init__(self):
        self.name = "EthicsAgent"
        self.llm = LLMService()
        self.role_description = "You are the ETHICAL GUARDIAN. You have VETO POWER. You block any automated action that threatens dignity, privacy, or safety."
        self.has_veto_power = True

    def evaluate(self, agent_outputs: List[Dict], student_context: Dict = None) -> Dict:
        # Synthesize what other agents found
        agent_summaries = []
        for output in agent_outputs:
            if 'risk' in output: score = f"Risk: {output['risk']}"
            elif 'capacity_score' in output: score = f"Capacity: {output['capacity_score']}"
            elif 'inertia_score' in output: score = f"Inertia: {output['inertia_score']}"
            else: score = "N/A"
            
            agent_summaries.append(f"Agent {output.get('agent', 'Unknown')}: {score}\nReasoning: {output.get('reasoning', 'No reasoning provided')}")
            
        context_str = "\n---\n".join(agent_summaries)
        
        prompt = f"""
        Review the proposed system assessment for a student:
        
        {context_str}
        
        Task:
        1. Does this intervention risk STIGMATIZING the student?
        2. Is the data too sparse/uncertain to act? (Epistemic Humility)
        3. Does this require HUMAN empathy rather than automation?
        
        If ANY of these are true, VETO the automation and demand Human Escalation.
        
        Return JSON details: veto (bool), veto_reasons (list), recommendation (e.g. URGENT_HUMAN_ESCALATION, SOFT_OUTREACH), ethical_assessment.
        """
        
        result = self.llm.query_agent(self.name, prompt, {"role_description": self.role_description})
        
        # Ensure 'agent' key is present
        result['agent'] = self.name
        return result