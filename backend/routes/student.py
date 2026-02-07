"""
Updated Student API Routes
Added endpoints for Senior Chat and GovConnect
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
    student_id: str
    total_friction_events: int
    recent_friction_events: int
    current_risk_level: str
    support_available: bool
    trajectory_summary: str
    distance_to_irreversibility: float = 1.0
    headline: str = "Status Verified"


# Global singleton for ML Coordinator
COORDINATOR_INSTANCE = None

def get_coordinator_singleton():
    """Get or initialize the global coordinator instance"""
    global COORDINATOR_INSTANCE
    if COORDINATOR_INSTANCE is None:
        print("Initializing Global ML Coordinator...")
        from agents.coordinator_ml import CoordinatorAgentML
        COORDINATOR_INSTANCE = CoordinatorAgentML()
        print("Global ML Coordinator Initialized.")
    return COORDINATOR_INSTANCE


@router.get("/dashboard", response_model=DashboardResponse)
async def get_student_dashboard(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get student dashboard summary with ML-powered risk assessment
    Shows non-clinical friction trajectory using trained models
    """
    
    # Get coordinator from singleton (should be pre-loaded by main.py)
    try:
        coordinator = get_coordinator_singleton()
    except Exception as e:
        print(f"Error getting coordinator: {e}")
        # Fallback if initialization fails
        coordinator = None
    
    # Get all events for student
    
    # Get all events for student
    events = db.query(StudentEvent).filter(
        StudentEvent.student_id == current_user.id
    ).all()
    
    # Recent events (last 30 days)
    cutoff = datetime.utcnow() - timedelta(days=30)
    recent_events = [e for e in events if e.timestamp >= cutoff]
    
    # Use cached coordinator for real-time assessment
    if events and coordinator:
        try:
            ml_result = coordinator.evaluate(events)
            
            risk_level = _map_decision_to_risk_level(ml_result['decision'])
            trajectory = ml_result['justification']
            distance = ml_result.get('distance_to_irreversibility', 1.0)
            headline = ml_result.get('headline', "Status Verified")
            
            # Optionally save to database for history
            try:
                decision = CoordinatorDecision(
                    student_id=current_user.id,
                    decision=ml_result['decision'],
                    aggregate_risk=ml_result['final_risk'],
                    confidence=ml_result.get('confidence', 0.8),
                    justification=trajectory,
                    meta_data=ml_result.get('meta_data', {})
                )
                db.add(decision)
                db.commit()
            except Exception as e:
                print(f"Warning: Could not save decision: {e}")
                db.rollback()

        except Exception as e:
            print(f"Error in ML evaluation: {e}")
            risk_level = "Processing Analysis"
            trajectory = "System analysis currently processing in background. Please refresh shortly."
            distance = 1.0
            headline = "Pending Analysis"
    else:
        # No events or coordinator not ready - use defaults
        risk_level = "Minimal friction"
        trajectory = "No significant bureaucratic barriers detected (or system initializing)"
        distance = 1.0
        headline = "System Nominal"
    
    return DashboardResponse(
        student_name=current_user.full_name or current_user.username,
        student_id=str(current_user.id),
        total_friction_events=len(events),
        recent_friction_events=len(recent_events),
        current_risk_level=risk_level,
        support_available=risk_level != "Minimal friction",
        trajectory_summary=trajectory,
        distance_to_irreversibility=distance,
        headline=headline
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


@router.get("/senior-chat")
async def get_senior_chat_access(
    current_user: User = Depends(get_current_student),
):
    """
    Access to verified senior mentorship chat
    """
    return {
        "available": True,
        "description": "Connect with verified senior mentors",
        "room_type": "senior",
        "features": [
            "Peer mentorship",
            "Academic guidance",
            "Campus navigation help",
            "Experience sharing"
        ],
        "privacy_note": "Your identity is visible only to verified senior mentors"
    }


@router.get("/gov-connect")
async def get_gov_connect_access(
    current_user: User = Depends(get_current_student),
):
    """
    Direct channel to institutional authorities
    """
    return {
        "available": True,
        "description": "Direct communication with institutional authorities",
        "room_type": "gov",
        "scope": [
            "Scholarship issues",
            "Hostel allotment",
            "Exam fee problems",
            "Administrative grievances"
        ],
        "response_policy": "Responses may take 24-48 hours depending on query volume",
        "transparency_note": "All conversations are logged for institutional accountability"
    }


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
        },
        "senior_chat": {
            "available": True,
            "description": "Connect with verified senior mentors",
        },
        "gov_connect": {
            "available": True,
            "description": "Direct channel to institutional authorities",
        },
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