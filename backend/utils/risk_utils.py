"""
Risk Utilities
Helper functions for event generation and system insights
"""

from typing import List, Dict
from datetime import datetime, timedelta
import random
from models import StudentEvent, User, SystemInsight
from sqlalchemy.orm import Session


def generate_sample_events(db: Session, student_id: int, scenario: str = "moderate") -> List[StudentEvent]:
    """
    Generate sample bureaucratic friction events for testing/demo
    
    Scenarios:
    - low: Minimal friction
    - moderate: Some accumulated barriers
    - high: Significant compounding issues
    - crisis: Basic needs threatened
    """
    events = []
    base_time = datetime.utcnow() - timedelta(days=90)
    
    if scenario == "low":
        # Single, low-severity event
        events.append(StudentEvent(
            student_id=student_id,
            event_type="fee_payment",
            severity=0.3,
            description="Minor delay in fee payment processing",
            timestamp=base_time + timedelta(days=30)
        ))
    
    elif scenario == "moderate":
        # Multiple events across domains
        events.extend([
            StudentEvent(
                student_id=student_id,
                event_type="scholarship_delay",
                severity=0.5,
                description="Scholarship disbursement delayed by 2 weeks",
                timestamp=base_time + timedelta(days=15)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="attendance_warning",
                severity=0.4,
                description="Attendance warning due to documentation issue",
                timestamp=base_time + timedelta(days=40)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="room_assignment",
                severity=0.5,
                description="Room reassignment delayed",
                timestamp=base_time + timedelta(days=60)
            )
        ])
    
    elif scenario == "high":
        # Frequent, clustered events
        events.extend([
            StudentEvent(
                student_id=student_id,
                event_type="scholarship_delay",
                severity=0.7,
                description="Scholarship delayed - verification issues",
                timestamp=base_time + timedelta(days=10)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="account_hold",
                severity=0.8,
                description="Account hold preventing registration",
                timestamp=base_time + timedelta(days=20)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="attendance_warning",
                severity=0.6,
                description="Attendance penalty despite medical documentation",
                timestamp=base_time + timedelta(days=25)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="deadline_conflict",
                severity=0.5,
                description="Conflicting administrative deadlines",
                timestamp=base_time + timedelta(days=30)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="language_barrier",
                severity=0.6,
                description="Financial aid form confusion - language mismatch",
                timestamp=base_time + timedelta(days=45)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="hostel_access",
                severity=0.7,
                description="Hostel access card deactivated - payment processing",
                timestamp=base_time + timedelta(days=70)
            )
        ])
    
    elif scenario == "crisis":
        # Basic needs threatened
        events.extend([
            StudentEvent(
                student_id=student_id,
                event_type="scholarship_delay",
                severity=0.8,
                description="Scholarship not disbursed - verification loop",
                timestamp=base_time + timedelta(days=5)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="mess_card",
                severity=0.9,
                description="Mess card suspended - payment pending",
                timestamp=base_time + timedelta(days=15)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="hostel_access",
                severity=0.9,
                description="Hostel access revoked - administrative error",
                timestamp=base_time + timedelta(days=20)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="account_hold",
                severity=0.9,
                description="Full account hold - cascading payment issues",
                timestamp=base_time + timedelta(days=25)
            ),
            StudentEvent(
                student_id=student_id,
                event_type="registration_block",
                severity=0.8,
                description="Registration blocked for next semester",
                timestamp=base_time + timedelta(days=80)
            )
        ])
    
    # Add events to database
    for event in events:
        db.add(event)
    
    db.commit()
    return events


def calculate_system_insights(db: Session) -> List[Dict]:
    """
    Calculate aggregated, anonymized insights for admin dashboard
    NO individual student data
    """
    insights = []
    
    # Query all events
    all_events = db.query(StudentEvent).all()
    
    if not all_events:
        return insights
    
    # Insight 1: Scholarship delays correlate with other friction
    scholarship_events = [e for e in all_events if e.event_type == "scholarship_delay"]
    scholarship_student_ids = set(e.student_id for e in scholarship_events)
    
    if scholarship_student_ids:
        # Check what other events these students experience
        other_events = [
            e for e in all_events 
            if e.student_id in scholarship_student_ids and e.event_type != "scholarship_delay"
        ]
        
        if other_events:
            # Count event types
            event_type_counts = {}
            for event in other_events:
                event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
            
            # Most common co-occurring issue
            most_common = max(event_type_counts.items(), key=lambda x: x[1])
            
            insights.append({
                'insight_type': 'correlation',
                'description': f"Students with scholarship delays also frequently experience {most_common[0]} ({most_common[1]} cases)",
                'affected_count': len(scholarship_student_ids),
                'severity': 0.7,
                'recommendation': "Review scholarship processing workflow and its impact on other services"
            })
    
    # Insight 2: Clustering of events (bureaucratic cascade)
    student_event_counts = {}
    for event in all_events:
        student_event_counts[event.student_id] = student_event_counts.get(event.student_id, 0) + 1
    
    high_friction_students = [sid for sid, count in student_event_counts.items() if count >= 5]
    
    if high_friction_students:
        insights.append({
            'insight_type': 'pattern',
            'description': f"Bureaucratic cascade detected - {len(high_friction_students)} students experiencing 5+ friction events",
            'affected_count': len(high_friction_students),
            'severity': 0.8,
            'recommendation': "Investigate process bottlenecks causing event clustering"
        })
    
    # Insight 3: Basic needs friction
    basic_needs_events = [
        e for e in all_events 
        if e.event_type in ['mess_card', 'hostel_access', 'amenity_restriction']
    ]
    
    if basic_needs_events:
        affected_students = len(set(e.student_id for e in basic_needs_events))
        insights.append({
            'insight_type': 'blind_spot',
            'description': f"Basic needs friction - {affected_students} students affected by housing/food access issues",
            'affected_count': affected_students,
            'severity': 0.9,
            'recommendation': "Priority review of basic needs access procedures"
        })
    
    # Insight 4: Language barriers
    language_events = [
        e for e in all_events 
        if e.event_type in ['language_barrier', 'form_confusion', 'communication_issue']
    ]
    
    if language_events:
        affected_students = len(set(e.student_id for e in language_events))
        insights.append({
            'insight_type': 'blind_spot',
            'description': f"Communication barriers - {affected_students} students facing language/documentation issues",
            'affected_count': affected_students,
            'severity': 0.6,
            'recommendation': "Consider multilingual support and clearer documentation"
        })
    
    return insights


def store_system_insights(db: Session):
    """Calculate and store system insights in database"""
    insights = calculate_system_insights(db)
    
    for insight_data in insights:
        insight = SystemInsight(
            insight_type=insight_data['insight_type'],
            description=insight_data['description'],
            affected_count=insight_data['affected_count'],
            severity=insight_data['severity'],
            metadata_text=str({'recommendation': insight_data['recommendation']})
        )
        db.add(insight)
    
    db.commit()