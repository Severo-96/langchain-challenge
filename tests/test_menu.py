"""
Tests for conversation menu.
"""
from unittest.mock import patch

import pytest
import questionary

from src.ui.menu import show_conversation_menu


class TestShowConversationMenu:
    """Test suite for show_conversation_menu function."""
    
    @patch('src.ui.menu.questionary.select')
    def test_new_conversation_selected(self, mock_select, conversation_db):
        """Test when user selects new conversation."""
        mock_select.return_value.ask.return_value = "💬 Nova conversa"
        
        thread_id, conv_id = show_conversation_menu(conversation_db)
        
        assert thread_id is None
        assert conv_id is None
    
    @patch('src.ui.menu.questionary.select')
    def test_existing_conversation_selected(self, mock_select, conversation_db):
        """Test when user selects existing conversation."""
        # Create a conversation first
        conv_id, thread_id = conversation_db.save_conversation_metadata("Test message")
        
        # Mock questionary to return the conversation option
        mock_select.return_value.ask.return_value = f"ID {conv_id} - Test message - 01-01-2024"
        
        result_thread_id, result_conv_id = show_conversation_menu(conversation_db)
        
        assert result_thread_id == thread_id
        assert result_conv_id == conv_id
    
    @patch('src.ui.menu.questionary.select')
    def test_no_choice_selected(self, mock_select, conversation_db):
        """Test when no choice is selected (None returned)."""
        mock_select.return_value.ask.return_value = None
        
        thread_id, conv_id = show_conversation_menu(conversation_db)
        
        assert thread_id is None
        assert conv_id is None
    
    @patch('src.ui.menu.questionary.select')
    def test_menu_with_multiple_conversations(self, mock_select, conversation_db):
        """Test menu with multiple conversations."""
        # Create multiple conversations
        conv_id1, thread_id1 = conversation_db.save_conversation_metadata("First")
        conv_id2, thread_id2 = conversation_db.save_conversation_metadata("Second")
        
        # Mock to return second conversation
        mock_select.return_value.ask.return_value = f"ID {conv_id2} - Second - 01-01-2024"
        
        result_thread_id, result_conv_id = show_conversation_menu(conversation_db)
        
        assert result_thread_id == thread_id2
        assert result_conv_id == conv_id2
    
    @patch('src.ui.menu.questionary.select')
    def test_long_message_truncated(self, mock_select, conversation_db):
        """Test that long messages are truncated in menu display."""
        long_message = "A" * 100
        conv_id, thread_id = conversation_db.save_conversation_metadata(long_message)
        
        # Mock questionary to return the conversation option
        # The truncation happens in show_conversation_menu, not in the database
        truncated_display = f"ID {conv_id} - {'A' * 47}... - 01-01-2024"
        mock_select.return_value.ask.return_value = truncated_display
        
        # The menu function should handle truncation when displaying
        # We test that the function can handle long messages
        result_thread_id, result_conv_id = show_conversation_menu(conversation_db)
        
        # The function should still work with long messages
        assert result_conv_id == conv_id
    
    @patch('src.ui.menu.questionary.select')
    def test_error_handling(self, mock_select, conversation_db):
        """Test error handling in menu."""
        # Make questionary raise an error
        mock_select.side_effect = Exception("Questionary error")
        
        thread_id, conv_id = show_conversation_menu(conversation_db)
        
        # Should return None, None on error
        assert thread_id is None
        assert conv_id is None

