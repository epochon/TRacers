"""
Language & Communication Agent
Detects language mismatch and communication barriers
Focus: institutional language vs. student's primary language
"""

from typing import List, Dict
from datetime import datetime, timedelta


class LanguageAgent:
    """
    Analyzes communication and language friction
    Language barriers as a bureaucratic obstacle
    """
    
    def __init__(self):
        self.name = "LanguageAgent"
        self.weight = 0.15
    
    def evaluate(self, events: List) -> Dict:
        """
        Evaluate language and communication friction
        
        Focus:
        - Language mismatch in official communications
        - Misunderstood bureaucratic processes
        - Communication barriers with administration
        """
        language_events = [
            e for e in events 
            if e.get('event_type') in ['language_barrier', 'communication_issue', 
                                       'form_confusion', 'instruction_misunderstanding']
        ]
        
        if not language_events:
            return {
                'agent': self.name,
                'risk': 0.0,
                'confidence': 0.75,
                'comment': 'No language friction detected',
                'details': {'event_count': 0}
            }
        
        event_count = len(language_events)
        
        # Language barriers often cascade - each makes the next worse
        cascade_factor = min(1.0 + (event_count - 1) * 0.2, 2.0)
        
        # Severity matters here - mild confusion vs. complete breakdown
        avg_severity = sum(e.get('severity', 0.5) for e in language_events) / event_count
        
        # Base risk calculation
        base_risk = min(event_count / 5.0, 0.8)
        risk = min(base_risk * cascade_factor * avg_severity, 1.0)
        
        # Moderate confidence - language issues are hard to quantify
        confidence = min(0.6 + (event_count * 0.05), 0.85)
        
        comment = self._generate_comment(event_count, avg_severity, risk)
        
        return {
            'agent': self.name,
            'risk': round(risk, 3),
            'confidence': round(confidence, 3),
            'comment': comment,
            'details': {
                'event_count': event_count,
                'avg_severity': round(avg_severity, 3),
                'cascade_factor': round(cascade_factor, 2),
                'barrier_types': self._categorize_barriers(language_events)
            }
        }
    
    def _generate_comment(self, count: int, severity: float, risk: float) -> str:
        """Generate contextual comment"""
        if risk < 0.3:
            return f"Minor language friction - {count} isolated communication issues"
        elif risk < 0.6:
            if severity > 0.7:
                return f"Moderate language barriers with high severity - {count} significant communication breakdowns"
            return f"Moderate communication friction - {count} language-related issues"
        else:
            return f"Severe language friction - {count} cascading communication barriers (severity: {severity:.2f})"
    
    def _categorize_barriers(self, events: List) -> Dict[str, int]:
        """Categorize types of language barriers"""
        categories = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            categories[event_type] = categories.get(event_type, 0) + 1
        return categories