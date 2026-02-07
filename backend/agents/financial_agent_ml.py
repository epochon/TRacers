"""
Financial Agent with ML, RAG, and LLM
Detects financial bureaucratic friction using machine learning
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


class FinancialAgentML:
    """
    Financial friction agent with ML model, RAG, and LLM reasoning.
    """
    
    def __init__(self):
        self.name = "FinancialAgent"
        self.weight = 0.25
        
        # Domain-specific event types
        self.domain_types = [
            'scholarship_delay',
            'fee_payment',
            'financial_aid',
            'account_hold'
        ]
        
        # ML Model
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.model_trained = False
        
        # RAG System
        self.rag = DomainRAG('financial')
        
        # LLM
        self.llm = get_llm()
        
        # Try to load pre-trained model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if available."""
        model_path = 'models/financial_agent.pkl'
        scaler_path = 'models/financial_scaler.pkl'
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.model_trained = True
                print(f"{self.name}: Loaded pre-trained model")
            except Exception as e:
                print(f"{self.name}: Could not load model: {e}")
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Train the ML model.
        
        Args:
            X: Feature matrix
            y: Labels
        """
        if len(X) < 2:
            print(f"{self.name}: Insufficient data for training")
            return
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.model_trained = True
        
        print(f"{self.name}: Model trained on {len(X)} samples")
    
    def save_model(self):
        """Save trained model to disk."""
        os.makedirs('models', exist_ok=True)
        
        with open('models/financial_agent.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        with open('models/financial_scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"{self.name}: Model saved")
    
    def evaluate(self, events: List[StudentEvent]) -> Dict:
        """
        Evaluate financial friction with ML + RAG + LLM.
        
        Args:
            events: List of all student events
            
        Returns:
            Dictionary with risk, confidence, and reasoning
        """
        # Filter domain-specific events
        financial_events = [e for e in events if e.event_type in self.domain_types]
        
        # Extract features
        features = extract_domain_features(events, self.domain_types)
        
        # ML Prediction
        if self.model_trained and len(features) > 0:
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            risk_prob = self.model.predict_proba(features_scaled)[0][1]
            ml_confidence = max(self.model.predict_proba(features_scaled)[0])
        else:
            # Fallback to heuristic
            risk_prob = self._heuristic_risk(financial_events)
            ml_confidence = 0.6
        
        # RAG Context Retrieval
        query = f"Financial events: {len(financial_events)} events with average severity {features[1]:.2f}"
        rag_context = self.rag.retrieve_context(query, top_k=2)
        
        # LLM Reasoning
        feature_dict = {
            'event_count': int(features[0]),
            'avg_severity': float(features[1]),
            'max_severity': float(features[2]),
            'recent_events': len([e for e in financial_events if (np.datetime64('now') - np.datetime64(e.timestamp)).astype('timedelta64[D]').astype(int) < 30])
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
                'max_severity': round(float(features[2]), 3),
                'ml_prediction': round(float(risk_prob), 3),
                'rag_context_used': True
            }
        }
    
    def _heuristic_risk(self, events: List[StudentEvent]) -> float:
        """Fallback heuristic risk calculation."""
        if not events:
            return 0.0
        
        event_count = len(events)
        avg_severity = sum(e.severity for e in events) / event_count
        
        # Simple heuristic
        frequency_factor = min(event_count / 5.0, 1.0)
        severity_factor = avg_severity
        
        return (frequency_factor * 0.4 + severity_factor * 0.6)
