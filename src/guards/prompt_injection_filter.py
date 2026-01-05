import re
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class PromptInjectionFilter:
    
    INJECTION_INDICATORS = [
        "ignore previous instructions",
        "disregard above",
        "forget all instructions",
        "new task:",
        "system:",
        "you are now",
        "act as",
        "pretend you are",
        "roleplay",
        "override your programming",
        "you must",
        "from now on",
    ]
    
    @staticmethod
    def sanitize_document_content(content: str) -> str:
        
        lines = content.split('\n')
        clean_lines = []
        
        for line in lines:
            line_lower = line.lower()
            
            is_suspicious = False
            for indicator in PromptInjectionFilter.INJECTION_INDICATORS:
                if indicator in line_lower:
                    is_suspicious = True
                    logger.warning(f"Removed suspicious line from document: {line[:50]}...")
                    break
            
            if not is_suspicious:
                clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    @staticmethod
    def filter_retrieved_documents(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        
        filtered = []
        
        for doc in docs:
            content = doc.get('content', '')
            clean_content = PromptInjectionFilter.sanitize_document_content(content)
            
            if clean_content.strip():
                doc_copy = doc.copy()
                doc_copy['content'] = clean_content
                filtered.append(doc_copy)
        
        removed = len(docs) - len(filtered)
        if removed > 0:
            logger.info(f"Filtered out {removed} documents with injection attempts")
        
        return filtered
    
    @staticmethod
    def detect_injection_in_query(query: str) -> bool:
        
        query_lower = query.lower()
        
        for indicator in PromptInjectionFilter.INJECTION_INDICATORS:
            if indicator in query_lower:
                logger.warning(f"Injection detected in query: {indicator}")
                return True
        
        patterns = [
            r'<\s*system\s*>',
            r'\[\s*system\s*\]',
            r'```\s*system',
            r'###\s*instruction',
        ]
        
        for pattern in patterns:
            if re.search(pattern, query_lower):
                logger.warning(f"Injection pattern detected: {pattern}")
                return True
        
        return False