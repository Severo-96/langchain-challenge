"""
Configuração do LangChain com OpenAI e Function Calling.
Aqui configuramos o modelo de IA e as ferramentas (funções) disponíveis.
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
    """Schema para validação dos parâmetros de busca de informações de país."""
    country_name: str = Field(
        description="Nome do país em inglês (ex: 'Brazil', 'United States', 'France')"
    )


class ExchangeRateInput(BaseModel):
    """Schema para validação dos parâmetros de busca de taxa de câmbio."""
    base_currency: str = Field(
        description="Código da moeda base (ex: 'USD', 'BRL', 'EUR')"
    )
    target_currency: str = Field(
        description="Código da moeda de destino (ex: 'BRL', 'USD', 'EUR')"
    )


def create_agent_executor():
    """
    Cria e configura o agente LangChain 1.0+ com Function Calling.
    
    Returns:
        Agente configurado e pronto para uso (nova API do LangChain 1.0+)
    """
    
    # Funções wrapper que formatam a saída das APIs para o assistente
    def get_country_info_wrapper(country_name: str) -> str:
        """
        Wrapper que busca informações sobre um país e formata a resposta.

        Args:
            country_name: Nome do país em inglês
        
        Returns:
            String formatada com informações do país ou mensagem de erro
        """
        result = get_country_info(country_name)

        if not result.get("success"):
            error_msg = result.get('error', 'Erro desconhecido')
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
        Wrapper que busca taxa de câmbio e formata a resposta.
        
        Args:
            base_currency: Código da moeda base
            target_currency: Código da moeda de destino
        
        Returns:
            String formatada com taxa de câmbio ou mensagem de erro
        """
        result = get_exchange_rate(base_currency, target_currency)
        
        if not result.get("success"):
            error_msg = result.get('error', 'Erro desconhecido')
            return f"Erro ao buscar taxa de câmbio: {error_msg}"
        
        base = result.get('base_currency', base_currency)
        target = result.get('target_currency', target_currency)
        rate = result.get('rate', 0)
        date = result.get('date', 'N/A')
        
        return f"""Taxa de câmbio:
                - {base} → {target}
                - Taxa: 1 {base} = {rate:.4f} {target}
                - Data: {date}"""
    
    # Inicializa o modelo de linguagem (usando GPT-3.5-turbo por ser mais barato)
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
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
                "Busca informações sobre um país, incluindo capital, população, "
                "região, moeda e idiomas. Use quando o usuário perguntar sobre países, "
                "capitais, população de países, ou informações geográficas."
            ),
            args_schema=CountryInfoInput
        ),
        StructuredTool.from_function(
            func=get_exchange_rate_wrapper,
            name="get_exchange_rate",
            description=(
                "Busca a taxa de câmbio atual entre duas moedas. "
                "Use quando o usuário perguntar sobre conversão de moedas, câmbio, "
                "ou valor de uma moeda em relação a outra."
            ),
            args_schema=ExchangeRateInput
        ),
    ]
    
    # Prompt do sistema que define o comportamento do assistente
    system_prompt = """Você é um assistente útil e amigável que pode buscar informações sobre:
                    - Países (capital, população, região, moeda, idiomas)
                    - Taxas de câmbio entre moedas

                    Use as ferramentas disponíveis quando necessário para responder às perguntas do usuário.
                    Seja claro, objetivo e amigável nas suas respostas.
                    Se não tiver certeza sobre algo, seja honesto e diga que não sabe.
                    Caso o usuário queira sair, diga que para sair ele precisa digitar 'sair', 'quit', 'exit' ou 'q'.
                    Caso o usuário queira limpar o histórico, diga que para limpar o histórico ele precisa digitar 'limpar',
                    'clear' ou 'reset'."""
    
    # Cria o agente usando a nova API do LangChain
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    return agent
