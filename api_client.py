"""
Cliente para fazer chamadas a APIs externas.
Aqui ficam todas as funções que se comunicam com serviços externos.
"""

import requests
from typing import Dict, Any

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
    # API REST Countries - gratuita, sem necessidade de chave
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
      data = response.json()
      # A API retorna uma lista, pegamos o primeiro resultado
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
    # API gratuita de câmbio (sem necessidade de chave para uso básico)
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
