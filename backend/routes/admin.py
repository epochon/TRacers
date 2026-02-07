"""
Admin API Routes
System-level insights and blind spot analytics
NO individual student monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import SystemInsight, StudentEvent
from auth import get_current_admin
from pydantic import BaseModel
from datetime import datetime, timedelta
from utils.risk_utils import calculate_system_insights, store_system_insights

router = APIRouter(prefix="/api/admin", tags=["admin"])


class InsightResponse(BaseModel):
    """System insight response"""
    id: int
    insight_type: str
    description: str
    affected_count: int
    severity: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


@router.get("/dashboard")
async def get_admin_dashboard(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get admin dashboard with system-level analytics
    Focus on institutional blind spots, not individual students
    """
    # Get system statistics
    total_events = db.query(StudentEvent).count()
    recent_events = db.query(StudentEvent).filter(
        StudentEvent.timestamp >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    # Event type distribution (aggregated)
    all_events = db.query(StudentEvent).all()
    event_type_counts = {}
    for event in all_events:
        event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
    
    # Get recent insights
    recent_insights = db.query(SystemInsight).order_by(
        SystemInsight.timestamp.desc()
    ).limit(5).all()
    
    return {
        "system_statistics": {
            "total_friction_events": total_events,
            "recent_friction_events": recent_events,
            "event_type_distribution": event_type_counts,
            "most_common_friction": max(event_type_counts.items(), key=lambda x: x[1])[0] if event_type_counts else "None"
        },
        "recent_insights": [
            {
                "type": insight.insight_type,
                "description": insight.description,
                "affected_count": insight.affected_count,
                "severity": insight.severity
            }
            for insight in recent_insights
        ],
        "privacy_note": "All data is aggregated and anonymized - no individual student tracking"
    }


@router.get("/insights", response_model=List[InsightResponse])
async def get_system_insights(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db),
    insight_type: str = None
):
    """
    Get system insights showing institutional blind spots
    Helps identify process problems, not student problems
    """
    query = db.query(SystemInsight)
    
    if insight_type:
        query = query.filter(SystemInsight.insight_type == insight_type)
    
    insights = query.order_by(SystemInsight.timestamp.desc()).all()
    
    return insights


@router.post("/generate-insights")
async def generate_insights(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Generate fresh system insights from current data
    Analyzes patterns and correlations at system level
    """
    # Calculate new insights
    insights = calculate_system_insights(db)
    
    # Store in database
    for insight_data in insights:
        insight = SystemInsight(
            insight_type=insight_data['insight_type'],
            description=insight_data['description'],
            affected_count=insight_data['affected_count'],
            severity=insight_data['severity'],
            metadata=str({'recommendation': insight_data['recommendation']})
        )
        db.add(insight)
    
    db.commit()
    
    return {
        "message": f"Generated {len(insights)} system insights",
        "insights": insights
    }


@router.get("/friction-patterns")
async def get_friction_patterns(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db),
    days: int = 90
):
    """
    Analyze friction patterns over time
    Identifies systemic issues and trends
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    events = db.query(StudentEvent).filter(
        StudentEvent.timestamp >= cutoff
    ).all()
    
    if not events:
        return {"message": "No events in time range"}
    
    # Temporal distribution
    events_by_week = {}
    for event in events:
        week = event.timestamp.isocalendar()[1]
        events_by_week[week] = events_by_week.get(week, 0) + 1
    
    # Identify peak friction periods
    avg_events_per_week = sum(events_by_week.values()) / len(events_by_week) if events_by_week else 0
    peak_weeks = [week for week, count in events_by_week.items() if count > avg_events_per_week * 1.5]
    
    # Co-occurrence analysis
    student_event_types = {}
    for event in events:
        if event.student_id not in student_event_types:
            student_event_types[event.student_id] = set()
        student_event_types[event.student_id].add(event.event_type)
    
    # Find common event pairs
    event_pairs = {}
    for event_set in student_event_types.values():
        if len(event_set) >= 2:
            for e1 in event_set:
                for e2 in event_set:
                    if e1 < e2:  # Avoid duplicates
                        pair = f"{e1} + {e2}"
                        event_pairs[pair] = event_pairs.get(pair, 0) + 1
    
    top_pairs = sorted(event_pairs.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "time_period": f"{days} days",
        "total_events": len(events),
        "events_per_week_avg": round(avg_events_per_week, 1),
        "peak_friction_weeks": peak_weeks,
        "common_event_combinations": [
            {"pair": pair, "count": count}
            for pair, count in top_pairs
        ],
        "interpretation": "These patterns suggest systemic process issues, not individual student problems"
    }


@router.get("/intervention-effectiveness")
async def get_intervention_effectiveness(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Analyze effectiveness of system interventions
    Focus on process improvements, not student outcomes
    """
    # This would track changes in friction patterns after policy changes
    # For demo, provide framework
    
    return {
        "message": "Intervention tracking framework",
        "metrics": {
            "pre_intervention_friction_rate": "Baseline friction events per student",
            "post_intervention_friction_rate": "Friction events after process change",
            "specific_friction_reduction": "Reduction in specific event types",
            "new_friction_emergence": "New types of friction created"
        },
        "note": "Focus on fixing processes, not fixing students"
    }


@router.get("/ethical-safeguards")
async def get_ethical_safeguards(
    current_user = Depends(get_current_admin)
):
    """
    Report on ethical safeguards and system restraint
    Transparency into how system protects students
    """
    return {
        "active_safeguards": [
            {
                "safeguard": "Ethics Agent Veto Power",
                "description": "Can block any automated decision that risks human dignity",
                "status": "Active"
            },
            {
                "safeguard": "Uncertainty Modeling",
                "description": "Explicitly acknowledges data limitations and defers to humans",
                "status": "Active"
            },
            {
                "safeguard": "Consent-Based Escalation",
                "description": "Students control identity revelation and support engagement",
                "status": "Active"
            },
            {
                "safeguard": "No Punitive Actions",
                "description": "System cannot trigger disciplinary or punitive measures",
                "status": "Active"
            },
            {
                "safeguard": "Aggregated Admin View",
                "description": "Admin sees patterns, not individual student data",
                "status": "Active"
            }
        ],
        "restraint_metrics": {
            "decisions_vetoed_by_ethics_agent": "Count of automated decisions blocked",
            "escalations_deferred_to_humans": "Cases where uncertainty was too high",
            "student_consent_required": "All identity-revealing interactions"
        },
        "philosophy": "System knows when NOT to act - restraint is a feature, not a bug"
    }