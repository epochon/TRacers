"""
TRACES Pro - Intervention Orchestrator Agent Models
Autonomous agent system for proactive student support
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base

# ============================================================================
# ENUMS
# ============================================================================

class AgentStatus(str, enum.Enum):
    IDLE = "idle"
    OBSERVING = "observing"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"

class InterventionType(str, enum.Enum):
    FINANCIAL_AID = "financial_aid"
    PEER_SUPPORT = "peer_support"
    COUNSELOR_CHAT = "counselor_chat"
    ACADEMIC_SUPPORT = "academic_support"
    DOCUMENT_ASSISTANCE = "document_assistance"
    SCHOLARSHIP_MATCH = "scholarship_match"
    FEE_EXTENSION = "fee_extension"
    EMERGENCY_ESCALATION = "emergency_escalation"

class InterventionStatus(str, enum.Enum):
    PLANNED = "planned"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ActionStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# ============================================================================
# AGENT MODELS
# ============================================================================

class AgentSession(Base):
    """IOA session tracking"""
    __tablename__ = "agent_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Session Info
    session_id = Column(String(100), unique=True, nullable=False)
    status = Column(SQLEnum(AgentStatus), nullable=False, default=AgentStatus.OBSERVING)
    
    # Risk Context
    current_risk_score = Column(Float, nullable=False)
    risk_trend = Column(String(50), nullable=True)  # increasing, stable, decreasing
    risk_velocity = Column(Float, nullable=True)  # Rate of change
    
    # Goals
    goal = Column(Text, nullable=False)
    target_risk_score = Column(Float, nullable=True)
    target_deadline = Column(DateTime, nullable=True)
    
    # Agent Memory (JSON)
    observations = Column(JSON, nullable=True)
    hypotheses = Column(JSON, nullable=True)
    context = Column(JSON, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_action_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student")
    intervention_plans = relationship("InterventionPlan", back_populates="session")

class InterventionPlan(Base):
    """Agent-generated intervention plans"""
    __tablename__ = "intervention_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("agent_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Plan Details
    plan_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Agent Reasoning
    reasoning = Column(JSON, nullable=False)  # Why this plan
    identified_causes = Column(JSON, nullable=True)  # Root causes
    expected_outcome = Column(Text, nullable=True)
    
    # Approval
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_status = Column(SQLEnum(InterventionStatus), default=InterventionStatus.PENDING_APPROVAL)
    approval_notes = Column(Text, nullable=True)
    
    # Priority & Timing
    priority = Column(Integer, default=1)  # 1-5
    estimated_duration_days = Column(Integer, nullable=True)
    
    # Success Criteria
    success_metrics = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("AgentSession", back_populates="intervention_plans")
    actions = relationship("AgentAction", back_populates="plan")
    outcomes = relationship("InterventionOutcome", back_populates="plan")

class AgentAction(Base):
    """Individual actions in an intervention plan"""
    __tablename__ = "agent_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("intervention_plans.id"), nullable=False)
    
    # Action Details
    action_id = Column(String(100), unique=True, nullable=False)
    action_type = Column(SQLEnum(InterventionType), nullable=False)
    sequence_order = Column(Integer, nullable=False)  # Order in plan
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Tool/Agent Assignment
    delegated_to = Column(String(100), nullable=False)  # Which sub-agent
    tool_parameters = Column(JSON, nullable=True)
    
    # Execution
    status = Column(SQLEnum(ActionStatus), default=ActionStatus.PENDING)
    execution_log = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Dependencies
    depends_on_action_id = Column(Integer, ForeignKey("agent_actions.id"), nullable=True)
    
    # Results
    result_data = Column(JSON, nullable=True)
    success = Column(Boolean, nullable=True)
    
    # Timestamps
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    plan = relationship("InterventionPlan", back_populates="actions")

class InterventionOutcome(Base):
    """Verification of intervention results"""
    __tablename__ = "intervention_outcomes"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("intervention_plans.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Outcome Metrics
    risk_score_before = Column(Float, nullable=False)
    risk_score_after = Column(Float, nullable=True)
    risk_reduction = Column(Float, nullable=True)
    
    # Verification Checks
    student_responded = Column(Boolean, default=False)
    engagement_improved = Column(Boolean, nullable=True)
    chat_sentiment_delta = Column(Float, nullable=True)
    
    # Success Indicators
    goals_achieved = Column(JSON, nullable=True)
    success_rate = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Agent Learning
    effectiveness_score = Column(Float, nullable=True)
    lessons_learned = Column(JSON, nullable=True)
    recommended_adjustments = Column(JSON, nullable=True)
    
    # Next Steps
    requires_plan_b = Column(Boolean, default=False)
    escalation_needed = Column(Boolean, default=False)
    
    # Timestamps
    measured_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plan = relationship("InterventionPlan", back_populates="outcomes")

class AgentObservation(Base):
    """Continuous monitoring observations"""
    __tablename__ = "agent_observations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    observation_type = Column(String(100), nullable=False)
    
    # Observation Data
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=True)
    metric_text = Column(Text, nullable=True)
    
    # Context
    context_data = Column(JSON, nullable=True)
    anomaly_detected = Column(Boolean, default=False)
    severity = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Patterns
    pattern_type = Column(String(100), nullable=True)  # trend, spike, drift, etc.
    
    observed_at = Column(DateTime, default=datetime.utcnow)

class GovConnectSignal(Base):
    """Aggregated signals for policy makers"""
    __tablename__ = "govconnect_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Signal Details
    signal_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Data
    affected_student_count = Column(Integer, nullable=False)
    region = Column(String(100), nullable=True)
    institution = Column(String(255), nullable=True)
    
    # Metrics
    dropout_correlation = Column(Float, nullable=True)
    urgency_score = Column(Float, nullable=False)
    
    # Policy Recommendation
    recommended_action = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=False)
    
    # Status
    reported_to_authorities = Column(Boolean, default=False)
    acknowledged = Column(Boolean, default=False)
    
    # Timestamps
    identified_at = Column(DateTime, default=datetime.utcnow)
    reported_at = Column(DateTime, nullable=True)
