"""
Tests for API clients (countries and exchange).
"""
from unittest.mock import Mock, patch

import pytest
import requests

from src.api.clients.countries import get_country_info
from src.api.clients.exchange import get_exchange_rate


class TestGetCountryInfo:
    """Test suite for get_country_info function."""
    
    @patch('src.api.clients.countries.requests.get')
    def test_successful_country_search(self, mock_get):
        """Test successful country information retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": {"common": "Brazil"},
            "capital": ["Brasília"],
            "population": 212559417,
            "region": "Americas",
            "currencies": {"BRL": {"name": "Brazilian real"}},
            "languages": {"por": "Portuguese"}
        }]
        mock_get.return_value = mock_response
        
        result = get_country_info("Brazil")
        
        assert result["success"] is True
        assert result["name"] == "Brazil"
        assert result["capital"] == "Brasília"
        assert result["population"] == 212559417
        assert result["region"] == "Americas"
        assert result["currency"] == "BRL"
        assert "Portuguese" in result["languages"]
    
    @patch('src.api.clients.countries.requests.get')
    def test_country_not_found(self, mock_get):
        """Test when country is not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = get_country_info("NonExistentCountry")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    @patch('src.api.clients.countries.requests.get')
    def test_api_error_status_code(self, mock_get):
        """Test when API returns error status code."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = get_country_info("Brazil")
        
        assert result["success"] is False
        assert "404" in result["error"]
    
    @patch('src.api.clients.countries.requests.get')
    def test_connection_error(self, mock_get):
        """Test when connection error occurs."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection timeout")
        
        result = get_country_info("Brazil")
        
        assert result["success"] is False
        assert "Connection error" in result["error"]
    
    @patch('src.api.clients.countries.requests.get')
    def test_missing_optional_fields(self, mock_get):
        """Test handling of missing optional fields."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "name": {"common": "TestCountry"},
            # Missing capital, currencies, languages
        }]
        mock_get.return_value = mock_response
        
        result = get_country_info("TestCountry")
        
        assert result["success"] is True
        assert result["capital"] == "N/A"
        assert result["currency"] == "N/A"
        assert result["languages"] == []


class TestGetExchangeRate:
    """Test suite for get_exchange_rate function."""
    
    @patch('src.api.clients.exchange.requests.get')
    def test_successful_exchange_rate(self, mock_get):
        """Test successful exchange rate retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "base": "USD",
            "date": "2024-01-01",
            "rates": {
                "BRL": 5.0,
                "EUR": 0.85
            }
        }
        mock_get.return_value = mock_response
        
        result = get_exchange_rate("USD", "BRL")
        
        assert result["success"] is True
        assert result["base_currency"] == "USD"
        assert result["target_currency"] == "BRL"
        assert result["rate"] == 5.0
        assert result["date"] == "2024-01-01"
    
    @patch('src.api.clients.exchange.requests.get')
    def test_currency_not_found(self, mock_get):
        """Test when target currency is not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": {"USD": 1.0}
        }
        mock_get.return_value = mock_response
        
        result = get_exchange_rate("USD", "INVALID")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    @patch('src.api.clients.exchange.requests.get')
    def test_api_error_status_code(self, mock_get):
        """Test when API returns error status code."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = get_exchange_rate("USD", "BRL")
        
        assert result["success"] is False
        assert "500" in result["error"]
    
    @patch('src.api.clients.exchange.requests.get')
    def test_connection_error(self, mock_get):
        """Test when connection error occurs."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection timeout")
        
        result = get_exchange_rate("USD", "BRL")
        
        assert result["success"] is False
        assert "Connection error" in result["error"]
    
    @patch('src.api.clients.exchange.requests.get')
    def test_uppercase_conversion(self, mock_get):
        """Test that currency codes are converted to uppercase."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": {"BRL": 5.0}
        }
        mock_get.return_value = mock_response
        
        result = get_exchange_rate("usd", "brl")
        
        assert result["success"] is True
        assert result["base_currency"] == "USD"
        assert result["target_currency"] == "BRL"

