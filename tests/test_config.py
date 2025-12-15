"""
Tests for configuration and settings.
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.config import (
    DEFAULT_CHECKPOINT_DB_PATH,
    DEFAULT_CONVERSATION_DB_PATH,
    DEFAULT_MODEL_NAME,
    DEFAULT_TEMPERATURE,
    Settings,
    _validate_api_key,
    _validate_temperature,
    create_settings_from_env,
)


class TestValidateApiKey:
    """Test suite for _validate_api_key function."""
    
    def test_validates_present_api_key(self):
        """Test that present API key is validated."""
        result = _validate_api_key("sk-test123")
        assert result == "sk-test123"
    
    def test_raises_error_on_missing_api_key(self):
        """Test that missing API key raises ValueError."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            _validate_api_key(None)
    
    def test_raises_error_on_empty_api_key(self):
        """Test that empty API key raises ValueError."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            _validate_api_key("")


class TestValidateTemperature:
    """Test suite for _validate_temperature function."""
    
    def test_validates_valid_temperature(self):
        """Test that valid temperature is accepted."""
        assert _validate_temperature("0.5") == 0.5
        assert _validate_temperature("1.0") == 1.0
        assert _validate_temperature("0.0") == 0.0
        assert _validate_temperature("2.0") == 2.0
    
    def test_raises_error_on_invalid_format(self):
        """Test that invalid temperature format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid TEMPERATURE value"):
            _validate_temperature("not-a-number")
    
    def test_raises_error_on_out_of_range_low(self):
        """Test that temperature below 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="Temperature must be between"):
            _validate_temperature("-0.1")
    
    def test_raises_error_on_out_of_range_high(self):
        """Test that temperature above 2.0 raises ValueError."""
        with pytest.raises(ValueError, match="Temperature must be between"):
            _validate_temperature("2.1")


class TestSettings:
    """Test suite for Settings class."""
    
    def test_initializes_with_all_parameters(self):
        """Test that Settings initializes with all parameters."""
        settings = Settings(
            openai_api_key="test-key",
            conversation_db_path=Path("test.db"),
            checkpoint_db_path=Path("checkpoint.db"),
            model_name="gpt-4",
            temperature=0.7
        )
        
        assert settings.openai_api_key == "test-key"
        assert settings.conversation_db_path == Path("test.db")
        assert settings.checkpoint_db_path == Path("checkpoint.db")
        assert settings.model_name == "gpt-4"
        assert settings.temperature == 0.7
    
    def test_uses_default_values(self):
        """Test that Settings uses default values when not provided."""
        settings = Settings(openai_api_key="test-key")
        
        assert settings.conversation_db_path == DEFAULT_CONVERSATION_DB_PATH
        assert settings.checkpoint_db_path == DEFAULT_CHECKPOINT_DB_PATH
        assert settings.model_name == DEFAULT_MODEL_NAME
        assert settings.temperature == DEFAULT_TEMPERATURE


class TestCreateSettingsFromEnv:
    """Test suite for create_settings_from_env function."""
    
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-env-key",
        "TEMPERATURE": "0.8",
        "MODEL_NAME": "gpt-4",
        "CONVERSATION_DB_PATH": "custom/conversations.db",
        "CHECKPOINT_DB_PATH": "custom/checkpoints.db"
    })
    @patch('src.core.config.load_dotenv')
    def test_loads_from_environment(self, mock_load_dotenv):
        """Test that settings are loaded from environment variables."""
        settings = create_settings_from_env()
        
        assert settings.openai_api_key == "test-env-key"
        assert settings.temperature == 0.8
        assert settings.model_name == "gpt-4"
        assert settings.conversation_db_path == Path("custom/conversations.db")
        assert settings.checkpoint_db_path == Path("custom/checkpoints.db")
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    @patch('src.core.config.load_dotenv')
    def test_uses_defaults_when_env_not_set(self, mock_load_dotenv):
        """Test that default values are used when env vars not set."""
        settings = create_settings_from_env()
        
        assert settings.openai_api_key == "test-key"
        assert settings.temperature == DEFAULT_TEMPERATURE
        assert settings.model_name == DEFAULT_MODEL_NAME
        assert settings.conversation_db_path == DEFAULT_CONVERSATION_DB_PATH
        assert settings.checkpoint_db_path == DEFAULT_CHECKPOINT_DB_PATH
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('src.core.config.load_dotenv')
    def test_raises_error_on_missing_api_key(self, mock_load_dotenv):
        """Test that missing API key raises ValueError."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            create_settings_from_env()

