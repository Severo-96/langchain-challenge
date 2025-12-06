"""
Configuration of LangChain with OpenAI and Function Calling.
Here we configure the AI model and the available tools (functions).
"""

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from typing import List
from src.core.config import settings
from src.tools.country_tool import create_country_tool
from src.tools.exchange_tool import create_exchange_tool

def create_agent_executor():
    """
    Creates and configures the LangChain 1.0+ agent with Function Calling.
    
    Returns:
        Configured agent ready to use (new LangChain 1.0+ API)
    """
    # Inicializa o modelo de linguagem (usando GPT-4o-mini por ser mais barato)
    llm = ChatOpenAI(
        model=settings.model_name,
        temperature=settings.temperature,
        api_key=settings.openai_api_key
    )
    
    # Cria as ferramentas (tools) usando StructuredTool
    # Cada ferramenta permite que o assistente chame funções externas
    tools: List[StructuredTool] = [
        create_country_tool(),
        create_exchange_tool(),
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
