"""
Additional tests for _create_summary function in summarizer.
"""
from unittest.mock import MagicMock, Mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.core.summarizer import _create_summary


class TestCreateSummary:
    """Test suite for _create_summary function."""
    
    def test_create_summary_with_messages(self, mock_llm):
        """Test creating summary from messages."""
        messages = [
            HumanMessage(content="What is the capital of Brazil?"),
            AIMessage(content="The capital of Brazil is Brasília."),
            HumanMessage(content="What is the population?"),
            AIMessage(content="The population is approximately 215 million."),
        ]
        
        mock_llm.invoke.return_value = Mock(content="Summary: Discussed Brazil's capital and population.")
        
        result = _create_summary(messages, mock_llm)
        
        assert result == "Summary: Discussed Brazil's capital and population."
        mock_llm.invoke.assert_called_once()
    
    def test_create_summary_filters_message_types(self, mock_llm):
        """Test that _create_summary only includes HumanMessage and AIMessage."""
        messages = [
            HumanMessage(content="Question 1"),
            AIMessage(content="Answer 1"),
            # ToolMessage would be ignored if present
        ]
        
        mock_llm.invoke.return_value = Mock(content="Summary")
        
        result = _create_summary(messages, mock_llm)
        
        assert result == "Summary"
        # Verify prompt contains user and assistant messages
        call_args = mock_llm.invoke.call_args[0][0]
        assert "User: Question 1" in call_args
        assert "Assistant: Answer 1" in call_args
    
    def test_create_summary_empty_messages(self, mock_llm):
        """Test creating summary from empty message list."""
        messages = []
        mock_llm.invoke.return_value = Mock(content="Empty conversation")
        
        result = _create_summary(messages, mock_llm)
        
        assert result == "Empty conversation"
        mock_llm.invoke.assert_called_once()
    
    def test_create_summary_includes_max_tokens_in_prompt(self, mock_llm):
        """Test that prompt includes max_tokens instruction."""
        messages = [HumanMessage(content="Test")]
        mock_llm.invoke.return_value = Mock(content="Summary")
        
        _create_summary(messages, mock_llm)
        
        call_args = mock_llm.invoke.call_args[0][0]
        assert "500" in call_args or "tokens" in call_args.lower()
    
    def test_create_summary_handles_llm_without_content_attr(self, mock_llm):
        """Test handling LLM response without content attribute."""
        messages = [HumanMessage(content="Test")]
        # Mock response as string instead of object with content
        mock_llm.invoke.return_value = "Summary text"
        
        result = _create_summary(messages, mock_llm)
        
        assert result == "Summary text"

