"""
Student API Routes
Endpoints for student dashboard, timeline, and chat access
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, StudentEvent, CoordinatorDecision, AgentOutput
from auth import get_current_student
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/student", tags=["student"])


class EventResponse(BaseModel):
    """Student event response model"""
    id: int
    event_type: str
    severity: float
    description: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class TimelineResponse(BaseModel):
    """Timeline response with events and analysis"""
    events: List[EventResponse]
    total_events: int
    recent_events: int
    trajectory_summary: str


class DashboardResponse(BaseModel):
    """Student dashboard summary"""
    student_name: str
    total_friction_events: int
    recent_friction_events: int  # Last 30 days
    current_risk_level: str
    support_available: bool
    trajectory_summary: str


@router.get("/dashboard", response_model=DashboardResponse)
async def get_student_dashboard(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get student dashboard summary
    Shows non-clinical friction trajectory
    """
    # Get all events for student
    events = db.query(StudentEvent).filter(
        StudentEvent.student_id == current_user.id
    ).all()
    
    # Recent events (last 30 days)
    cutoff = datetime.utcnow() - timedelta(days=30)
    recent_events = [e for e in events if e.timestamp >= cutoff]
    
    # Get latest coordinator decision if exists
    latest_decision = db.query(CoordinatorDecision).filter(
        CoordinatorDecision.student_id == current_user.id
    ).order_by(CoordinatorDecision.timestamp.desc()).first()
    
    # Determine risk level and trajectory
    if latest_decision:
        risk_level = _map_decision_to_risk_level(latest_decision.decision)
        trajectory = latest_decision.justification
    else:
        risk_level = "Minimal friction"
        trajectory = "No significant bureaucratic barriers detected"
    
    return DashboardResponse(
        student_name=current_user.full_name or current_user.username,
        total_friction_events=len(events),
        recent_friction_events=len(recent_events),
        current_risk_level=risk_level,
        support_available=risk_level != "Minimal friction",
        trajectory_summary=trajectory
    )


@router.get("/timeline", response_model=TimelineResponse)
async def get_student_timeline(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
    days: int = 90
):
    """
    Get student's bureaucratic friction timeline
    Shows events over time, not grades or performance
    """
    # Get events within time range
    cutoff = datetime.utcnow() - timedelta(days=days)
    events = db.query(StudentEvent).filter(
        StudentEvent.student_id == current_user.id,
        StudentEvent.timestamp >= cutoff
    ).order_by(StudentEvent.timestamp.desc()).all()
    
    # Recent events (last 30 days)
    recent_cutoff = datetime.utcnow() - timedelta(days=30)
    recent_count = len([e for e in events if e.timestamp >= recent_cutoff])
    
    # Generate trajectory summary
    if len(events) == 0:
        summary = "No bureaucratic friction events in the past 90 days"
    elif len(events) <= 2:
        summary = f"{len(events)} minor friction events - isolated administrative issues"
    elif recent_count > len(events) * 0.7:
        summary = f"{len(events)} events, mostly recent - potential clustering of barriers"
    else:
        summary = f"{len(events)} accumulated friction events - ongoing administrative challenges"
    
    return TimelineResponse(
        events=[EventResponse.from_orm(e) for e in events],
        total_events=len(events),
        recent_events=recent_count,
        trajectory_summary=summary
    )


@router.get("/agent-analysis")
async def get_agent_analysis(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get latest multi-agent analysis of student's situation
    Transparent view into how system assesses friction
    """
    # Get latest agent outputs
    latest_outputs = db.query(AgentOutput).filter(
        AgentOutput.student_id == current_user.id
    ).order_by(AgentOutput.timestamp.desc()).limit(10).all()
    
    if not latest_outputs:
        return {
            "message": "No agent analysis available yet",
            "analysis": []
        }
    
    # Group by timestamp to get most recent analysis set
    latest_timestamp = latest_outputs[0].timestamp
    current_analysis = [
        o for o in latest_outputs 
        if o.timestamp == latest_timestamp
    ]
    
    # Format for student view
    analysis_summary = []
    for output in current_analysis:
        analysis_summary.append({
            "agent": output.agent_name,
            "risk_level": _format_risk_level(output.risk_score),
            "confidence": f"{output.confidence * 100:.0f}%",
            "assessment": output.comment
        })
    
    return {
        "analyzed_at": latest_timestamp.isoformat(),
        "analysis": analysis_summary,
        "transparency_note": "This shows how our system assesses bureaucratic friction - not your academic ability or worth"
    }


@router.get("/support-resources")
async def get_support_resources(
    current_user: User = Depends(get_current_student)
):
    """
    Get available support resources
    Non-coercive, consent-based
    """
    return {
        "anonymous_counselor_chat": {
            "available": True,
            "description": "Anonymous chat with a counselor - no identity required",
            "consent_based": True
        },
        "community_chat": {
            "available": True,
            "description": "Connect with other first-year students",
            "rooms": ["General", "Academic Support", "Campus Life", "Wellness"]
        },
        "human_support": {
            "available": True,
            "description": "Request connection with a human counselor",
            "note": "You control if and when to share your identity"
        }
    }


def _map_decision_to_risk_level(decision: str) -> str:
    """Map coordinator decision to human-readable risk level"""
    mapping = {
        "NO_ACTION": "Minimal friction",
        "WATCH": "Low-moderate friction",
        "SOFT_OUTREACH": "Moderate friction - support available",
        "ESCALATE_TO_HUMAN": "Significant friction - counselor recommended"
    }
    return mapping.get(decision, "Unknown")


def _format_risk_level(risk_score: float) -> str:
    """Format risk score as human-readable level"""
    if risk_score < 0.3:
        return "Low"
    elif risk_score < 0.6:
        return "Moderate"
    else:
        return "Elevated"