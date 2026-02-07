"""SQLAlchemy ORM models used by the backend routes and utilities."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=False, default='student')
    created_at = Column(DateTime, default=datetime.utcnow)


class StudentEvent(Base):
    __tablename__ = 'student_events'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    event_type = Column(String, nullable=False)
    severity = Column(Float, default=0.0)
    description = Column(Text, default='')
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    meta = Column(Text, default='')

    student = relationship('User')


class AgentOutput(Base):
    __tablename__ = 'agent_outputs'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    agent_name = Column(String, nullable=False)
    risk_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.5)
    comment = Column(Text, default='')
    analysis_data = Column(Text, default='')
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    student = relationship('User')


class CoordinatorDecision(Base):
    __tablename__ = 'coordinator_decisions'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    decision = Column(String, nullable=False)
    justification = Column(Text, default='')
    ethics_veto = Column(Boolean, default=False)
    aggregate_risk = Column(Float, default=0.0)
    uncertainty_level = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    aggregate_risk = Column(Float)
    uncertainty_level = Column(Float)
    meta_data = Column(JSON) # Stores distance_to_irreversibility, headline, etc.

    student = relationship('User')


class CounselorEscalation(Base):
    __tablename__ = 'counselor_escalations'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String, nullable=True)
    counselor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String, default='pending')
    consent_given = Column(Boolean, default=False)
    reason = Column(Text, default='')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    student = relationship('User', foreign_keys=[student_id])
    counselor = relationship('User', foreign_keys=[counselor_id])


class SystemInsight(Base):
    __tablename__ = 'system_insights'

    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String, nullable=False)
    description = Column(Text, default='')
    affected_count = Column(Integer, default=0)
    severity = Column(Float, default=0.0)
    metadata_text = Column(Text, default='')
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
