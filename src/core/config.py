"""
Configuration file for the project.
Manages the loading of environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

DEFAULT_CONVERSATION_DB_PATH = Path("data/conversations.db")
DEFAULT_CHECKPOINT_DB_PATH = Path("data/checkpoints.db")
DEFAULT_MODEL_NAME = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.5


def _validate_api_key(api_key: str | None) -> str:
    """
    Validates OpenAI API key from environment.
    
    Args:
        api_key: API key value from environment (may be None)
        
    Returns:
        Validated API key string
        
    Raises:
        ValueError: If API key is missing or invalid
    """
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found.")
    
    return api_key


def _validate_temperature(temperature_raw: str) -> float:
    """
    Validates and converts a temperature value.

    Args:
        temperature_raw: Temperature value from environment.

    Returns:
        Validated temperature as float.

    Raises:
        ValueError: If temperature cannot be parsed as float
                or if it is out of the allowed range [0.0, 2.0].
    """
    try:
        temperature = float(temperature_raw)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid TEMPERATURE value: {temperature_raw!r}")

    if not 0.0 <= temperature <= 2.0:
        raise ValueError(
            f"Temperature must be between 0.0 and 2.0, got {temperature}"
        )

    return temperature


class Settings:
    """Application settings."""
    
    def __init__(
        self,
        openai_api_key: str,
        conversation_db_path: Path = DEFAULT_CONVERSATION_DB_PATH,
        checkpoint_db_path: Path = DEFAULT_CHECKPOINT_DB_PATH,
        model_name: str = DEFAULT_MODEL_NAME,
        temperature: float = DEFAULT_TEMPERATURE
    ):
        """
        Initialize Settings instance.
        
        Args:
            openai_api_key: OpenAI API key
            conversation_db_path: Path to the conversation database file
            checkpoint_db_path: Path to the checkpoint database file
            model_name: Name of the AI model to use
            temperature: Controls creativity (0.0 = deterministic, 2.0 = very creative)
        """
        self.openai_api_key = openai_api_key
        self.conversation_db_path = conversation_db_path
        self.checkpoint_db_path = checkpoint_db_path
        self.model_name = model_name
        self.temperature = temperature


def create_settings_from_env() -> Settings:
    """
    Loads settings from environment variables.
    
    Returns:
        Configured Settings instance
        
    Raises:
        ValueError: If OPENAI_API_KEY is not found or invalid,
                   or if TEMPERATURE is invalid
    """
    # Load environment variables from .env file
    load_dotenv()

    # Validate and get API key
    api_key = _validate_api_key(os.getenv("OPENAI_API_KEY"))
    
    # Validate and get temperature
    temp_raw = os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE))
    temperature = _validate_temperature(temp_raw)
    
    return Settings(
        openai_api_key=api_key,
        conversation_db_path=Path(os.getenv("CONVERSATION_DB_PATH", str(DEFAULT_CONVERSATION_DB_PATH))),
        checkpoint_db_path=Path(os.getenv("CHECKPOINT_DB_PATH", str(DEFAULT_CHECKPOINT_DB_PATH))),
        model_name=os.getenv("MODEL_NAME", DEFAULT_MODEL_NAME),
        temperature=temperature,
    )


# Global settings instance
settings = create_settings_from_env()

