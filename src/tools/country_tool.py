"""
LangChain tool for searching country information.
"""

from langchain_core.tools import StructuredTool
from src.core.schemas import CountryInfoInput
from src.api.clients.countries import get_country_info


def get_country_info_wrapper(country_name: str) -> str:
    """
    Wrapper that searches for country information and formats the response.

    Args:
        country_name: Country name in english
    
    Returns:
        String formatted with country information or error message
    """
    result = get_country_info(country_name)

    if not result.get("success"):
        error_msg = result.get('error', 'Unknown error')
        return f"Erro ao buscar informações sobre {country_name}: {error_msg}"

    name = result.get('name', country_name)
    capital = result.get('capital', 'N/A')
    population = result.get('population', 0)
    region = result.get('region', 'N/A')
    currency = result.get('currency', 'N/A')
    languages = ', '.join(result.get('languages', [])) or 'N/A'
    
    return f"""Informações sobre {name}:
        - Capital: {capital}
        - População: {population:,}
        - Região: {region}
        - Moeda: {currency}
        - Idiomas: {languages}"""


def create_country_tool() -> StructuredTool:
    """
    Creates the country information tool for LangChain.
    
    Returns:
        StructuredTool configured for country information
    """
    return StructuredTool.from_function(
        func=get_country_info_wrapper,
        name="get_country_info",
        description=(
            "Search for country information, including capital, population, region, currency and languages. "
            "The function returns an object with the country information, with the country name, capital, population, region, currency and languages. "
            "Use when the user asks about countries, capitals, population of countries, or geographic information. "
            "The country name must be searched in english."
        ),
        args_schema=CountryInfoInput
    )

