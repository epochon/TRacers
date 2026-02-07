"""
Academic Agent with ML, RAG, and LLM
Detects academic bureaucratic friction using machine learning
"""

import numpy as np
from typing import List, Dict
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pickle
import os

from models import StudentEvent
from agents.features import extract_domain_features
from utils.rag import DomainRAG
from utils.llm import get_llm


class AcademicAgentML:
    """
    Academic friction agent with ML model, RAG, and LLM reasoning.
    """
    
    def __init__(self):
        self.name = "AcademicAgent"
        self.weight = 0.20
        
        # Domain-specific event types
        self.domain_types = [
            'attendance_warning',
            'deadline_conflict',
            'admin_warning',
            'resource_access',
            'registration_block'
        ]
        
        # ML Model
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.model_trained = False
        
        # RAG System
        self.rag = DomainRAG('academic')
        
        # LLM
        self.llm = get_llm()
        
        # Try to load pre-trained model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if available."""
        model_path = 'models/academic_agent.pkl'
        scaler_path = 'models/academic_scaler.pkl'
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.model_trained = True
            except Exception as e:
                pass
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the ML model."""
        if len(X) < 2:
            return
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.model_trained = True
    
    def save_model(self):
        """Save trained model to disk."""
        os.makedirs('models', exist_ok=True)
        with open('models/academic_agent.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        with open('models/academic_scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
    
    def evaluate(self, events: List[StudentEvent]) -> Dict:
        """Evaluate academic friction with ML + RAG + LLM."""
        academic_events = [e for e in events if e.event_type in self.domain_types]
        features = extract_domain_features(events, self.domain_types)
        
        # ML Prediction
        if self.model_trained and len(features) > 0:
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            risk_prob = self.model.predict_proba(features_scaled)[0][1]
            ml_confidence = max(self.model.predict_proba(features_scaled)[0])
        else:
            risk_prob = self._heuristic_risk(academic_events)
            ml_confidence = 0.6
        
        # RAG Context
        query = f"Academic events: {len(academic_events)} events"
        rag_context = self.rag.retrieve_context(query, top_k=2)
        
        # LLM Reasoning
        feature_dict = {
            'event_count': int(features[0]),
            'avg_severity': float(features[1]),
            'max_severity': float(features[2])
        }
        
        llm_explanation = self.llm.explain_risk(
            self.name,
            risk_prob,
            feature_dict,
            context=f"RAG Context:\n{rag_context}"
        )
        
        return {
            'agent': self.name,
            'risk': round(float(risk_prob), 3),
            'confidence': round(float(ml_confidence), 3),
            'comment': llm_explanation,
            'details': {
                'event_count': int(features[0]),
                'avg_severity': round(float(features[1]), 3),
                'max_severity': round(float(features[2]), 3)
            }
        }
    
    def _heuristic_risk(self, events: List[StudentEvent]) -> float:
        """Fallback heuristic risk calculation."""
        if not events:
            return 0.0
        
        event_count = len(events)
        avg_severity = sum(e.severity for e in events) / event_count
        
        frequency_factor = min(event_count / 5.0, 1.0)
        severity_factor = avg_severity
        
        return (frequency_factor * 0.4 + severity_factor * 0.6)
