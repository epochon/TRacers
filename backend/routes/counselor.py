"""
Counselor API Routes
Endpoints for viewing aggregated risk signals and managing interventions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import User, StudentEvent, CoordinatorDecision, AgentOutput, CounselorEscalation
from auth import get_current_counselor
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/counselor", tags=["counselor"])


class StudentRiskSummary(BaseModel):
    """Aggregated risk summary for counselor view"""
    student_id: int
    student_name: str
    risk_level: str
    aggregate_risk: float
    last_analyzed: datetime
    decision: str
    friction_count: int
    requires_attention: bool


class EscalationRequest(BaseModel):
    """Request for escalation"""
    student_id: Optional[int] = None
    session_id: Optional[str] = None
    reason: str


@router.get("/dashboard")
async def get_counselor_dashboard(
    current_user: User = Depends(get_current_counselor),
    db: Session = Depends(get_db)
):
    """
    Get counselor dashboard with overview of students needing attention
    Shows AGGREGATED signals, not raw surveillance
    """
    # Get all recent coordinator decisions
    recent_decisions = db.query(CoordinatorDecision).filter(
        CoordinatorDecision.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).order_by(CoordinatorDecision.timestamp.desc()).all()
    
    # Filter for attention-requiring decisions
    needs_attention = [
        d for d in recent_decisions 
        if d.decision in ['SOFT_OUTREACH', 'ESCALATE_TO_HUMAN']
    ]
    
    # Get pending escalations
    pending_escalations = db.query(CounselorEscalation).filter(
        CounselorEscalation.status == 'pending'
    ).count()
    
    # Statistics
    stats = {
        "total_monitored_students": len(set(d.student_id for d in recent_decisions)),
        "students_needing_attention": len(set(d.student_id for d in needs_attention)),
        "pending_escalations": pending_escalations,
        "soft_outreach_recommended": len([d for d in needs_attention if d.decision == 'SOFT_OUTREACH']),
        "human_intervention_recommended": len([d for d in needs_attention if d.decision == 'ESCALATE_TO_HUMAN'])
    }
    
    return {
        "statistics": stats,
        "last_updated": datetime.utcnow().isoformat(),
        "ethics_note": "All recommendations preserve student autonomy - no forced interventions"
    }


@router.get("/students-at-risk", response_model=List[StudentRiskSummary])
async def get_students_at_risk(
    current_user: User = Depends(get_current_counselor),
    db: Session = Depends(get_db),
    risk_threshold: float = 0.45
):
    """
    Get list of students with elevated friction
    Aggregated view only - no detailed surveillance
    """
    # Get recent decisions above threshold
    decisions = db.query(CoordinatorDecision).filter(
        CoordinatorDecision.aggregate_risk >= risk_threshold
    ).order_by(CoordinatorDecision.timestamp.desc()).all()
    
    # Group by student (most recent decision per student)
    student_decisions = {}
    for decision in decisions:
        if decision.student_id not in student_decisions:
            student_decisions[decision.student_id] = decision
    
    # Build summary list
    summaries = []
    for student_id, decision in student_decisions.items():
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            continue
        
        # Get friction event count
        event_count = db.query(StudentEvent).filter(
            StudentEvent.student_id == student_id
        ).count()
        
        summaries.append(StudentRiskSummary(
            student_id=student.id,
            student_name=student.full_name or student.username,
            risk_level=_format_risk_level(decision.aggregate_risk),
            aggregate_risk=decision.aggregate_risk,
            last_analyzed=decision.timestamp,
            decision=decision.decision,
            friction_count=event_count,
            requires_attention=decision.decision in ['SOFT_OUTREACH', 'ESCALATE_TO_HUMAN']
        ))
    
    return summaries


@router.get("/student/{student_id}/details")
async def get_student_details(
    student_id: int,
    current_user: User = Depends(get_current_counselor),
    db: Session = Depends(get_db)
):
    """
    Get detailed view of student's friction trajectory
    Only accessible when counselor is actively working on case
    """
    # Get student
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get latest coordinator decision
    latest_decision = db.query(CoordinatorDecision).filter(
        CoordinatorDecision.student_id == student_id
    ).order_by(CoordinatorDecision.timestamp.desc()).first()
    
    # Get latest agent outputs
    latest_outputs = db.query(AgentOutput).filter(
        AgentOutput.student_id == student_id
    ).order_by(AgentOutput.timestamp.desc()).limit(10).all()
    
    # Get events
    events = db.query(StudentEvent).filter(
        StudentEvent.student_id == student_id
    ).order_by(StudentEvent.timestamp.desc()).limit(20).all()
    
    return {
        "student_info": {
            "id": student.id,
            "name": student.full_name or student.username,
            "email": student.email
        },
        "current_assessment": {
            "decision": latest_decision.decision if latest_decision else "NO_ASSESSMENT",
            "justification": latest_decision.justification if latest_decision else "",
            "aggregate_risk": latest_decision.aggregate_risk if latest_decision else 0.0,
            "ethics_veto": latest_decision.ethics_veto if latest_decision else False,
            "distance_to_irreversibility": (latest_decision.meta_data or {}).get('distance_to_irreversibility', 100) if latest_decision else 100,
            "headline": (latest_decision.meta_data or {}).get('headline', "No Data") if latest_decision else "No Data"
        },
        "agent_insights": [
            {
                "agent": output.agent_name,
                "risk": output.risk_score,
                "confidence": output.confidence,
                "comment": output.comment
            }
            for output in latest_outputs
        ],
        "recent_friction_events": [
            {
                "type": event.event_type,
                "severity": event.severity,
                "description": event.description,
                "date": event.timestamp.isoformat()
            }
            for event in events
        ]
    }


@router.post("/escalate")
async def create_escalation(
    request: EscalationRequest,
    current_user: User = Depends(get_current_counselor),
    db: Session = Depends(get_db)
):
    """
    Create escalation request
    Consent-based - student must approve
    """
    escalation = CounselorEscalation(
        student_id=request.student_id,
        session_id=request.session_id,
        counselor_id=current_user.id,
        status='pending',
        consent_given=False,
        reason=request.reason
    )
    
    db.add(escalation)
    db.commit()
    
    return {
        "message": "Escalation created - awaiting student consent",
        "escalation_id": escalation.id,
        "consent_required": True
    }


@router.get("/escalations")
async def get_escalations(
    current_user: User = Depends(get_current_counselor),
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """Get escalation requests"""
    query = db.query(CounselorEscalation).filter(
        CounselorEscalation.counselor_id == current_user.id
    )
    
    if status:
        query = query.filter(CounselorEscalation.status == status)
    
    escalations = query.order_by(CounselorEscalation.created_at.desc()).all()
    
    return {
        "escalations": [
            {
                "id": e.id,
                "student_id": e.student_id,
                "status": e.status,
                "consent_given": e.consent_given,
                "reason": e.reason,
                "created_at": e.created_at.isoformat()
            }
            for e in escalations
        ]
    }


@router.get("/anonymous-sessions")
async def get_anonymous_sessions(
    current_user: User = Depends(get_current_counselor)
):
    """
    Get active anonymous chat sessions
    Minimal metadata only
    """
    from chat.counselor_chat import counselor_chat_manager
    
    sessions = []
    for session_id, metadata in counselor_chat_manager.session_metadata.items():
        if session_id in counselor_chat_manager.active_sessions:
            sessions.append({
                "session_id": session_id,
                "started_at": metadata['started_at'],
                "is_anonymous": metadata['is_anonymous'],
                "message_count": len(counselor_chat_manager.message_history.get(session_id, []))
            })
    
    return {"active_sessions": sessions}


def _format_risk_level(risk: float) -> str:
    """Format risk as human-readable level"""
    if risk < 0.3:
        return "Low"
    elif risk < 0.6:
        return "Moderate"
    else:
        return "Elevated"