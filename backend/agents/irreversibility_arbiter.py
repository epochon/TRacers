"""
Irreversibility Arbiter (Meta-Agent)
Replaces the old CoordinatorAgent.
Synthesizes the Agent Debate and calculates:
1. Distance-to-Irreversibility (0-100%)
2. Final Posture (Observe, Soft Outreach, Urgent Human Escalation)
"""

from typing import List, Dict
from models import StudentEvent
from agents.friction_agent import FrictionAccumulationAgent
from agents.recovery_agent import RecoveryCapacityAgent
from agents.inertia_agent import InstitutionalInertiaAgent
from agents.ethics_agent import EthicsAgent
from llm_core import LLMService

class IrreversibilityArbiter:
    def __init__(self):
        self.name = "IrreversibilityArbiter"
        self.llm = LLMService()
        self.role_description = "You are the FINAL DECISION MAKER. You synthesize the debate between agents. Your goal is to estimate the POINT OF NO RETURN."
        
        # Initialize sub-agents
        self.friction_agent = FrictionAccumulationAgent()
        self.recovery_agent = RecoveryCapacityAgent()
        self.inertia_agent = InstitutionalInertiaAgent()
        self.ethics_agent = EthicsAgent()

    def analyze_student(self, events: List[StudentEvent], student_context: Dict = None) -> Dict:
        """
        Orchestrate the multi-agent debate and synthesize the result.
        """
        agent_outputs = []
        
        # 1. Run Domain Agents
        friction_output = self.friction_agent.evaluate(events)
        friction_output['agent'] = self.friction_agent.name # Ensure name involved
        agent_outputs.append(friction_output)
        
        recovery_output = self.recovery_agent.evaluate(events)
        recovery_output['agent'] = self.recovery_agent.name
        agent_outputs.append(recovery_output)
        
        inertia_output = self.inertia_agent.evaluate(events)
        inertia_output['agent'] = self.inertia_agent.name
        agent_outputs.append(inertia_output)
        
        # 2. Run Ethics Agent (Reviewing the others)
        ethics_output = self.ethics_agent.evaluate(agent_outputs, student_context)
        ethics_output['agent'] = self.ethics_agent.name
        agent_outputs.append(ethics_output)
        
        # 3. IF Ethics VETO -> Return Veto Result
        if ethics_output.get('veto', False):
             return {
                'decision': ethics_output['recommendation'],
                'justification': f"ETHICS VETO: {ethics_output.get('ethical_assessment', 'Blocked by ethics agent')}",
                'aggregate_risk': 1.0, # Treat as high priority
                'uncertainty_level': 0.0,
                'ethics_veto': True,
                'veto_reasons': ethics_output.get('veto_reasons', []),
                'agent_outputs': agent_outputs,
                'distance_to_irreversibility': 0, # Imminent
                'headline': "Blocked by Ethics Guardian"
            }
            
        # 4. Synthesize Debate via LLM
        debate_transcript = "\n---\n".join([
            f"Agent {o.get('agent')}: {o.get('reasoning') or o.get('comment') or 'No details'}"
            for o in agent_outputs
        ])
        
        prompt = f"""
        Synthesize this Multi-Agent Debate for a student:
        
        {debate_transcript}
        
        Task:
        1. Calculate "Distance to Irreversibility" (0% = Point of No Return/Dropout, 100% = Safe).
        2. Decide the FINAL POSTURE: [OBSERVE, SOFT_OUTREACH, URGENT_HUMAN_ESCALATION].
        3. Write a 1-sentence HEADLINE for the Dashboard.
        
        Return JSON details: posture, distance_to_irreversibility (0-100), headline, synthesis.
        """
        
        arbiter_result = self.llm.query_agent(self.name, prompt, {"role_description": self.role_description})
        
        # 5. Format for the API/Frontend
        # Map new metrics to old schema where possible for compatibility, or extend schema
        return {
            'decision': arbiter_result.get('posture', "OBSERVE"),
            'justification': arbiter_result.get('synthesis', "Analysis complete."),
            'aggregate_risk': (100 - arbiter_result.get('distance_to_irreversibility', 50)) / 100.0, # Map to risk for DB
            'uncertainty_level': 0.1, # Placeholder
            'ethics_veto': False,
            'veto_reasons': [],
            'agent_outputs': agent_outputs,
            'extra_metrics': {
                 'distance_to_irreversibility': arbiter_result.get('distance_to_irreversibility', 50) / 100.0,
                 'headline': arbiter_result.get('headline', "Status Verified")
            }
        }
