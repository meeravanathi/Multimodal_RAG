from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class PromptBuilder:
    
    SYSTEM_PROMPT = """You are an expert QA engineer and test case designer. Your task is to generate comprehensive, well-structured test cases and use cases based ONLY on the provided context from documentation.

CRITICAL RULES:
1. ONLY use information explicitly stated in the provided context
2. If information is missing, state assumptions clearly
3. Do NOT invent features, APIs, or behaviors not mentioned in the context
4. Generate realistic test data that aligns with context requirements
5. Always structure output as valid JSON

OUTPUT FORMAT:
{
  "use_cases": [
    {
      "title": "Clear, descriptive title",
      "goal": "What this test validates",
      "preconditions": ["List of prerequisites"],
      "test_data": {"key": "value"},
      "steps": [
        {
          "step_number": 1,
          "action": "What to do",
          "expected_result": "What should happen"
        }
      ],
      "expected_results": ["Overall expected outcomes"],
      "negative_cases": ["Error scenarios to test"],
      "boundary_cases": ["Edge cases to test"]
    }
  ],
  "metadata": {
    "total_use_cases": 0,
    "coverage_areas": []
  },
  "confidence_score": 0.0,
  "retrieved_sources": [],
  "warnings": [],
  "assumptions": []
}"""
    
    @staticmethod
    def build_generation_prompt(
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        assumptions: List[str] = None,
        warnings: List[str] = None
    ) -> str:
        
        context_parts = []
        sources = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            content = doc.get('content', '')
            source = doc.get('metadata', {}).get('source_file', f'Document {i}')
            sources.append(source)
            
            context_parts.append(f"--- Source {i}: {source} ---")
            context_parts.append(content)
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        prompt = f"""USER QUERY: {query}

RETRIEVED CONTEXT:
{context}

SOURCES USED: {', '.join(set(sources))}"""
        
        if assumptions:
            prompt += f"\n\nASSUMPTIONS (due to limited info):\n" + "\n".join(f"- {a}" for a in assumptions)
        
        if warnings:
            prompt += f"\n\nWARNINGS:\n" + "\n".join(f"- {w}" for w in warnings)
        
        prompt += """

TASK:
Generate comprehensive test cases/use cases based ONLY on the above context. Follow these guidelines:

1. POSITIVE CASES: Cover main success scenarios
2. NEGATIVE CASES: Invalid inputs, error conditions, authentication failures
3. BOUNDARY CASES: Edge values, limits, constraints
4. Include realistic test data based on context requirements
5. Be specific with expected results
6. If critical information is missing, note it in assumptions

Output valid JSON matching the required schema."""
        
        return prompt
    
    @staticmethod
    def build_retrieval_prompt(query: str) -> str:
        return f"Find relevant information to answer: {query}"