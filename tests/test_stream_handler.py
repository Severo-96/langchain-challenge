"""
Tests for stream handler.
"""
from unittest.mock import MagicMock, Mock

import pytest
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from src.ui.stream_handler import (
    _handle_tool_message,
    _process_messages_chunk,
    _process_updates_chunk,
    process_agent_stream,
)


class TestProcessAgentStream:
    """Test suite for process_agent_stream function."""
    
    def test_process_agent_stream_calls_agent(self):
        """Test that process_agent_stream calls agent.stream correctly."""
        # Mock agent
        mock_agent = MagicMock()
        mock_agent.stream.return_value = [
            ("messages", [AIMessageChunk(content="Hello")]),
            ("updates", {"tools": {"messages": []}}),
        ]
        
        user_message = HumanMessage(content="Test")
        thread_id = "test_thread"
        
        process_agent_stream(mock_agent, user_message, thread_id)
        
        # Verify agent.stream was called with correct parameters
        mock_agent.stream.assert_called_once()
        call_args = mock_agent.stream.call_args
        assert "messages" in call_args[0][0]
        assert call_args[1]["stream_mode"] == ["updates", "messages"]
        # Check config is present
        assert "config" in call_args[1]
    
    def test_process_agent_stream_handles_updates(self):
        """Test that process_agent_stream handles updates stream mode."""
        mock_agent = MagicMock()
        # ToolMessage requires tool_call_id
        mock_tool_message = ToolMessage(content="get_country_info: result", tool_call_id="test_id")
        mock_agent.stream.return_value = [
            ("updates", {"tools": {"messages": [mock_tool_message]}}),
        ]
        
        user_message = HumanMessage(content="Test")
        thread_id = "test_thread"
        
        # Should not raise
        process_agent_stream(mock_agent, user_message, thread_id)
    
    def test_process_agent_stream_handles_messages(self):
        """Test that process_agent_stream handles messages stream mode."""
        mock_agent = MagicMock()
        mock_agent.stream.return_value = [
            ("messages", [AIMessageChunk(content="Response")]),
        ]
        
        user_message = HumanMessage(content="Test")
        thread_id = "test_thread"
        
        # Should not raise
        process_agent_stream(mock_agent, user_message, thread_id)


class TestProcessUpdatesChunk:
    """Test suite for _process_updates_chunk function."""
    
    def test_process_updates_chunk_with_tools(self):
        """Test processing updates chunk with tools."""
        chunk = {
            "tools": {
                "messages": [ToolMessage(content="test", tool_call_id="test_id")]
            }
        }
        tool_content_list = set()
        
        # Should not raise
        _process_updates_chunk(chunk, tool_content_list)
    
    def test_process_updates_chunk_without_tools(self):
        """Test processing updates chunk without tools."""
        chunk = {}
        tool_content_list = set()
        
        # Should not raise
        _process_updates_chunk(chunk, tool_content_list)


class TestProcessMessagesChunk:
    """Test suite for _process_messages_chunk function."""
    
    def test_process_messages_chunk_with_content(self):
        """Test processing messages chunk with content."""
        chunk = [AIMessageChunk(content="Hello world")]
        first_message_chunk = True
        
        result = _process_messages_chunk(chunk, first_message_chunk)
        
        assert result is False  # Should be False after first chunk
    
    def test_process_messages_chunk_empty_content(self):
        """Test processing messages chunk with empty content."""
        chunk = [AIMessageChunk(content="")]
        first_message_chunk = True
        
        result = _process_messages_chunk(chunk, first_message_chunk)
        
        assert result is True  # Should remain True if no content
    
    def test_process_messages_chunk_multiple_chunks(self):
        """Test processing multiple message chunks."""
        chunk1 = [AIMessageChunk(content="Hello")]
        chunk2 = [AIMessageChunk(content=" world")]
        
        first = _process_messages_chunk(chunk1, True)
        assert first is False
        
        second = _process_messages_chunk(chunk2, False)
        assert second is False


class TestHandleToolMessage:
    """Test suite for _handle_tool_message function."""
    
    def test_handle_tool_message_valid(self):
        """Test handling valid tool message."""
        tool_message = ToolMessage(content="get_country_info: result", tool_call_id="test_id")
        tools_chunk = {"messages": [tool_message]}
        tool_content_list = set()
        
        _handle_tool_message(tools_chunk, tool_content_list)
        
        assert "get_country_info" in tool_content_list
    
    def test_handle_tool_message_no_messages(self):
        """Test handling tool message with no messages."""
        tools_chunk = {"messages": []}
        tool_content_list = set()
        
        _handle_tool_message(tools_chunk, tool_content_list)
        
        assert len(tool_content_list) == 0
    
    def test_handle_tool_message_prevents_duplicates(self):
        """Test that tool messages don't print duplicates."""
        tool_message = ToolMessage(content="get_country_info: result", tool_call_id="test_id")
        tools_chunk = {"messages": [tool_message]}
        tool_content_list = set()
        
        # First call
        _handle_tool_message(tools_chunk, tool_content_list)
        assert "get_country_info" in tool_content_list
        
        # Second call with same tool
        _handle_tool_message(tools_chunk, tool_content_list)
        # Should still only have one entry
        assert len(tool_content_list) == 1
    
    def test_handle_tool_message_invalid_type(self):
        """Test handling non-ToolMessage in messages."""
        invalid_message = HumanMessage(content="Not a tool message")
        tools_chunk = {"messages": [invalid_message]}
        tool_content_list = set()
        
        _handle_tool_message(tools_chunk, tool_content_list)
        
        # Should not add to list
        assert len(tool_content_list) == 0

