import re
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher
from utils.logger import get_logger

logger = get_logger(__name__)

class HallucinationDetector:
    
    @staticmethod
    def check_grounding(
        generated_text: str,
        source_documents: List[Dict[str, Any]]
    ) -> Tuple[bool, float, List[str]]:
        
        if not source_documents:
            return False, 0.0, ["No source documents to verify against"]
        
        source_text = " ".join([doc.get('content', '') for doc in source_documents])
        
        generated_sentences = HallucinationDetector._split_sentences(generated_text)
        
        grounded_count = 0
        ungrounded = []
        
        for sentence in generated_sentences:
            if len(sentence.strip()) < 10:
                continue
            
            is_grounded = HallucinationDetector._is_sentence_grounded(
                sentence,
                source_text
            )
            
            if is_grounded:
                grounded_count += 1
            else:
                ungrounded.append(sentence[:100])
        
        total_sentences = len([s for s in generated_sentences if len(s.strip()) >= 10])
        grounding_score = grounded_count / total_sentences if total_sentences > 0 else 0.0
        
        is_grounded = grounding_score >= 0.7
        
        warnings = []
        if not is_grounded:
            warnings.append(f"Low grounding score: {grounding_score:.2f}")
            warnings.append(f"Found {len(ungrounded)} potentially hallucinated sentences")
        
        logger.debug(f"Grounding check: {is_grounded} (score: {grounding_score:.2f})")
        return is_grounded, grounding_score, warnings
    
    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def _is_sentence_grounded(sentence: str, source_text: str, threshold: float = 0.6) -> bool:
        
        sentence_lower = sentence.lower()
        source_lower = source_text.lower()
        
        sentence_words = set(re.findall(r'\b\w+\b', sentence_lower))
        source_words = set(re.findall(r'\b\w+\b', source_lower))
        
        common_stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        sentence_words -= common_stopwords
        source_words -= common_stopwords
        
        if not sentence_words:
            return True
        
        overlap = len(sentence_words & source_words) / len(sentence_words)
        
        if overlap >= threshold:
            return True
        
        sentence_chunks = [sentence_lower[i:i+50] for i in range(0, len(sentence_lower), 25)]
        source_chunks = [source_lower[i:i+50] for i in range(0, len(source_lower), 25)]
        
        max_similarity = 0.0
        for sc in sentence_chunks:
            for src_c in source_chunks:
                sim = SequenceMatcher(None, sc, src_c).ratio()
                max_similarity = max(max_similarity, sim)
        
        return max_similarity >= 0.7
    
    @staticmethod
    def detect_contradictions(
        generated_text: str,
        source_documents: List[Dict[str, Any]]
    ) -> List[str]:
        
        contradictions = []
        
        return contradictions