"""
Additional Database Models for Senior Chat and GovConnect
Add these to your existing models.py file
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class StudentProfile(Base):
    """
    Student profile for senior chat matching
    Stores course and batch information
    """
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), unique=True)
    course = Column(String(100))
    batch = Column(String(10))
    matched_senior_id = Column(String(50), nullable=True)
    session_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    student = relationship("User", back_populates="profile")


class SeniorChatMessage(Base):
    """
    Message history for senior chat sessions
    """
    __tablename__ = "senior_chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    senior_id = Column(String(50))
    sender = Column(String(20))  # 'student' or 'senior'
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    student = relationship("User", foreign_keys=[student_id])


class GovConnectTicket(Base):
    """
    Tickets for GovConnect system
    """
    __tablename__ = "gov_connect_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    category = Column(String(50))
    subject = Column(String(200))
    description = Column(Text)
    status = Column(String(20), default='open')  # 'open', 'in_progress', 'closed'
    assigned_to = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationship
    student = relationship("User", back_populates="gov_tickets")
    messages = relationship("GovConnectMessage", back_populates="ticket", cascade="all, delete-orphan")


class GovConnectMessage(Base):
    """
    Message history for GovConnect tickets
    """
    __tablename__ = "gov_connect_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), ForeignKey('gov_connect_tickets.ticket_id'))
    sender = Column(String(20))  # 'student' or 'government'
    sender_id = Column(String(50))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    ticket = relationship("GovConnectTicket", back_populates="messages")


# Add these relationships to your existing User model:
# 
# profile = relationship("StudentProfile", back_populates="student", uselist=False)
# gov_tickets = relationship("GovConnectTicket", back_populates="student")