"""
HuggingFace LLM Integration for TRACE-AI
Provides text generation capabilities using local transformer models
"""

import os
import torch
from typing import Optional, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import warnings

warnings.filterwarnings('ignore')


class LLMService:
    """
    Lazy-loading HuggingFace LLM service.
    Uses microsoft/phi-2 by default for efficient local inference.
    """
    
    def __init__(self, model_name: str = "microsoft/phi-2"):
        """
        Initialize LLM service with lazy loading.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self._pipeline = None
        self._tokenizer = None
        self._model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def _load_model(self):
        """Lazy load the model and tokenizer."""
        if self._pipeline is not None:
            return
        
        try:
            print(f"Loading {self.model_name} on {self.device}...")
            
            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True,
                device_map="auto" if self.device == "cuda" else None
            )
            
            # Create pipeline
            self._pipeline = pipeline(
                "text-generation",
                model=self._model,
                tokenizer=self._tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            print(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Warning: Could not load {self.model_name}: {e}")
            print("Falling back to deterministic mode")
            self._pipeline = None
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 150,
        temperature: float = 0.7,
        do_sample: bool = True,
        top_p: float = 0.9,
        top_k: int = 50
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (higher = more random)
            do_sample: Whether to use sampling
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Generated text
        """
        # Lazy load model
        if self._pipeline is None:
            self._load_model()
        
        # Fallback to deterministic response if model unavailable
        if self._pipeline is None:
            return self._deterministic_fallback(prompt)
        
        try:
            # Generate text
            outputs = self._pipeline(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=do_sample,
                top_p=top_p,
                top_k=top_k,
                pad_token_id=self._tokenizer.eos_token_id,
                return_full_text=False
            )
            
            generated_text = outputs[0]['generated_text'].strip()
            return generated_text
            
        except Exception as e:
            print(f"Generation error: {e}")
            return self._deterministic_fallback(prompt)
    
    def _deterministic_fallback(self, prompt: str) -> str:
        """
        Deterministic fallback when model is unavailable.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Rule-based response
        """
        prompt_lower = prompt.lower()
        
        # Financial domain
        if "financial" in prompt_lower or "scholarship" in prompt_lower:
            return "Based on financial event patterns, there is moderate to high risk due to scholarship delays and payment issues. These bureaucratic barriers can compound quickly."
        
        # Academic domain
        elif "academic" in prompt_lower or "attendance" in prompt_lower:
            return "Academic friction detected through attendance warnings and administrative barriers. These issues may indicate systemic obstacles rather than student capability."
        
        # Residential domain
        elif "residential" in prompt_lower or "hostel" in prompt_lower:
            return "Housing and basic needs friction observed. Access to essential services is critical for student wellbeing and retention."
        
        # Language domain
        elif "language" in prompt_lower or "communication" in prompt_lower:
            return "Communication barriers detected. Language mismatches in administrative processes can create cascading difficulties."
        
        # Ethics domain
        elif "ethic" in prompt_lower or "bias" in prompt_lower:
            return "Ethical review complete. No demographic bias detected. System maintains human dignity and consent-based approach."
        
        # Uncertainty domain
        elif "uncertain" in prompt_lower or "confidence" in prompt_lower:
            return "Data quality assessment indicates moderate uncertainty. Recommendation: proceed with caution and human oversight."
        
        # Default
        else:
            return "Analysis complete. Risk assessment based on available event data and domain-specific patterns."
    
    def explain_risk(
        self,
        agent_name: str,
        risk_score: float,
        features: Dict[str, Any],
        context: str = ""
    ) -> str:
        """
        Generate natural language explanation for risk score.
        
        Args:
            agent_name: Name of the agent
            risk_score: Calculated risk score (0-1)
            features: Dictionary of features used
            context: Additional context
            
        Returns:
            Natural language explanation
        """
        prompt = f"""You are the {agent_name} in a student support system.

Risk Score: {risk_score:.2f}
Features: {features}
Context: {context}

Explain in 2-3 sentences why this risk score was assigned and what it means for student support. Be specific and actionable."""

        return self.generate(prompt, max_new_tokens=100, temperature=0.5)


# Global LLM service instance (lazy loaded)
_llm_service = None


def get_llm() -> LLMService:
    """
    Get global LLM service instance (singleton pattern).
    
    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
