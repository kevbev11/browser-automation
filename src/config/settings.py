from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # AgentCore Configuration
    agentcore_runtime_name: str = "browser-automation-agent"
    agentcore_browser_enabled: bool = True
    agentcore_memory_enabled: bool = True
    agentcore_observability_enabled: bool = True
    
    # Authentication
    oauth_discovery_url: Optional[str] = None
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    
    # Model Configuration - CHANGED TO OPENAI
    openai_api_key: str
    model_name: str = "gpt-4o"
    model_temperature: float = 0.1
    
    # LangSmith (Optional)
    langchain_api_key: Optional[str] = None
    langchain_tracing_v2: bool = False
    langchain_project: str = "AgentCore-Browser-Agent"
    
    # Development
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
