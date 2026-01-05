from typing import List, Dict, Any, Tuple
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class ConfidenceChecker:
    
    def __init__(self, threshold: float = None):
        self.threshold = threshold or settings.confidence_threshold
    
    def check_retrieval_confidence(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> Tuple[bool, float, List[str]]:
        
        if not retrieved_docs:
            return False, 0.0, ["No relevant documents found"]
        
        scores = [doc.get('score', 0.0) for doc in retrieved_docs]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        warnings = []
        
        if avg_score < self.threshold:
            warnings.append(f"Low retrieval confidence ({avg_score:.2f} < {self.threshold})")
        
        if len(retrieved_docs) < 3:
            warnings.append(f"Limited evidence: only {len(retrieved_docs)} documents retrieved")
        
        top_score = scores[0] if scores else 0.0
        if top_score < 0.4:
            warnings.append(f"Best match has low score: {top_score:.2f}")
        
        is_confident = avg_score >= self.threshold and not warnings
        
        logger.debug(f"Confidence check: {is_confident} (score: {avg_score:.2f})")
        return is_confident, avg_score, warnings
    
    def suggest_clarifications(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        warnings: List[str]
    ) -> List[str]:
        
        suggestions = []
        
        if not retrieved_docs:
            suggestions.append("Could you provide more specific details about the feature or functionality?")
            suggestions.append("Which specific aspect of the system should I focus on?")
            return suggestions
        
        if "Low retrieval confidence" in ' '.join(warnings):
            suggestions.append("The available documentation may not cover this topic in detail. Could you:")
            suggestions.append("  - Rephrase your question with different keywords?")
            suggestions.append("  - Provide more context about what you're looking for?")
        
        if "Limited evidence" in ' '.join(warnings):
            suggestions.append("I found limited information. Consider:")
            suggestions.append("  - Breaking down your query into smaller parts")
            suggestions.append("  - Checking if relevant documents are in the knowledge base")
        
        return suggestions
    
    def generate_assumptions_needed(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> List[str]:
        
        assumptions = []
        
        query_lower = query.lower()
        
        if 'signup' in query_lower or 'registration' in query_lower:
            if not any('email' in doc['content'].lower() for doc in retrieved_docs):
                assumptions.append("Assuming email-based registration")
            if not any('password' in doc['content'].lower() for doc in retrieved_docs):
                assumptions.append("Assuming password requirements exist but are not specified")
        
        if 'api' in query_lower:
            if not any('endpoint' in doc['content'].lower() for doc in retrieved_docs):
                assumptions.append("Assuming standard REST API endpoints")
        
        if 'ui' in query_lower or 'interface' in query_lower:
            if not any('button' in doc['content'].lower() or 'form' in doc['content'].lower() for doc in retrieved_docs):
                assumptions.append("Assuming standard UI elements (forms, buttons)")
        
        return assumptions