"""
Configuration file for the project.
Manages the loading of environment variables.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

@dataclass
class Settings:
    """Application settings."""
    openai_api_key: str
    db_path: Path = Path("data/conversations.db")
    model_name: str = "gpt-4o-mini" 
    temperature: float = 0.5 # Controla a criatividade (0.0 = determinístico, 1.0 = muito criativo)
    
    @classmethod
    def from_env(cls) -> "Settings":
        """
        Loads settings from environment variables.
        
        Returns:
            Configured Settings instance
            
        Raises:
            ValueError: If OPENAI_API_KEY is not found
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found.")
        
        return cls(
            openai_api_key=api_key,
            db_path=Path("data/conversations.db"),
            model_name=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            temperature=float(os.getenv("TEMPERATURE", "0.5")),
        )


# Instância global de configurações
settings = Settings.from_env()
