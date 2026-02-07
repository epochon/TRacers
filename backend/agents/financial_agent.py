"""
Financial Friction Agent
Detects cumulative bureaucratic barriers related to scholarships, fees, and financial aid
NOT about poverty - about institutional friction
"""

from typing import List, Dict
from models import StudentEvent


class FinancialAgent:
    """
    Analyzes financial bureaucratic friction events
    Focus: scholarship delays, fee payment barriers, financial aid access issues
    """
    
    def __init__(self):
        self.name = "FinancialAgent"
        self.weight = 0.25  # Contribution to overall risk assessment
    
    def evaluate(self, events: List[StudentEvent]) -> Dict:
        """
        Evaluate financial friction events
        
        Returns:
            dict: {
                'agent': str,
                'risk': float (0.0-1.0),
                'confidence': float (0.0-1.0),
                'comment': str,
                'details': dict
            }
        """
        financial_events = [
            e for e in events 
            if e.event_type in ['scholarship_delay', 'fee_payment', 'financial_aid', 'account_hold']
        ]
        
        if not financial_events:
            return {
                'agent': self.name,
                'risk': 0.0,
                'confidence': 0.9,
                'comment': 'No financial friction detected',
                'details': {'event_count': 0}
            }
        
        # Calculate risk based on event frequency and recency
        event_count = len(financial_events)
        recent_events = [e for e in financial_events if self._is_recent(e, days=30)]
        
        # Severity accumulation (bureaucratic friction compounds)
        avg_severity = sum(e.severity for e in financial_events) / event_count
        
        # Risk calculation
        frequency_factor = min(event_count / 5.0, 1.0)  # Normalize to max 5 events
        recency_factor = len(recent_events) / max(event_count, 1)
        severity_factor = avg_severity
        
        risk = (frequency_factor * 0.4 + recency_factor * 0.3 + severity_factor * 0.3)
        
        # Confidence based on data availability
        confidence = min(0.6 + (event_count * 0.05), 0.95)
        
        # Generate contextual comment
        comment = self._generate_comment(event_count, recent_events, risk)
        
        return {
            'agent': self.name,
            'risk': round(risk, 3),
            'confidence': round(confidence, 3),
            'comment': comment,
            'details': {
                'event_count': event_count,
                'recent_events': len(recent_events),
                'avg_severity': round(avg_severity, 3),
                'primary_issues': self._get_primary_issues(financial_events)
            }
        }
    
    def _is_recent(self, event: StudentEvent, days: int = 30) -> bool:
        """Check if event occurred within specified days"""
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        return event.timestamp >= cutoff
    
    def _generate_comment(self, count: int, recent: List, risk: float) -> str:
        """Generate human-readable comment about financial friction"""
        if risk < 0.3:
            return "Minimal financial friction detected"
        elif risk < 0.6:
            return f"Moderate financial bureaucratic delays ({count} events, {len(recent)} recent)"
        else:
            return f"Significant financial friction pattern - {count} cumulative barriers detected"
    
    def _get_primary_issues(self, events: List[StudentEvent]) -> List[str]:
        """Identify most common financial friction types"""
        issue_counts = {}
        for event in events:
            issue_type = event.event_type
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Return top 3 issues
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue[0] for issue in sorted_issues[:3]]