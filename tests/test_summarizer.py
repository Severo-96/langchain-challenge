"""
Tests for conversation summarization.
"""
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from src.core.summarizer import MAX_MESSAGES_BEFORE_SUMMARIZE, summarize_conversation


class TestSummarizeConversation:
    """Test suite for summarize_conversation function."""
    
    def test_no_summarization_when_below_limit(self, checkpointer, mock_llm, sample_messages):
        """Test that summarization doesn't occur when below message limit."""
        thread_id = "test_thread"
        config = RunnableConfig(configurable={"thread_id": thread_id, "checkpoint_ns": ""})
        
        # Create checkpoint with few messages
        checkpoint = {
            "id": "test_checkpoint_id",
            "channel_values": {"messages": sample_messages},
            "channel_versions": {}
        }
        checkpointer.put(config, checkpoint, {"source": "test"}, {})
        
        # Try to summarize
        result = summarize_conversation(checkpointer, thread_id, mock_llm)
        
        assert result is False
        mock_llm.invoke.assert_not_called()
    
    def test_summarization_when_above_limit(self, checkpointer, mock_llm, many_messages):
        """Test that summarization occurs when above message limit."""
        thread_id = "test_thread"
        config = RunnableConfig(configurable={"thread_id": thread_id, "checkpoint_ns": ""})
        
        # Create checkpoint with many messages
        checkpoint = {
            "id": "test_checkpoint_id",
            "channel_values": {"messages": many_messages},
            "channel_versions": {}
        }
        checkpointer.put(config, checkpoint, {"source": "test"}, {})
        
        # Summarize
        result = summarize_conversation(checkpointer, thread_id, mock_llm)
        
        assert result is True
        mock_llm.invoke.assert_called_once()
        
        # Verify checkpoint was updated
        updated_checkpoint = checkpointer.get(config)
        messages = updated_checkpoint["channel_values"]["messages"]
        assert len(messages) == 1
        assert isinstance(messages[0], AIMessage)
        assert "Resume of previous conversation" in messages[0].content
    
    def test_summarization_at_limit(self, checkpointer, mock_llm):
        """Test that summarization doesn't occur exactly at limit (100 messages)."""
        thread_id = "test_thread"
        config = RunnableConfig(configurable={"thread_id": thread_id, "checkpoint_ns": ""})
        
        # Create exactly 100 messages
        messages = [HumanMessage(content=f"Msg {i}") for i in range(100)]
        checkpoint = {
            "id": "test_checkpoint_id",
            "channel_values": {"messages": messages},
            "channel_versions": {}
        }
        checkpointer.put(config, checkpoint, {"source": "test"}, {})
        
        result = summarize_conversation(checkpointer, thread_id, mock_llm)
        
        assert result is False
        mock_llm.invoke.assert_not_called()
    
    def test_summarization_creates_llm_if_none(self, checkpointer, many_messages, monkeypatch):
        """Test that LLM is created if not provided."""
        thread_id = "test_thread"
        config = RunnableConfig(configurable={"thread_id": thread_id, "checkpoint_ns": ""})
        
        checkpoint = {
            "id": "test_checkpoint_id",
            "channel_values": {"messages": many_messages},
            "channel_versions": {}
        }
        checkpointer.put(config, checkpoint, {"source": "test"}, {})
        
        # Mock ChatOpenAI creation
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = MagicMock(content="Test summary")
        
        with patch('src.core.summarizer.ChatOpenAI', return_value=mock_llm_instance):
            result = summarize_conversation(checkpointer, thread_id, llm=None)
        
        assert result is True
        mock_llm_instance.invoke.assert_called_once()
    
    def test_summarization_handles_missing_checkpoint(self, checkpointer, mock_llm):
        """Test that function returns False if checkpoint doesn't exist."""
        thread_id = "non_existent_thread"
        
        result = summarize_conversation(checkpointer, thread_id, mock_llm)
        
        assert result is False
        mock_llm.invoke.assert_not_called()
    
    def test_summarization_handles_errors_gracefully(self, checkpointer, mock_llm, many_messages):
        """Test that errors are handled gracefully."""
        thread_id = "test_thread"
        config = RunnableConfig(configurable={"thread_id": thread_id, "checkpoint_ns": ""})
        
        checkpoint = {
            "id": "test_checkpoint_id",
            "channel_values": {"messages": many_messages},
            "channel_versions": {}
        }
        checkpointer.put(config, checkpoint, {"source": "test"}, {})
        
        # Make LLM raise an error
        mock_llm.invoke.side_effect = Exception("API Error")
        
        # Should not raise, but return False
        result = summarize_conversation(checkpointer, thread_id, mock_llm)
        
        assert result is False

