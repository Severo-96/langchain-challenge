"""
Configuration of LangChain with OpenAI and Function Calling.
Here we configure the AI model and the available tools (functions).
"""

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import List
from config import OPENAI_API_KEY
from api_client import get_country_info, get_exchange_rate

# Schemas Pydantic para validação dos parâmetros das ferramentas
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

def create_agent_executor():
  """
  Creates and configures the LangChain 1.0+ agent with Function Calling.
  
  Returns:
    Configured agent ready to use (new LangChain 1.0+ API)
  """
  
  # Funções wrapper que formatam a saída das APIs para o assistente
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
  
  def get_exchange_rate_wrapper(base_currency: str, target_currency: str) -> str:
    """
    Wrapper that searches for exchange rate and formats the response.
    
    Args:
      base_currency: Base currency code
      target_currency: Target currency code
    
    Returns:
      String formatted with exchange rate or error message
    """
    result = get_exchange_rate(base_currency, target_currency)
    
    if not result.get("success"):
      error_msg = result.get('error', 'Unknown error')
      return f"Erro ao buscar taxa de câmbio: {error_msg}"
    
    base = result.get('base_currency', base_currency)
    target = result.get('target_currency', target_currency)
    rate = result.get('rate', 0)
    date = result.get('date', 'N/A')
    
    return f"""Taxa de câmbio:
        - {base} → {target}
        - Taxa: 1 {base} = {rate:.4f} {target}
        - Data: {date}"""
  
  # Inicializa o modelo de linguagem (usando GPT-4o-mini por ser mais barato)
  llm = ChatOpenAI(
    model="gpt-4o-mini",    
    temperature=0.5,  # Controla a criatividade (0.0 = determinístico, 1.0 = muito criativo)
    api_key=OPENAI_API_KEY
  )
  
  # Cria as ferramentas (tools) usando StructuredTool
  # Cada ferramenta permite que o assistente chame funções externas
  tools: List[StructuredTool] = [
    StructuredTool.from_function(
      func=get_country_info_wrapper,
      name="get_country_info",
      description=(
        "Search for country information, including capital, population, region, currency and languages. "
        "The function returns an object with the country information, with the country name, capital, population, region, currency and languages. "
        "Use when the user asks about countries, capitals, population of countries, or geographic information. "
        "The country name must be searched in english."
      ),
      args_schema=CountryInfoInput
    ),
    StructuredTool.from_function(
      func=get_exchange_rate_wrapper,
      name="get_exchange_rate",
      description=(
        "Search for current exchange rate between two currencies. "
        "The function returns an object with the exchange rate, with the base currency, the target currency, "
        "the exchange rate and the date of the exchange rate. "
        "Use when the user asks about currency conversion, exchange rate, or value of a currency in relation to another."
      ),
      args_schema=ExchangeRateInput
    ),
  ]
  
  # Prompt do sistema que define o comportamento do assistente
  system_prompt = """You are a useful and friendly assistant that can search for information about:
          - Countries (capital, population, region, currency, languages)
          - Exchange rate between currencies

          Use the available tools when necessary to answer the user's questions.
          Be clear, objective and friendly in your responses, whenever possible show a summary of the information shown.
          If you are not sure about something, be honest and say you don't know.

          If the user wants to exit, say that to exit he needs to type 'sair', 'quit', 'exit' or 'q'.
          If the user wants to clear the history, say that to clear the history he needs to type 'limpar',
          'clear' or 'reset'."""
  
  # Cria o agente usando a nova API do LangChain
  agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
  )
  
  return agent
