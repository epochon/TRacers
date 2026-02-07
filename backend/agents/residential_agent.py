"""
Residential Stability Agent
Detects housing and basic needs friction
Focus: hostel access, mess services, residential bureaucracy
"""
#residential_agent.py
from typing import List, Dict
from models import StudentEvent
from datetime import datetime, timedelta


class ResidentialAgent:
    """
    Analyzes residential stability and basic needs friction
    Housing insecurity as a bureaucratic barrier to education
    """
    
    def __init__(self):
        self.name = "ResidentialAgent"
        self.weight = 0.2
    
    def evaluate(self, events: List[StudentEvent]) -> Dict:
        """
        Evaluate residential friction events
        
        Critical factors:
        - Hostel access issues
        - Mess card problems
        - Room assignment delays
        - Basic amenities access
        """
        residential_events = [
            e for e in events 
            if e.event_type in ['hostel_access', 'mess_card', 'room_assignment', 
                               'amenity_restriction', 'housing_payment']
        ]
        
        if not residential_events:
            return {
                'agent': self.name,
                'risk': 0.0,
                'confidence': 0.8,
                'comment': 'No residential friction detected',
                'details': {'event_count': 0}
            }
        
        event_count = len(residential_events)
        
        # Basic needs issues are HIGH PRIORITY
        basic_needs_events = [
            e for e in residential_events 
            if e.event_type in ['mess_card', 'amenity_restriction']
        ]
        
        # Recency matters more for residential issues
        recent_events = [
            e for e in residential_events 
            if (datetime.utcnow() - e.timestamp) <= timedelta(days=21)
        ]
        
        # Calculate risk
        base_risk = min(event_count / 4.0, 0.85)  # Housing issues are serious
        basic_needs_multiplier = 1.0 + (len(basic_needs_events) * 0.2)  # Up to 1.6x
        recency_factor = len(recent_events) / max(event_count, 1)
        
        risk = min(base_risk * basic_needs_multiplier * (0.7 + 0.3 * recency_factor), 1.0)
        
        # Lower confidence - housing situations are complex
        confidence = min(0.55 + (event_count * 0.06), 0.88)
        
        comment = self._generate_comment(event_count, basic_needs_events, recent_events, risk)
        
        return {
            'agent': self.name,
            'risk': round(risk, 3),
            'confidence': round(confidence, 3),
            'comment': comment,
            'details': {
                'event_count': event_count,
                'basic_needs_events': len(basic_needs_events),
                'recent_events': len(recent_events),
                'issue_breakdown': self._breakdown_issues(residential_events)
            }
        }
    
    def _generate_comment(self, count: int, basic_needs: List, recent: List, risk: float) -> str:
        """Generate comment with emphasis on basic needs"""
        if len(basic_needs) > 0:
            return f"Basic needs friction detected - {len(basic_needs)} mess/amenity barriers among {count} total events"
        elif risk > 0.6:
            return f"Significant residential friction - {count} housing-related barriers, {len(recent)} recent"
        elif risk > 0.3:
            return f"Moderate residential bureaucracy - {count} access issues"
        else:
            return "Minor residential friction"
    
    def _breakdown_issues(self, events: List[StudentEvent]) -> Dict[str, int]:
        """Break down residential issues by type"""
        breakdown = {}
        for event in events:
            event_type = event.event_type
            breakdown[event_type] = breakdown.get(event_type, 0) + 1
        return breakdown