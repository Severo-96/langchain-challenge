"""
Tests for agent creation and configuration.
"""
from unittest.mock import MagicMock, patch
from pathlib import Path
import sqlite3

import pytest
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver

from src.core.agent import create_agent_executor


class TestCreateAgentExecutor:
    """Test suite for create_agent_executor function."""
    
    def test_creates_agent_with_default_llm(self, temp_checkpoint_db_path, monkeypatch):
        """Test that agent is created with default LLM when none provided."""

        # Mock settings
        test_settings = MagicMock()
        test_settings.model_name = "gpt-4o-mini"
        test_settings.temperature = 0.5
        test_settings.openai_api_key = "test-key"
        test_settings.checkpoint_db_path = temp_checkpoint_db_path
        monkeypatch.setattr("src.core.agent.settings", test_settings)
        
        # Mock ChatOpenAI to avoid real API calls
        with patch('src.core.agent.ChatOpenAI') as mock_chat:
            mock_llm_instance = MagicMock()
            mock_chat.return_value = mock_llm_instance
            
            # Mock create_agent
            with patch('src.core.agent.create_agent') as mock_create:
                mock_agent = MagicMock(spec=Runnable)
                mock_create.return_value = mock_agent
                
                agent, checkpointer = create_agent_executor()
        
        assert agent is not None
        assert isinstance(checkpointer, SqliteSaver)
        mock_chat.assert_called_once()
    
    def test_creates_agent_with_provided_llm(self, temp_checkpoint_db_path, monkeypatch):
        """Test that agent uses provided LLM instead of creating new one."""

        # Mock settings
        test_settings = MagicMock()
        test_settings.checkpoint_db_path = temp_checkpoint_db_path
        monkeypatch.setattr("src.core.agent.settings", test_settings)
        
        # Create custom LLM
        custom_llm = MagicMock(spec=ChatOpenAI)
        
        # Mock create_agent
        with patch('src.core.agent.create_agent') as mock_create:
            mock_agent = MagicMock(spec=Runnable)
            mock_create.return_value = mock_agent
            
            agent, checkpointer = create_agent_executor(llm=custom_llm)
        
        assert agent is not None
        # Verify custom LLM was used
        mock_create.assert_called_once()
        # Check that custom_llm was passed to create_agent
        call_args = mock_create.call_args
        assert call_args.kwargs['model'] == custom_llm
    
    def test_creates_agent_with_provided_checkpointer(self, temp_checkpoint_db_path, monkeypatch):
        """Test that agent uses provided checkpointer instead of creating new one."""
        # Mock settings
        test_settings = MagicMock()
        test_settings.model_name = "gpt-4o-mini"
        test_settings.temperature = 0.5
        test_settings.openai_api_key = "test-key"
        test_settings.checkpoint_db_path = temp_checkpoint_db_path
        monkeypatch.setattr("src.core.agent.settings", test_settings)
        
        # Create custom checkpointer
        custom_checkpointer = MagicMock(spec=SqliteSaver)
        
        # Mock ChatOpenAI to avoid validation errors
        with patch('src.core.agent.ChatOpenAI') as mock_chat:
            mock_llm_instance = MagicMock()
            mock_chat.return_value = mock_llm_instance
            
            # Mock create_agent
            with patch('src.core.agent.create_agent') as mock_create:
                mock_agent = MagicMock(spec=Runnable)
                mock_create.return_value = mock_agent
                
                agent, checkpointer = create_agent_executor(checkpointer=custom_checkpointer)
        
        assert agent is not None
        assert checkpointer == custom_checkpointer
        # Verify custom checkpointer was used
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        assert call_args.kwargs['checkpointer'] == custom_checkpointer
    
    def test_agent_has_tools(self, temp_checkpoint_db_path, monkeypatch):
        """Test that created agent has tools configured."""

        # Mock settings
        test_settings = MagicMock()
        test_settings.model_name = "gpt-4o-mini"
        test_settings.temperature = 0.5
        test_settings.openai_api_key = "test-key"
        test_settings.checkpoint_db_path = temp_checkpoint_db_path
        monkeypatch.setattr("src.core.agent.settings", test_settings)
        
        # Mock ChatOpenAI
        with patch('src.core.agent.ChatOpenAI') as mock_chat:
            mock_llm_instance = MagicMock()
            mock_chat.return_value = mock_llm_instance
            
            # Mock create_agent
            with patch('src.core.agent.create_agent') as mock_create:
                mock_agent = MagicMock(spec=Runnable)
                mock_create.return_value = mock_agent
                
                agent, _ = create_agent_executor()
        
        # Verify create_agent was called with tools
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        assert 'tools' in call_args.kwargs
        tools = call_args.kwargs['tools']
        assert len(tools) > 0  # Should have at least country and exchange tools

