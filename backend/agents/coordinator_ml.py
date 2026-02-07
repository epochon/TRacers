"""
ML-Powered Coordinator Agent
Orchestrates multi-agent system with ML models
"""

from typing import List, Dict
from models import StudentEvent
from agents.financial_agent_ml import FinancialAgentML
from agents.academic_agent_ml import AcademicAgentML
from agents.residential_agent_ml import ResidentialAgentML
from agents.language_agent_ml import LanguageAgentML
from utils.llm import get_llm


class CoordinatorAgentML:
    """
    Coordinator that uses ML-powered agents for risk assessment.
    """
    
    def __init__(self):
        self.name = "CoordinatorML"
        
        # Initialize ML agents
        self.financial_agent = FinancialAgentML()
        self.academic_agent = AcademicAgentML()
        self.residential_agent = ResidentialAgentML()
        self.language_agent = LanguageAgentML()
        
        # LLM for synthesis
        self.llm = get_llm()
        
        # Decision thresholds
        self.threshold_escalate = 0.7
        self.threshold_soft = 0.5
        self.threshold_watch = 0.3
    
    def evaluate(self, events: List[StudentEvent]) -> Dict:
        """
        Evaluate student risk using all ML agents.
        
        Args:
            events: List of student events
            
        Returns:
            Comprehensive risk assessment with agent breakdown
        """
        if not events:
            return {
                'final_risk': 0.0,
                'decision': 'NO_ACTION',
                'confidence': 1.0,
                'justification': 'No events detected',
                'agent_outputs': []
            }
        
        # Run all agents
        agent_outputs = []
        
        financial_result = self.financial_agent.evaluate(events)
        agent_outputs.append(financial_result)
        
        academic_result = self.academic_agent.evaluate(events)
        agent_outputs.append(academic_result)
        
        residential_result = self.residential_agent.evaluate(events)
        agent_outputs.append(residential_result)
        
        language_result = self.language_agent.evaluate(events)
        agent_outputs.append(language_result)
        
        # Weighted risk aggregation
        total_weight = (
            self.financial_agent.weight +
            self.academic_agent.weight +
            self.residential_agent.weight +
            self.language_agent.weight
        )
        
        weighted_risk = (
            financial_result['risk'] * self.financial_agent.weight +
            academic_result['risk'] * self.academic_agent.weight +
            residential_result['risk'] * self.residential_agent.weight +
            language_result['risk'] * self.language_agent.weight
        ) / total_weight
        
        # Average confidence
        avg_confidence = sum(a['confidence'] for a in agent_outputs) / len(agent_outputs)
        
        # Make decision
        if weighted_risk >= self.threshold_escalate:
            decision = 'ESCALATE_TO_HUMAN'
            posture = 'URGENT_HUMAN_ESCALATION'
        elif weighted_risk >= self.threshold_soft:
            decision = 'SOFT_OUTREACH'
            posture = 'SOFT_OUTREACH'
        elif weighted_risk >= self.threshold_watch:
            decision = 'WATCH'
            posture = 'OBSERVE'
        else:
            decision = 'NO_ACTION'
            posture = 'OBSERVE'
        
        # Generate synthesis using LLM
        synthesis_prompt = f"""Synthesize the following agent assessments:

Financial: Risk={financial_result['risk']:.2f}, {financial_result['comment'][:100]}
Academic: Risk={academic_result['risk']:.2f}, {academic_result['comment'][:100]}
Residential: Risk={residential_result['risk']:.2f}, {residential_result['comment'][:100]}
Language: Risk={language_result['risk']:.2f}, {language_result['comment'][:100]}

Overall Risk: {weighted_risk:.2f}
Decision: {decision}

Provide a 2-3 sentence synthesis explaining the overall situation and recommended action."""

        justification = self.llm.generate(synthesis_prompt, max_new_tokens=100, temperature=0.5)
        
        # Calculate distance to irreversibility (inverse of risk) - stay as float 0-1
        distance_to_irreversibility = 1.0 - weighted_risk
        
        # Generate headline
        if weighted_risk >= 0.8:
            headline = "Critical Intervention Needed"
        elif weighted_risk >= 0.6:
            headline = "Significant Friction Detected"
        elif weighted_risk >= 0.4:
            headline = "Moderate Concerns Present"
        else:
            headline = "Status Nominal"
        
        return {
            'final_risk': round(weighted_risk, 3),
            'decision': decision,
            'posture': posture,
            'confidence': round(avg_confidence, 3),
            'justification': justification,
            'agent_outputs': agent_outputs,
            'distance_to_irreversibility': distance_to_irreversibility,
            'headline': headline,
            'meta_data': {
                'distance_to_irreversibility': distance_to_irreversibility,
                'headline': headline,
                'agent_count': len(agent_outputs),
                'ml_powered': True
            }
        }
    
    def train_all_agents(self, training_data: List[Dict]):
        """
        Train all ML agents.
        
        Args:
            training_data: List of dicts with 'events' and 'label' keys
        """
        import numpy as np
        from agents.features import extract_domain_features
        
        # Prepare training data for each agent
        financial_X, financial_y = [], []
        academic_X, academic_y = [], []
        residential_X, residential_y = [], []
        language_X, language_y = [], []
        
        for sample in training_data:
            events = sample['events']
            label = 1 if sample['label'] else 0
            
            # Extract features for each domain
            financial_features = extract_domain_features(events, self.financial_agent.domain_types)
            academic_features = extract_domain_features(events, self.academic_agent.domain_types)
            residential_features = extract_domain_features(events, self.residential_agent.domain_types)
            language_features = extract_domain_features(events, self.language_agent.domain_types)
            
            financial_X.append(financial_features)
            financial_y.append(label)
            
            academic_X.append(academic_features)
            academic_y.append(label)
            
            residential_X.append(residential_features)
            residential_y.append(label)
            
            language_X.append(language_features)
            language_y.append(label)
        
        # Train each agent
        self.financial_agent.train(np.array(financial_X), np.array(financial_y))
        self.financial_agent.save_model()
        
        self.academic_agent.train(np.array(academic_X), np.array(academic_y))
        self.academic_agent.save_model()
        
        self.residential_agent.train(np.array(residential_X), np.array(residential_y))
        self.residential_agent.save_model()
        
        self.language_agent.train(np.array(language_X), np.array(language_y))
        self.language_agent.save_model()
        
        print(f"{self.name}: All agents trained and saved")
