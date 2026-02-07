"""
RAG (Retrieval-Augmented Generation) Utility for TRACE-AI
Uses FAISS for vector search and sentence-transformers for embeddings
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import faiss


class RAGSystem:
    """
    Retrieval-Augmented Generation system using FAISS and sentence-transformers.
    """
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        index_path: Optional[str] = None
    ):
        """
        Initialize RAG system.
        
        Args:
            embedding_model: SentenceTransformer model name
            index_path: Path to save/load FAISS index
        """
        self.embedding_model_name = embedding_model
        self.encoder = None
        self.index = None
        self.documents = []
        self.index_path = index_path
        self._load_encoder()
    
    def _load_encoder(self):
        """Lazy load the sentence transformer model."""
        if self.encoder is None:
            print(f"Loading embedding model: {self.embedding_model_name}")
            self.encoder = SentenceTransformer(self.embedding_model_name)
            print("Embedding model loaded")
    
    def add_documents(self, documents: List[str]):
        """
        Add documents to the RAG system and build FAISS index.
        
        Args:
            documents: List of text documents
        """
        if not documents:
            return
        
        self.documents.extend(documents)
        
        # Encode documents
        print(f"Encoding {len(documents)} documents...")
        embeddings = self.encoder.encode(documents, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Build or update FAISS index
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        
        self.index.add(embeddings)
        print(f"Index now contains {self.index.ntotal} documents")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            
        Returns:
            List of dictionaries with 'text' and 'score' keys
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Encode query
        query_embedding = self.encoder.encode([query], show_progress_bar=False)
        query_embedding = np.array(query_embedding).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                results.append({
                    'text': self.documents[idx],
                    'score': float(score)
                })
        
        return results
    
    def save_index(self, path: Optional[str] = None):
        """
        Save FAISS index and documents to disk.
        
        Args:
            path: Path to save (uses self.index_path if not provided)
        """
        save_path = path or self.index_path
        if save_path is None:
            raise ValueError("No save path specified")
        
        # Save FAISS index
        faiss.write_index(self.index, f"{save_path}.index")
        
        # Save documents
        with open(f"{save_path}.docs", 'wb') as f:
            pickle.dump(self.documents, f)
        
        print(f"Index saved to {save_path}")
    
    def load_index(self, path: Optional[str] = None):
        """
        Load FAISS index and documents from disk.
        
        Args:
            path: Path to load (uses self.index_path if not provided)
        """
        load_path = path or self.index_path
        if load_path is None:
            raise ValueError("No load path specified")
        
        # Load FAISS index
        self.index = faiss.read_index(f"{load_path}.index")
        
        # Load documents
        with open(f"{load_path}.docs", 'rb') as f:
            self.documents = pickle.load(f)
        
        print(f"Index loaded from {load_path} ({self.index.ntotal} documents)")


class DomainRAG:
    """
    Domain-specific RAG system with pre-loaded knowledge.
    """
    
    def __init__(self, domain: str):
        """
        Initialize domain-specific RAG.
        
        Args:
            domain: Domain name (financial, academic, residential, language)
        """
        self.domain = domain
        self.rag = RAGSystem(index_path=f"data/rag_{domain}")
        self._load_domain_knowledge()
    
    def _load_domain_knowledge(self):
        """Load domain-specific knowledge documents."""
        knowledge = self._get_domain_knowledge()
        self.rag.add_documents(knowledge)
    
    def _get_domain_knowledge(self) -> List[str]:
        """
        Get domain-specific knowledge documents.
        
        Returns:
            List of knowledge documents
        """
        knowledge_base = {
            'financial': [
                "Scholarship delays can compound into housing and food insecurity issues.",
                "Fee payment processing errors often create cascading administrative holds.",
                "Financial aid verification loops can trap students in bureaucratic cycles.",
                "Students from low-income backgrounds face higher friction from payment delays.",
                "Emergency financial aid typically takes 2-4 weeks to process.",
                "Account holds prevent registration and access to academic resources.",
                "Scholarship disbursement delays average 3-6 weeks in most institutions.",
                "Financial stress correlates strongly with academic performance decline.",
            ],
            'academic': [
                "Attendance penalties due to documentation issues are bureaucratic, not educational.",
                "Conflicting deadline requirements indicate systemic process failures.",
                "Administrative warnings often stem from institutional friction, not student failure.",
                "Registration blocks can prevent students from continuing their education.",
                "Course drop deadlines vary across departments, creating confusion.",
                "Academic holds are often administrative rather than performance-based.",
                "Documentation requirements for medical absences vary inconsistently.",
                "Grade posting delays can affect scholarship eligibility determinations.",
            ],
            'residential': [
                "Hostel access revocation threatens basic housing security.",
                "Mess card suspensions directly impact student nutrition and wellbeing.",
                "Room reassignment delays create housing instability during critical periods.",
                "Amenity restrictions compound stress during academic pressure periods.",
                "Housing allocation errors disproportionately affect first-generation students.",
                "Hostel fee payment issues often stem from scholarship disbursement delays.",
                "Basic needs security (housing, food) is fundamental to academic success.",
                "Residential friction creates compounding stress that affects all life areas.",
            ],
            'language': [
                "Language barriers in administrative processes create systemic exclusion.",
                "Form confusion often indicates institutional language mismatch, not student capability.",
                "Communication issues with administration compound other bureaucratic friction.",
                "Multilingual support reduces dropout rates significantly.",
                "Documentation in non-native languages increases processing errors.",
                "Language barriers cascade into financial and academic friction.",
                "Translation services are often unavailable for critical administrative processes.",
                "First-generation students face higher language-related administrative barriers.",
            ],
            'ethics': [
                "Automated systems must not stigmatize or label students.",
                "Human dignity requires consent-based intervention approaches.",
                "Demographic bias in risk assessment violates ethical principles.",
                "Uncertainty must be acknowledged explicitly in automated decisions.",
                "Basic needs threats require immediate human escalation.",
                "Privacy and anonymity are fundamental student rights.",
                "Punitive actions have no place in support systems.",
                "Transparency in algorithmic decision-making builds trust.",
            ],
            'uncertainty': [
                "Sparse data requires conservative risk estimates and human oversight.",
                "Conflicting agent signals indicate epistemic uncertainty.",
                "Stale information reduces confidence in risk assessments.",
                "High variance between agents suggests complex, ambiguous situations.",
                "Uncertainty increases with data sparsity and recency gaps.",
                "Bayesian approaches help quantify epistemic uncertainty.",
                "Human judgment is essential when uncertainty is high.",
                "Confidence intervals should widen with limited data.",
            ]
        }
        
        return knowledge_base.get(self.domain, [])
    
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            
        Returns:
            Concatenated context string
        """
        results = self.rag.retrieve(query, top_k=top_k)
        
        if not results:
            return "No relevant context available."
        
        context_parts = [f"- {r['text']}" for r in results]
        return "\n".join(context_parts)
