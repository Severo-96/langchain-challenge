"""
Client for making calls to the exchange rate API.
Searches for exchange rates between currencies.
"""

from typing import Any, Dict

import requests

def get_exchange_rate(base_currency: str, target_currency: str) -> Dict[str, Any]:
    """
    Search for exchange rate between two currencies using a public API.
    Uses the exchangerate-api.com API (free version).
    
    Args:
        base_currency: Base currency (ex: "USD", "BRL", "EUR")
        target_currency: Target currency (ex: "BRL", "USD", "EUR")
    
    Returns:
        Dictionary with exchange rate or error
    """
    try:
        # Free exchange rate API (no key required for basic use)
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency.upper()}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", {})
            target = target_currency.upper()
            
            if target in rates:
                rate = rates[target]
                return {
                    "success": True,
                    "base_currency": base_currency.upper(),
                    "target_currency": target,
                    "rate": rate,
                    "date": data.get("date", "")
                }
            else:
                return {"success": False, "error": f"Currency {target} not found"}
        else:
            return {"success": False, "error": f"Error in API: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}
