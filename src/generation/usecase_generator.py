import json
import re
from typing import Dict, Any, List
from generation.llm_client import LLMClient
from generation.prompt_builder import PromptBuilder
from retriever.hybrid_retriever import HybridRetriever
from retriever.query_processor import QueryProcessor
from guards.confidence_checker import ConfidenceChecker
from guards.prompt_injection_filter import PromptInjectionFilter
from guards.deduplicator import Deduplicator
from guards.hallucination_detector import HallucinationDetector
from utils.logger import get_logger
from utils.metrics import metrics_collector
from utils.validators import sanitize_output

logger = get_logger(__name__)

class UseCaseGenerator:
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompt_builder = PromptBuilder()
        self.retriever = HybridRetriever()
        self.query_processor = QueryProcessor()
        self.confidence_checker = ConfidenceChecker()
        self.injection_filter = PromptInjectionFilter()
        self.deduplicator = Deduplicator()
        self.hallucination_detector = HallucinationDetector()
    
    def generate(self, query: str, debug_mode: bool = False) -> Dict[str, Any]:
        
        metric = metrics_collector.track("full_generation")
        
        logger.info(f"Processing query: {query}")
        
        if self.injection_filter.detect_injection_in_query(query):
            logger.warning("Potential injection detected in query, rejecting")
            return {
                "error": "Invalid query detected",
                "use_cases": [],
                "warnings": ["Query contains suspicious content"]
            }
        
        sanitized_query = self.query_processor.sanitize_query(query)
        intent = self.query_processor.extract_intent(sanitized_query)
        logger.debug(f"Query intent: {intent}")
        
        retrieved_docs = self.retriever.retrieve(sanitized_query)
        
        filtered_docs = self.injection_filter.filter_retrieved_documents(retrieved_docs)
        
        deduplicated_docs = self.deduplicator.deduplicate_chunks(filtered_docs)
        
        is_confident, conf_score, conf_warnings = self.confidence_checker.check_retrieval_confidence(
            sanitized_query,
            deduplicated_docs
        )
        
        assumptions = self.confidence_checker.generate_assumptions_needed(
            sanitized_query,
            deduplicated_docs
        )
        
        if not is_confident:
            clarifications = self.confidence_checker.suggest_clarifications(
                sanitized_query,
                deduplicated_docs,
                conf_warnings
            )
            logger.warning(f"Low confidence, suggesting clarifications")
        
        generation_prompt = self.prompt_builder.build_generation_prompt(
            sanitized_query,
            deduplicated_docs,
            assumptions=assumptions,
            warnings=conf_warnings if not is_confident else None
        )
        
        raw_output = self.llm_client.generate_with_json_mode(
            system_prompt=self.prompt_builder.SYSTEM_PROMPT,
            user_prompt=generation_prompt,
            temperature=0.3
        )
        
        try:
            result = self._parse_json_output(raw_output)
        except Exception as e:
            logger.error(f"Failed to parse LLM output: {e}")
            result = {
                "use_cases": [],
                "error": "Failed to parse LLM response",
                "raw_output": raw_output[:500]
            }
        
        result = sanitize_output(result)
        
        if "use_cases" in result and result["use_cases"]:
            generated_text = json.dumps(result["use_cases"])
            is_grounded, grounding_score, grounding_warnings = self.hallucination_detector.check_grounding(
                generated_text,
                deduplicated_docs
            )
            
            result["grounding_score"] = grounding_score
            if grounding_warnings:
                result["warnings"].extend(grounding_warnings)
        
        result["confidence_score"] = conf_score
        result["assumptions"] = assumptions
        result["retrieved_sources"] = [
            doc.get('metadata', {}).get('source_file', 'Unknown')
            for doc in deduplicated_docs
        ]
        
        if debug_mode:
            result["debug_info"] = {
                "retrieved_chunks": len(retrieved_docs),
                "filtered_chunks": len(filtered_docs),
                "deduplicated_chunks": len(deduplicated_docs),
                "intent": intent,
                "confidence_warnings": conf_warnings
            }
        
        metric.stop().add_metadata(
            use_cases_generated=len(result.get("use_cases", [])),
            confidence_score=conf_score
        )
        
        logger.info(f"Generated {len(result.get('use_cases', []))} use cases")
        return result
    
    def _parse_json_output(self, raw_output: str) -> Dict[str, Any]:
        
        cleaned = raw_output.strip()
        
        json_match = re.search(r'```json\s*(.*?)\s*```', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(1)
        
        cleaned = re.sub(r'^```.*?\n', '', cleaned)
        cleaned = re.sub(r'\n```$', '', cleaned)
        
        return json.loads(cleaned)