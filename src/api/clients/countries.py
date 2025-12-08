"""
Client for making calls to the REST Countries API.
Searches for country information.
"""

from typing import Any, Dict

import requests

def get_country_info(country_name: str) -> Dict[str, Any]:
    """
    Search for country information using the REST Countries API.
    This API is free and does not require authentication.
    
    Args:
        country_name: Country name in english (ex: "Brazil", "United States")
    
    Returns:
        Dictionary with country information or error
    """

    try:
        # REST Countries API - free, no key required
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # API returns a list, we take the first result
            if data and len(data) > 0:
                country = data[0]
                return {
                    "success": True,
                    "name": country.get("name", {}).get("common", ""),
                    "capital": country.get("capital", ["N/A"])[0] if country.get("capital") else "N/A",
                    "population": country.get("population", 0),
                    "region": country.get("region", "N/A"),
                    "currency": list(country.get("currencies", {}).keys())[0] if country.get("currencies") else "N/A",
                    "languages": list(country.get("languages", {}).values()) if country.get("languages") else [],
                }
            else:
                return {"success": False, "error": "Country not found"}
        else:
            return {"success": False, "error": f"Error in API: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}
