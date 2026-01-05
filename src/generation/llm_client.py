from typing import Dict, Any, Optional
from groq import Groq
from config import settings
from utils.logger import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential

logger = get_logger(__name__)

class LLMClient:
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        
        if self.provider == "groq":
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY not set in environment")
            self.client = Groq(api_key=settings.groq_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> str:
        
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                content = response.choices[0].message.content
                logger.debug(f"Generated {len(content)} characters using {self.provider}/{self.model}")
                return content
            
        except Exception as e:
            logger.error(f"Error generating with {self.provider}: {e}")
            raise
    
    def generate_with_json_mode(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> str:
        
        enhanced_system = system_prompt + "\n\nYou MUST respond with valid JSON only. No explanations, no markdown, just JSON."
        enhanced_user = user_prompt + "\n\nRespond with valid JSON only."
        
        return self.generate(
            system_prompt=enhanced_system,
            user_prompt=enhanced_user,
            temperature=temperature,
            max_tokens=max_tokens
        )