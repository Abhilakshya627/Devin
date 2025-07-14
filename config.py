"""
Configuration management for the Devin AI Assistant.
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AgentConfig:
    """Configuration for the AI agent."""
    
    # Voice and model settings
    voice: str = "Charon"
    temperature: float = 0.8
    max_tokens: Optional[int] = None
    
    # Audio settings
    audio_enabled: bool = True
    video_enabled: bool = True
    noise_cancellation: bool = True
    
    # API Keys and external services
    openweather_api_key: Optional[str] = None
    google_translate_api_key: Optional[str] = None
    
    # Tool settings
    max_search_results: int = 3
    reminder_default_minutes: int = 5
    
    # Logging
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Load environment variables after initialization."""
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.google_translate_api_key = os.getenv('GOOGLE_TRANSLATE_API_KEY')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Convert string values to appropriate types
        self.temperature = float(os.getenv('AGENT_TEMPERATURE', self.temperature))
        self.max_search_results = int(os.getenv('MAX_SEARCH_RESULTS', self.max_search_results))
        self.audio_enabled = os.getenv('AUDIO_ENABLED', 'true').lower() == 'true'
        self.video_enabled = os.getenv('VIDEO_ENABLED', 'true').lower() == 'true'
        self.noise_cancellation = os.getenv('NOISE_CANCELLATION', 'true').lower() == 'true'

# Global configuration instance
config = AgentConfig()
