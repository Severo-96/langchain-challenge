"""
Tests for Pydantic schemas.
"""
import pytest
from pydantic import ValidationError

from src.core.schemas import CountryInfoInput, ExchangeRateInput


class TestCountryInfoInput:
    """Test suite for CountryInfoInput schema."""
    
    def test_valid_country_name(self):
        """Test valid country name."""
        schema = CountryInfoInput(country_name="Brazil")
        assert schema.country_name == "Brazil"
    
    def test_empty_country_name(self):
        """Test that empty country name is allowed (validation happens elsewhere)."""
        schema = CountryInfoInput(country_name="")
        assert schema.country_name == ""
    
    def test_country_name_with_spaces(self):
        """Test country name with spaces."""
        schema = CountryInfoInput(country_name="United States")
        assert schema.country_name == "United States"
    
    def test_country_name_field_description(self):
        """Test that field has description."""
        field = CountryInfoInput.model_fields["country_name"]
        assert field.description is not None
        assert len(field.description) > 0


class TestExchangeRateInput:
    """Test suite for ExchangeRateInput schema."""
    
    def test_valid_currencies(self):
        """Test valid currency codes."""
        schema = ExchangeRateInput(base_currency="USD", target_currency="BRL")
        assert schema.base_currency == "USD"
        assert schema.target_currency == "BRL"
    
    def test_lowercase_currencies(self):
        """Test that lowercase currencies are accepted."""
        schema = ExchangeRateInput(base_currency="usd", target_currency="brl")
        assert schema.base_currency == "usd"
        assert schema.target_currency == "brl"
    
    def test_same_base_and_target(self):
        """Test that same currency for base and target is allowed."""
        schema = ExchangeRateInput(base_currency="USD", target_currency="USD")
        assert schema.base_currency == schema.target_currency
    
    def test_empty_currencies(self):
        """Test that empty currencies are allowed (validation happens elsewhere)."""
        schema = ExchangeRateInput(base_currency="", target_currency="")
        assert schema.base_currency == ""
        assert schema.target_currency == ""
    
    def test_currency_fields_have_descriptions(self):
        """Test that fields have descriptions."""
        base_field = ExchangeRateInput.model_fields["base_currency"]
        target_field = ExchangeRateInput.model_fields["target_currency"]
        
        assert base_field.description is not None
        assert target_field.description is not None
        assert len(base_field.description) > 0
        assert len(target_field.description) > 0
    
    def test_serialization(self):
        """Test that schema can be serialized to dict."""
        schema = ExchangeRateInput(base_currency="USD", target_currency="BRL")
        data = schema.model_dump()
        
        assert data["base_currency"] == "USD"
        assert data["target_currency"] == "BRL"

