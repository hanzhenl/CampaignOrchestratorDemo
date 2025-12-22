"""
Configuration management for agent orchestration system
"""
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class AgentConfig:
    """Configuration for agent orchestration system"""
    
    # Deepseek API Configuration
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # Request Configuration
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    
    # Agent Temperature Settings
    agent_temperatures: Dict[str, float] = {
        "classification": 0.3,
        "planning": 0.5,
        "research": 0.7,
        "campaign": 0.7,
        "audience": 0.6,
        "journey": 0.7,
        "validation": 0.3
    }
    
    # Agent Max Tokens Settings
    agent_max_tokens: Dict[str, int] = {
        "classification": 100,
        "planning": 500,
        "research": 2000,
        "campaign": 3000,
        "audience": 1500,
        "journey": 2500,
        "validation": 1500
    }
    
    @classmethod
    def get_temperature(cls, agent_name: str) -> float:
        """Get temperature for specific agent"""
        return cls.agent_temperatures.get(agent_name, 0.7)
    
    @classmethod
    def get_max_tokens(cls, agent_name: str) -> int:
        """Get max tokens for specific agent"""
        return cls.agent_max_tokens.get(agent_name, 2000)

