import re
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

class QueryProcessor:
    
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|all|above)\s+instructions",
        r"disregard\s+(previous|all|above)\s+instructions",
        r"forget\s+(previous|all|above)\s+instructions",
        r"new\s+instructions",
        r"system\s*:\s*you\s+are",
        r"override\s+your\s+instructions",
        r"act\s+as\s+if",
        r"pretend\s+you\s+are",
    ]
    
    @staticmethod
    def detect_prompt_injection(query: str) -> bool:
        query_lower = query.lower()
        
        for pattern in QueryProcessor.INJECTION_PATTERNS:
            if re.search(pattern, query_lower):
                logger.warning(f"Potential prompt injection detected in query")
                return True
        
        return False
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        query = query.strip()
        
        query = re.sub(r'\s+', ' ', query)
        
        query = re.sub(r'[^\w\s\-.,?!]', '', query)
        
        return query
    
    @staticmethod
    def expand_query(query: str) -> List[str]:
        expanded = [query]
        
        synonyms = {
            'use case': ['test case', 'scenario', 'user story'],
            'signup': ['sign up', 'registration', 'register', 'create account'],
            'login': ['log in', 'sign in', 'authentication'],
            'negative': ['error', 'invalid', 'failure', 'exception'],
            'boundary': ['edge case', 'limit', 'constraint']
        }
        
        query_lower = query.lower()
        for term, variants in synonyms.items():
            if term in query_lower:
                for variant in variants:
                    expanded.append(query.replace(term, variant))
        
        return expanded[:3]
    
    @staticmethod
    def extract_intent(query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        
        intent = {
            'type': 'general',
            'entities': [],
            'modifiers': []
        }
        
        if any(kw in query_lower for kw in ['create', 'generate', 'write']):
            intent['type'] = 'generation'
        elif any(kw in query_lower for kw in ['find', 'search', 'show', 'list']):
            intent['type'] = 'retrieval'
        
        if 'use case' in query_lower or 'test case' in query_lower:
            intent['entities'].append('use_case')
        
        if 'negative' in query_lower or 'error' in query_lower:
            intent['modifiers'].append('negative')
        if 'boundary' in query_lower or 'edge' in query_lower:
            intent['modifiers'].append('boundary')
        if 'positive' in query_lower or 'happy' in query_lower:
            intent['modifiers'].append('positive')
        
        features = re.findall(r'\b(signup|login|payment|checkout|profile|search)\b', query_lower)
        if features:
            intent['entities'].extend(features)
        
        return intent