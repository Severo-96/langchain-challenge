"""
Cliente para fazer chamadas a APIs externas.
Aqui ficam todas as funções que se comunicam com serviços externos.
"""

import requests
from typing import Dict, Any, Optional

def get_country_info(country_name: str) -> Dict[str, Any]:
    """
    Busca informações sobre um país usando a REST Countries API.
    Esta API é gratuita e não requer autenticação.
    
    Args:
        country_name: Nome do país (ex: "Brazil", "United States")
    
    Returns:
        Dicionário com informações do país ou erro
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
                return {"success": False, "error": "País não encontrado"}
        else:
            return {"success": False, "error": f"Erro na API: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Erro de conexão: {str(e)}"}

def get_exchange_rate(base_currency: str, target_currency: str) -> Dict[str, Any]:
    """
    Busca taxa de câmbio entre duas moedas usando uma API pública.
    Usa a API exchangerate-api.com (versão gratuita).
    
    Args:
        base_currency: Moeda base (ex: "USD", "BRL", "EUR")
        target_currency: Moeda de destino (ex: "BRL", "USD", "EUR")
    
    Returns:
        Dicionário com taxa de câmbio ou erro
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
                return {"success": False, "error": f"Moeda {target} não encontrada"}
        else:
            return {"success": False, "error": f"Erro na API: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Erro de conexão: {str(e)}"}
