"""
Coordinator Agent
Synthesizes multi-agent outputs and makes final decisions
Respects ethics agent veto power
"""

from typing import List, Dict
from agents.financial_agent import FinancialAgent
from agents.academic_agent import AcademicAgent
from agents.residential_agent import ResidentialAgent
from agents.language_agent import LanguageAgent
from agents.uncertainty_agent import UncertaintyAgent
from agents.ethics_agent import EthicsAgent
from models import StudentEvent


class CoordinatorAgent:
    """
    Coordinates multi-agent analysis and makes final decisions
    
    Decision hierarchy:
    1. Ethics agent has VETO power
    2. Uncertainty agent influences confidence
    3. Domain agents contribute weighted risk scores
    4. Final decision balances all inputs
    
    Possible decisions:
    - NO_ACTION: Explicit decision to not intervene
    - WATCH: Continue monitoring without intervention
    - SOFT_OUTREACH: Gentle, consent-based check-in
    - ESCALATE_TO_HUMAN: Human counselor required
    """
    
    def __init__(self):
        self.name = "CoordinatorAgent"
        
        # Initialize all domain agents
        self.financial_agent = FinancialAgent()
        self.academic_agent = AcademicAgent()
        self.residential_agent = ResidentialAgent()
        self.language_agent = LanguageAgent()
        self.uncertainty_agent = UncertaintyAgent()
        self.ethics_agent = EthicsAgent()
    
    def analyze_student(self, events: List[StudentEvent], student_context: Dict = None) -> Dict:
        """
        Perform complete multi-agent analysis of student trajectory
        
        Returns:
            dict: {
                'decision': str,
                'justification': str,
                'aggregate_risk': float,
                'uncertainty_level': float,
                'ethics_veto': bool,
                'agent_outputs': List[Dict],
                'minority_opinions': List[Dict]
            }
        """
        # Step 1: Run all domain agents
        agent_outputs = []
        
        financial_output = self.financial_agent.evaluate(events)
        agent_outputs.append(financial_output)
        
        academic_output = self.academic_agent.evaluate(events)
        agent_outputs.append(academic_output)
        
        residential_output = self.residential_agent.evaluate(events)
        agent_outputs.append(residential_output)
        
        language_output = self.language_agent.evaluate(events)
        agent_outputs.append(language_output)
        
        # Step 2: Run uncertainty agent with other outputs
        uncertainty_output = self.uncertainty_agent.evaluate(events, agent_outputs)
        agent_outputs.append(uncertainty_output)
        
        # Step 3: Run ethics agent (has veto power)
        ethics_output = self.ethics_agent.evaluate(agent_outputs, student_context)
        agent_outputs.append(ethics_output)
        
        # Step 4: Check for ethics veto
        if ethics_output.get('veto', False):
            return {
                'decision': ethics_output['recommendation'],
                'justification': ethics_output['comment'],
                'aggregate_risk': ethics_output.get('risk', 0.0),
                'uncertainty_level': uncertainty_output.get('risk', 0.0),
                'ethics_veto': True,
                'veto_reasons': ethics_output.get('veto_reasons', []),
                'agent_outputs': agent_outputs,
                'minority_opinions': self._identify_minority_opinions(agent_outputs)
            }
        
        # Step 5: Calculate aggregate risk (weighted average)
        aggregate_risk = self._calculate_aggregate_risk(agent_outputs)
        
        # Step 6: Make final decision based on aggregate risk and uncertainty
        decision = self._make_decision(
            aggregate_risk, 
            uncertainty_output.get('risk', 0.0),
            agent_outputs
        )
        
        justification = self._generate_justification(decision, aggregate_risk, agent_outputs)
        
        return {
            'decision': decision,
            'justification': justification,
            'aggregate_risk': round(aggregate_risk, 3),
            'uncertainty_level': round(uncertainty_output.get('risk', 0.0), 3),
            'ethics_veto': False,
            'veto_reasons': [],
            'agent_outputs': agent_outputs,
            'minority_opinions': self._identify_minority_opinions(agent_outputs)
        }
    
    def _calculate_aggregate_risk(self, agent_outputs: List[Dict]) -> float:
        """
        Calculate weighted aggregate risk from domain agents
        Excludes uncertainty and ethics agents
        """
        weights = {
            'FinancialAgent': 0.25,
            'AcademicAgent': 0.20,
            'ResidentialAgent': 0.20,
            'LanguageAgent': 0.15,
            'UncertaintyAgent': 0.20  # Uncertainty as a risk factor
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for output in agent_outputs:
            agent_name = output['agent']
            if agent_name in weights:
                risk = output.get('risk', 0.0)
                confidence = output.get('confidence', 0.5)
                
                # Weight by both assigned weight and agent confidence
                effective_weight = weights[agent_name] * confidence
                weighted_sum += risk * effective_weight
                total_weight += effective_weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def _make_decision(self, aggregate_risk: float, uncertainty: float, agent_outputs: List[Dict]) -> str:
        """
        Make final decision based on risk and uncertainty
        
        Decision thresholds (conservative):
        - aggregate_risk > 0.65: ESCALATE_TO_HUMAN
        - aggregate_risk > 0.45: SOFT_OUTREACH
        - aggregate_risk > 0.25: WATCH
        - aggregate_risk <= 0.25: NO_ACTION
        
        High uncertainty lowers thresholds (more conservative)
        """
        # Adjust thresholds based on uncertainty
        if uncertainty > 0.7:
            # High uncertainty -> defer to human at lower risk
            if aggregate_risk > 0.5:
                return "ESCALATE_TO_HUMAN"
            elif aggregate_risk > 0.3:
                return "WATCH"
            else:
                return "NO_ACTION"
        
        # Normal thresholds
        if aggregate_risk > 0.65:
            return "ESCALATE_TO_HUMAN"
        elif aggregate_risk > 0.45:
            return "SOFT_OUTREACH"
        elif aggregate_risk > 0.25:
            return "WATCH"
        else:
            return "NO_ACTION"
    
    def _generate_justification(self, decision: str, aggregate_risk: float, agent_outputs: List[Dict]) -> str:
        """Generate human-readable justification for decision"""
        # Identify contributing factors
        high_risk_agents = [
            o for o in agent_outputs 
            if o.get('risk', 0) > 0.5 and o['agent'] not in ['EthicsAgent', 'UncertaintyAgent']
        ]
        
        if decision == "NO_ACTION":
            return f"No intervention warranted (aggregate risk: {aggregate_risk:.2f})"
        
        elif decision == "WATCH":
            if high_risk_agents:
                agent_names = [a['agent'].replace('Agent', '') for a in high_risk_agents]
                return f"Monitor situation - elevated {', '.join(agent_names)} friction (risk: {aggregate_risk:.2f})"
            return f"Low-moderate friction detected (risk: {aggregate_risk:.2f}) - watchful waiting"
        
        elif decision == "SOFT_OUTREACH":
            agent_names = [a['agent'].replace('Agent', '') for a in high_risk_agents]
            return f"Suggest gentle check-in - notable {', '.join(agent_names)} barriers (risk: {aggregate_risk:.2f})"
        
        elif decision == "ESCALATE_TO_HUMAN":
            agent_names = [a['agent'].replace('Agent', '') for a in high_risk_agents]
            return f"Human counselor recommended - significant {', '.join(agent_names)} friction (risk: {aggregate_risk:.2f})"
        
        return f"Decision: {decision} (risk: {aggregate_risk:.2f})"
    
    def _identify_minority_opinions(self, agent_outputs: List[Dict]) -> List[Dict]:
        """
        Identify agents whose risk assessments significantly differ from consensus
        Preserves dissenting views
        """
        domain_outputs = [
            o for o in agent_outputs 
            if o['agent'] not in ['EthicsAgent', 'UncertaintyAgent']
        ]
        
        if len(domain_outputs) < 3:
            return []
        
        risks = [o.get('risk', 0.0) for o in domain_outputs]
        mean_risk = sum(risks) / len(risks)
        
        minority = []
        for output in domain_outputs:
            risk_diff = abs(output.get('risk', 0.0) - mean_risk)
            if risk_diff > 0.3:  # Significantly different from mean
                minority.append({
                    'agent': output['agent'],
                    'risk': output.get('risk', 0.0),
                    'comment': output.get('comment', ''),
                    'deviation': round(risk_diff, 3)
                })
        
        return minority