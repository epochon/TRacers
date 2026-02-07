"""
Feature Extraction Module for TRACE-AI
Extracts numerical features from student events for ML models
"""

import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from models import StudentEvent


def extract_features(events: List[StudentEvent]) -> np.ndarray:
    """
    Extract numerical features from student events.
    
    Features:
    - event_count: Total number of events
    - avg_severity: Average severity across all events
    - max_severity: Maximum severity observed
    - severity_std: Standard deviation of severity
    - avg_days_since_event: Average days since events occurred
    - max_days_since_event: Maximum days since any event
    
    Args:
        events: List of StudentEvent objects
        
    Returns:
        NumPy array of shape (6,) containing extracted features
    """
    if not events:
        # Return zero features if no events
        return np.zeros(6)
    
    # Extract severity values
    severities = [e.severity for e in events]
    
    # Calculate time-based features
    now = datetime.utcnow()
    days_since = [(now - e.timestamp).days for e in events]
    
    # Feature 1: Event count
    event_count = len(events)
    
    # Feature 2: Average severity
    avg_severity = np.mean(severities)
    
    # Feature 3: Maximum severity
    max_severity = np.max(severities)
    
    # Feature 4: Severity standard deviation
    severity_std = np.std(severities) if len(severities) > 1 else 0.0
    
    # Feature 5: Average days since event
    avg_days_since = np.mean(days_since)
    
    # Feature 6: Maximum days since event
    max_days_since = np.max(days_since)
    
    features = np.array([
        event_count,
        avg_severity,
        max_severity,
        severity_std,
        avg_days_since,
        max_days_since
    ])
    
    return features


def extract_domain_features(events: List[StudentEvent], domain_types: List[str]) -> np.ndarray:
    """
    Extract features for a specific domain (e.g., financial, academic).
    
    Args:
        events: List of all student events
        domain_types: List of event types relevant to this domain
        
    Returns:
        NumPy array of domain-specific features
    """
    # Filter events by domain
    domain_events = [e for e in events if e.event_type in domain_types]
    
    # Extract features from domain-specific events
    return extract_features(domain_events)


def get_event_type_distribution(events: List[StudentEvent]) -> Dict[str, int]:
    """
    Get distribution of event types.
    
    Args:
        events: List of StudentEvent objects
        
    Returns:
        Dictionary mapping event types to counts
    """
    distribution = {}
    for event in events:
        event_type = event.event_type
        distribution[event_type] = distribution.get(event_type, 0) + 1
    
    return distribution


def calculate_event_velocity(events: List[StudentEvent], window_days: int = 30) -> float:
    """
    Calculate the velocity of events (events per day) in recent window.
    
    Args:
        events: List of StudentEvent objects
        window_days: Number of days to look back
        
    Returns:
        Events per day in the window
    """
    if not events:
        return 0.0
    
    now = datetime.utcnow()
    recent_events = [
        e for e in events 
        if (now - e.timestamp).days <= window_days
    ]
    
    if not recent_events:
        return 0.0
    
    return len(recent_events) / window_days


def detect_event_clustering(events: List[StudentEvent], cluster_window_days: int = 14) -> int:
    """
    Detect if events are clustered in time (indicates compounding issues).
    
    Args:
        events: List of StudentEvent objects
        cluster_window_days: Window to consider events as clustered
        
    Returns:
        Number of event clusters detected
    """
    if len(events) < 2:
        return 0
    
    # Sort events by timestamp
    sorted_events = sorted(events, key=lambda x: x.timestamp)
    
    clusters = 0
    for i in range(len(sorted_events) - 1):
        time_diff = (sorted_events[i + 1].timestamp - sorted_events[i].timestamp).days
        if time_diff <= cluster_window_days:
            clusters += 1
    
    return clusters
