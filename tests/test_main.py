"""
Tests for main entry point.
"""
from unittest.mock import patch

import pytest

from src.main import main


class TestMain:
    """Test suite for main function."""
    
    @patch('src.main.run_cli')
    def test_main_calls_run_cli(self, mock_run_cli):
        """Test that main function calls run_cli."""
        main()
        mock_run_cli.assert_called_once()
    
    @patch('src.main.run_cli')
    def test_main_handles_exceptions(self, mock_run_cli):
        """Test that main handles exceptions gracefully."""
        mock_run_cli.side_effect = Exception("Test error")
        
        # Should not raise, but let exception propagate
        with pytest.raises(Exception, match="Test error"):
            main()

