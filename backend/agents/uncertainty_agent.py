"""
Uncertainty Agent
Explicit modeling of data limitations and ambiguity
This agent REDUCES confidence when data is sparse or contradictory
"""

from typing import List, Dict
from models import StudentEvent
from datetime import datetime, timedelta


class UncertaintyAgent:
    """
    Models epistemic uncertainty and data quality
    Critical for responsible AI - acknowledges what we DON'T know
    """
    
    def __init__(self):
        self.name = "UncertaintyAgent"
        self.weight = 0.1
    
    def evaluate(self, events: List[StudentEvent], other_agent_outputs: List[Dict] = None) -> Dict:
        """
        Evaluate uncertainty and data quality
        
        Uncertainty factors:
        - Sparse data (too few events)
        - Stale data (no recent events)
        - Conflicting signals
        - Missing context
        """
        event_count = len(events)
        
        # Calculate various uncertainty factors
        data_sparsity = self._assess_sparsity(event_count)
        temporal_staleness = self._assess_staleness(events)
        signal_conflict = self._assess_conflict(other_agent_outputs) if other_agent_outputs else 0.0
        
        # Overall uncertainty score (0 = certain, 1 = highly uncertain)
        uncertainty = max(data_sparsity, temporal_staleness, signal_conflict)
        
        # Risk in this context means "risk of making wrong decision due to uncertainty"
        risk = uncertainty
        
        # Confidence is inverted - high uncertainty = low confidence
        confidence = 1.0 - uncertainty
        
        comment = self._generate_comment(data_sparsity, temporal_staleness, signal_conflict, uncertainty)
        
        return {
            'agent': self.name,
            'risk': round(risk, 3),
            'confidence': round(confidence, 3),
            'comment': comment,
            'details': {
                'data_sparsity': round(data_sparsity, 3),
                'temporal_staleness': round(temporal_staleness, 3),
                'signal_conflict': round(signal_conflict, 3),
                'overall_uncertainty': round(uncertainty, 3),
                'recommendation': self._get_recommendation(uncertainty)
            },
            'uncertainty_flags': self._get_flags(data_sparsity, temporal_staleness, signal_conflict)
        }
    
    def _assess_sparsity(self, event_count: int) -> float:
        """Assess if we have enough data to make reliable assessments"""
        if event_count == 0:
            return 1.0  # Maximum uncertainty
        elif event_count < 3:
            return 0.8  # Very sparse
        elif event_count < 5:
            return 0.5  # Somewhat sparse
        elif event_count < 8:
            return 0.3  # Acceptable
        else:
            return 0.1  # Good data
    
    def _assess_staleness(self, events: List[StudentEvent]) -> float:
        """Assess if data is recent enough to be reliable"""
        if not events:
            return 1.0
        
        most_recent = max(events, key=lambda x: x.timestamp)
        days_since = (datetime.utcnow() - most_recent.timestamp).days
        
        if days_since > 60:
            return 0.9  # Very stale
        elif days_since > 30:
            return 0.6  # Somewhat stale
        elif days_since > 14:
            return 0.3  # Recent enough
        else:
            return 0.1  # Fresh data
    
    def _assess_conflict(self, agent_outputs: List[Dict]) -> float:
        """Assess if other agents disagree significantly"""
        if not agent_outputs or len(agent_outputs) < 2:
            return 0.0
        
        # Get risk scores from other agents (excluding self and ethics agent)
        risk_scores = [
            output['risk'] for output in agent_outputs 
            if output['agent'] not in ['UncertaintyAgent', 'EthicsAgent']
        ]
        
        if len(risk_scores) < 2:
            return 0.0
        
        # Calculate variance - high variance = conflicting signals
        mean_risk = sum(risk_scores) / len(risk_scores)
        variance = sum((r - mean_risk) ** 2 for r in risk_scores) / len(risk_scores)
        
        # Normalize variance to 0-1 range
        conflict_score = min(variance * 4, 1.0)  # Scale factor of 4
        
        return conflict_score
    
    def _generate_comment(self, sparsity: float, staleness: float, conflict: float, overall: float) -> str:
        """Generate human-readable uncertainty assessment"""
        issues = []
        
        if sparsity > 0.5:
            issues.append("insufficient data")
        if staleness > 0.5:
            issues.append("stale information")
        if conflict > 0.4:
            issues.append("conflicting agent signals")
        
        if not issues:
            return "Good data quality - confident assessment possible"
        
        if overall > 0.7:
            return f"HIGH UNCERTAINTY: {', '.join(issues)} - recommend caution"
        elif overall > 0.5:
            return f"Moderate uncertainty: {', '.join(issues)}"
        else:
            return f"Low uncertainty: minor issues with {', '.join(issues)}"
    
    def _get_recommendation(self, uncertainty: float) -> str:
        """Recommend action based on uncertainty level"""
        if uncertainty > 0.7:
            return "DEFER_TO_HUMAN - uncertainty too high for automated decision"
        elif uncertainty > 0.5:
            return "GATHER_MORE_DATA - wait for more events before acting"
        else:
            return "PROCEED_WITH_CAUTION - acceptable uncertainty level"
    
    def _get_flags(self, sparsity: float, staleness: float, conflict: float) -> List[str]:
        """Return list of specific uncertainty flags"""
        flags = []
        if sparsity > 0.6:
            flags.append("SPARSE_DATA")
        if staleness > 0.6:
            flags.append("STALE_DATA")
        if conflict > 0.5:
            flags.append("CONFLICTING_SIGNALS")
        return flags