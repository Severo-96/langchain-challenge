"""
Pydantic schemas for tool parameter validation.
"""

from pydantic import BaseModel, Field

class CountryInfoInput(BaseModel):
    """Schema for validation of parameters for searching country information."""
    country_name: str = Field(
        description="Country name in english (ex: 'Brazil', 'United States', 'France')"
    )

class ExchangeRateInput(BaseModel):
    """Schema for validation of parameters for searching exchange rate."""
    base_currency: str = Field(
        description="Base currency code (ex: 'USD', 'BRL', 'EUR')"
    )
    target_currency: str = Field(
        description="Target currency code (ex: 'BRL', 'USD', 'EUR')"
    )
