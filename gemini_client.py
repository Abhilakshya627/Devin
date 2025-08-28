"""
Enhanced Gemini API client with connection pooling and error handling.
"""
import os
import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from functools import wraps
import time

# Optional offline fallback
OFFLINE = os.getenv("OFFLINE_LLM", "0").lower() in {"1", "true", "yes"}
if OFFLINE:
    try:
        from dev.local_llm import LocalLLM, load_config
    except Exception:
        LocalLLM = None
        load_config = None

logger = logging.getLogger(__name__)

@dataclass
class GeminiConfig:
    """Configuration for Gemini API client."""
    api_key: str
    model: str = "gemini-1.5-flash"
    max_retries: int = 3
    timeout: int = 30
    rate_limit_requests_per_minute: int = 60

class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors."""
    pass

class GeminiClient:
    """Enhanced Gemini API client with pooling and error handling."""
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        self._model = None
        self._last_request_time = 0
        self._request_count = 0
        self._request_times = []
        self._offline = OFFLINE
        self._local_llm = None
        
    async def _ensure_model(self):
        """Lazy initialization of Gemini model."""
        if self._offline:
            if self._local_llm is None:
                if load_config is None:
                    raise GeminiAPIError("Offline LLM requested but dev.local_llm not available")
                try:
                    cfg = load_config("dev/local_config.json")
                    self._local_llm = LocalLLM(cfg)
                except Exception as e:
                    raise GeminiAPIError(f"Failed to initialize offline LLM: {e}")
        else:
            if self._model is None:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.config.api_key)
                    self._model = genai.GenerativeModel(self.config.model)
                except Exception as e:
                    raise GeminiAPIError(f"Failed to initialize Gemini model: {e}")
    
    async def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        
        # Clean old request times (older than 1 minute)
        self._request_times = [t for t in self._request_times if current_time - t < 60]
        
        # Check if we're within rate limits
        if len(self._request_times) >= self.config.rate_limit_requests_per_minute:
            sleep_time = 60 - (current_time - self._request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
        
        self._request_times.append(current_time)
    
    async def _retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff."""
        for attempt in range(self.config.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise GeminiAPIError(f"Failed after {self.config.max_retries} attempts: {e}")
                
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
    
    async def generate_content(self, prompt: str, **kwargs) -> str:  
        """Generate content with error handling and retries."""
        await self._ensure_model()
        await self._rate_limit()
        
        async def _generate():
            try:
                if self._offline:
                    messages = [
                        {"role": "system", "content": "You are Devin, a capable local assistant. Be concise."},
                        {"role": "user", "content": prompt},
                    ]
                    text = self._local_llm.chat(messages, max_tokens=kwargs.get("max_output_tokens", 512))
                    return text
                else:
                    response = self._model.generate_content(prompt, **kwargs)
                    return response.text
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                raise
        
        return await self._retry_with_backoff(_generate)

# Global Gemini client instance
_gemini_client: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    """Get or create the global Gemini client."""
    global _gemini_client
    
    if _gemini_client is None:
        if OFFLINE:
            # No API key required
            config = GeminiConfig(api_key="offline", model="local")
        else:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise GeminiAPIError("GOOGLE_API_KEY not found in environment variables")
            config = GeminiConfig(api_key=api_key)
        _gemini_client = GeminiClient(config)
    
    return _gemini_client

def gemini_tool(func):
    """Decorator for tools that use Gemini API."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except GeminiAPIError as e:
            logger.error(f"Gemini API error in {func.__name__}: {e}")
            return f"AI service temporarily unavailable: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return f"An unexpected error occurred: {str(e)}"
    
    return wrapper
