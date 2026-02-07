"""
Academic Pressure Agent
Detects bureaucratic academic friction (not academic failure)
Focus: attendance penalties, deadline conflicts, administrative warnings
"""

from typing import List, Dict
from models import StudentEvent
from datetime import datetime, timedelta


class AcademicAgent:
    """
    Analyzes academic bureaucratic pressure
    NOT about grades - about systemic barriers to academic participation
    """
    
    def __init__(self):
        self.name = "AcademicAgent"
        self.weight = 0.2
    
    def evaluate(self, events: List[StudentEvent]) -> Dict:
        """
        Evaluate academic friction events
        
        Focus areas:
        - Attendance penalties (bureaucratic, not educational)
        - Conflicting deadline requirements
        - Administrative warnings
        - Access restrictions to academic resources
        """
        academic_events = [
            e for e in events 
            if e.event_type in ['attendance_warning', 'deadline_conflict', 
                               'admin_warning', 'resource_access', 'registration_block']
        ]
        
        if not academic_events:
            return {
                'agent': self.name,
                'risk': 0.0,
                'confidence': 0.85,
                'comment': 'No academic bureaucratic friction detected',
                'details': {'event_count': 0}
            }
        
        event_count = len(academic_events)
        
        # Analyze clustering - multiple events in short time = higher friction
        clustered_events = self._detect_clustering(academic_events)
        
        # Calculate risk
        base_risk = min(event_count / 6.0, 0.9)  # Normalize to 6 events max
        cluster_penalty = min(clustered_events * 0.15, 0.3)  # Up to 30% additional
        
        # Severity weighting
        avg_severity = sum(e.severity for e in academic_events) / event_count
        
        risk = min(base_risk + cluster_penalty, 1.0) * avg_severity
        
        # Confidence increases with more data points
        confidence = min(0.65 + (event_count * 0.04), 0.92)
        
        comment = self._generate_comment(event_count, clustered_events, risk)
        
        return {
            'agent': self.name,
            'risk': round(risk, 3),
            'confidence': round(confidence, 3),
            'comment': comment,
            'details': {
                'event_count': event_count,
                'clustered_events': clustered_events,
                'avg_severity': round(avg_severity, 3),
                'friction_types': self._categorize_friction(academic_events)
            }
        }
    
    def _detect_clustering(self, events: List[StudentEvent]) -> int:
        """Detect if events cluster in time (indicates compounding friction)"""
        if len(events) < 2:
            return 0
        
        # Sort by timestamp
        sorted_events = sorted(events, key=lambda x: x.timestamp)
        
        clusters = 0
        for i in range(len(sorted_events) - 1):
            time_diff = sorted_events[i + 1].timestamp - sorted_events[i].timestamp
            if time_diff <= timedelta(days=14):  # Events within 2 weeks
                clusters += 1
        
        return clusters
    
    def _generate_comment(self, count: int, clusters: int, risk: float) -> str:
        """Generate contextual comment"""
        if risk < 0.3:
            return "Low academic friction - isolated administrative events"
        elif risk < 0.6:
            if clusters > 0:
                return f"Moderate friction with {clusters} clustered events - compounding barriers"
            return f"Moderate academic bureaucratic pressure ({count} events)"
        else:
            return f"High academic friction - {count} events including {clusters} rapid-succession barriers"
    
    def _categorize_friction(self, events: List[StudentEvent]) -> Dict[str, int]:
        """Break down friction by category"""
        categories = {}
        for event in events:
            event_type = event.event_type
            categories[event_type] = categories.get(event_type, 0) + 1
        return categories