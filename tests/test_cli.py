"""
Tests for CLI interface.
"""
from unittest.mock import MagicMock, Mock, patch

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from src.ui.cli import EXIT_COMMANDS, CLEAR_COMMANDS, run_cli
from src.database.repository import ConversationDB


class TestRunCli:
    """Test suite for run_cli function."""
    
    @patch('src.ui.cli.show_conversation_menu')
    @patch('src.ui.cli.create_agent_executor')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_cli_exits_on_exit_command(self, mock_print, mock_input, mock_create_agent, mock_menu):
        """Test that run_cli exits when user types exit command."""
        # Setup mocks
        mock_menu.return_value = (None, None)
        mock_agent = MagicMock(spec=Runnable)
        mock_checkpointer = MagicMock()
        mock_create_agent.return_value = (mock_agent, mock_checkpointer)
        
        # Simulate user typing exit command
        mock_input.return_value = "sair"
        
        # Should not raise and should exit
        try:
            run_cli()
        except SystemExit:
            pass  # Expected if sys.exit is called
        
        # Verify that exit message was printed
        mock_print.assert_any_call("\n👋 Até logo!")
    
    @patch('src.ui.cli.show_conversation_menu')
    @patch('src.ui.cli.create_agent_executor')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_cli_handles_keyboard_interrupt(self, mock_print, mock_input, mock_create_agent, mock_menu):
        """Test that run_cli handles KeyboardInterrupt gracefully."""
        mock_menu.return_value = (None, None)
        mock_agent = MagicMock(spec=Runnable)
        mock_checkpointer = MagicMock()
        mock_create_agent.return_value = (mock_agent, mock_checkpointer)
        
        # Simulate Ctrl+C
        mock_input.side_effect = KeyboardInterrupt()
        
        # Should handle gracefully
        run_cli()
        
        # Verify that interrupt message was printed
        mock_print.assert_any_call("\n\n👋 Interrompido pelo usuário. Até logo!")
    
    @patch('src.ui.cli.show_conversation_menu')
    @patch('src.ui.cli.create_agent_executor')
    def test_run_cli_initializes_with_provided_db(self, mock_create_agent, mock_menu):
        """Test that run_cli uses provided database."""
        
        mock_menu.return_value = (None, None)
        mock_agent = MagicMock(spec=Runnable)
        mock_checkpointer = MagicMock()
        mock_create_agent.return_value = (mock_agent, mock_checkpointer)
        
        db = ConversationDB()
        
        # Should not create new db if provided
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            run_cli(db=db)
    
    @patch('src.ui.cli.show_conversation_menu')
    @patch('src.ui.cli.create_agent_executor')
    def test_run_cli_initializes_with_provided_agent(self, mock_create_agent, mock_menu):
        """Test that run_cli uses provided agent."""
        mock_menu.return_value = (None, None)
        mock_agent = MagicMock(spec=Runnable)
        mock_checkpointer = MagicMock()
        # Mock create_agent_executor to return checkpointer when called for summarization
        mock_create_agent.return_value = (mock_agent, mock_checkpointer)
        
        # Should not create new agent if provided, but may need checkpointer
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            run_cli(agent=mock_agent)
    
    @patch('src.ui.cli.show_conversation_menu')
    @patch('src.ui.cli.create_agent_executor')
    @patch('builtins.input')
    def test_run_cli_handles_agent_initialization_error(self, mock_input, mock_create_agent, mock_menu):
        """Test that run_cli handles agent initialization errors."""
        mock_menu.return_value = (None, None)
        mock_create_agent.side_effect = Exception("API key error")
        
        # Should exit on error
        with pytest.raises(SystemExit):
            run_cli()
    
    def test_exit_commands_constant(self):
        """Test that EXIT_COMMANDS constant is defined correctly."""
        assert isinstance(EXIT_COMMANDS, list)
        assert len(EXIT_COMMANDS) > 0
        assert "sair" in EXIT_COMMANDS
        assert "quit" in EXIT_COMMANDS
        assert "exit" in EXIT_COMMANDS
    
    def test_clear_commands_constant(self):
        """Test that CLEAR_COMMANDS constant is defined correctly."""
        assert isinstance(CLEAR_COMMANDS, list)
        assert len(CLEAR_COMMANDS) > 0
        assert "limpar" in CLEAR_COMMANDS
        assert "clear" in CLEAR_COMMANDS
        assert "reset" in CLEAR_COMMANDS
    
    @patch('src.ui.cli.show_conversation_menu')
    @patch('src.ui.cli.create_agent_executor')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_exit_command_calls_break(self, mock_print, mock_input, mock_create_agent, mock_menu):
        """Test that exit command (sair) breaks the loop."""
        # Setup mocks
        mock_menu.return_value = (None, None)
        mock_agent = MagicMock(spec=Runnable)
        mock_checkpointer = MagicMock()
        mock_create_agent.return_value = (mock_agent, mock_checkpointer)
        
        # Simulate user typing exit command - should only be called once
        mock_input.return_value = "sair"
        
        # Run CLI - should exit after first input
        try:
            run_cli()
        except SystemExit:
            pass
        
        # Verify that input was called only once (loop broke after exit command)
        assert mock_input.call_count == 1
        
        # Verify exit message was printed
        mock_print.assert_any_call("\n👋 Até logo!")
    
    @patch('src.ui.cli.show_conversation_menu')
    @patch('src.ui.cli.create_agent_executor')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_clear_command_calls_delete_conversation(self, mock_print, mock_input, mock_create_agent, mock_menu):
        """Test that clear command (limpar) calls delete_conversation when conversation exists."""
        # Setup mocks
        mock_db = MagicMock(spec=ConversationDB)
        mock_db.get_conversation.return_value = {'id': 1, 'thread_id': 't1'}
        mock_menu.return_value = ('t1', 1)  # Existing conversation
        
        mock_agent = MagicMock(spec=Runnable)
        mock_checkpointer = MagicMock()
        mock_create_agent.return_value = (mock_agent, mock_checkpointer)
        
        # Simulate user typing clear command, then exit
        mock_input.side_effect = ["limpar", "sair"]
        
        # Run CLI
        try:
            run_cli(db=mock_db)
        except SystemExit:
            pass
        
        # Verify that delete_conversation was called with conversation ID
        mock_db.delete_conversation.assert_called_once_with(1)
        
        # Verify clear message was printed
        mock_print.assert_any_call("\n🧹 Histórico da conversa limpo!")

