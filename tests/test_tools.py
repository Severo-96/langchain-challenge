"""
Tests for LangChain tools (country and exchange).
"""
from unittest.mock import Mock, patch

import pytest
from langchain_core.tools import StructuredTool

from src.tools.country_tool import create_country_tool, get_country_info_wrapper
from src.tools.exchange_tool import create_exchange_tool, get_exchange_rate_wrapper


class TestCountryTool:
    """Test suite for country tool."""
    
    @patch('src.tools.country_tool.get_country_info')
    def test_get_country_info_wrapper_success(self, mock_get_country_info):
        """Test successful country info wrapper."""
        mock_get_country_info.return_value = {
            "success": True,
            "name": "Brazil",
            "capital": "Brasília",
            "population": 212559417,
            "region": "Americas",
            "currency": "BRL",
            "languages": ["Portuguese"]
        }
        
        result = get_country_info_wrapper("Brazil")
        
        assert "Brazil" in result
        assert "Brasília" in result
        assert "212,559,417" in result
        assert "Americas" in result
        assert "BRL" in result
        assert "Portuguese" in result
    
    @patch('src.tools.country_tool.get_country_info')
    def test_get_country_info_wrapper_error(self, mock_get_country_info):
        """Test country info wrapper with error."""
        mock_get_country_info.return_value = {
            "success": False,
            "error": "Country not found"
        }
        
        result = get_country_info_wrapper("InvalidCountry")
        
        assert "Erro" in result
        assert "InvalidCountry" in result
        assert "not found" in result
    
    def test_create_country_tool(self):
        """Test creation of country tool."""
        tool = create_country_tool()
        
        assert isinstance(tool, StructuredTool)
        assert tool.name == "get_country_info"
        assert "country" in tool.description.lower()
        assert "capital" in tool.description.lower()
    
    def test_country_tool_invocation(self):
        """Test that country tool can be invoked."""
        tool = create_country_tool()
        
        # Tool should have invoke method
        assert hasattr(tool, 'invoke')
        assert callable(tool.invoke)


class TestExchangeTool:
    """Test suite for exchange tool."""
    
    @patch('src.tools.exchange_tool.get_exchange_rate')
    def test_get_exchange_rate_wrapper_success(self, mock_get_exchange_rate):
        """Test successful exchange rate wrapper."""
        mock_get_exchange_rate.return_value = {
            "success": True,
            "base_currency": "USD",
            "target_currency": "BRL",
            "rate": 5.0,
            "date": "2024-01-01"
        }
        
        result = get_exchange_rate_wrapper("USD", "BRL")
        
        assert "USD" in result
        assert "BRL" in result
        assert "5.0000" in result
        assert "2024-01-01" in result
    
    @patch('src.tools.exchange_tool.get_exchange_rate')
    def test_get_exchange_rate_wrapper_error(self, mock_get_exchange_rate):
        """Test exchange rate wrapper with error."""
        mock_get_exchange_rate.return_value = {
            "success": False,
            "error": "Currency not found"
        }
        
        result = get_exchange_rate_wrapper("USD", "INVALID")
        
        assert "Erro" in result
        assert "not found" in result
    
    def test_create_exchange_tool(self):
        """Test creation of exchange tool."""
        tool = create_exchange_tool()
        
        assert isinstance(tool, StructuredTool)
        assert tool.name == "get_exchange_rate"
        assert "exchange" in tool.description.lower() or "câmbio" in tool.description.lower()
        assert "currency" in tool.description.lower()
    
    def test_exchange_tool_invocation(self):
        """Test that exchange tool can be invoked."""
        tool = create_exchange_tool()
        
        # Tool should have invoke method
        assert hasattr(tool, 'invoke')
        assert callable(tool.invoke)

