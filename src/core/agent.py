"""
Configuration of LangChain with OpenAI and Function Calling.
Here we configure the AI model and the available tools (functions).
"""

import sqlite3
from textwrap import dedent
from typing import List

from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver

from src.core.config import settings
from src.tools.country_tool import create_country_tool
from src.tools.exchange_tool import create_exchange_tool

def create_agent_executor(
    llm: ChatOpenAI | None = None,
    checkpointer: SqliteSaver | None = None
) -> tuple[Runnable, SqliteSaver]:
    """
    Creates and configures the LangChain 1.0+ agent with Function Calling and checkpoint support.
    
    Args:
        llm: Language model instance. If None, creates a new ChatOpenAI instance
            using settings from config.
        checkpointer: Checkpoint saver instance. If None, creates a new SqliteSaver
            using settings from config.
    
    Returns:
        Tuple of (configured agent, checkpointer, llm) ready to use
    """
    # Initialize language model if not provided
    if llm is None:
        llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            api_key=settings.openai_api_key
        )
    
    # Initialize checkpointer if not provided
    if checkpointer is None:
        # Ensure checkpoint database directory exists
        checkpoint_path = settings.checkpoint_db_path
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        # Create SQLite connection and SqliteSaver directly
        # check_same_thread=False is OK as SqliteSaver uses a lock for thread safety
        conn = sqlite3.connect(str(checkpoint_path), check_same_thread=False)
        checkpointer = SqliteSaver(conn)
    
    # Create tools using StructuredTool
    # Each tool allows the assistant to call external functions
    tools: List[StructuredTool] = [
        create_country_tool(),
        create_exchange_tool(),
    ]
    
    # System prompt that defines assistant behavior
    system_prompt = dedent("""\
        You are a useful and friendly assistant that can search
        for information about:
        - Countries (capital, population, region, currency, languages)
        - Exchange rate between currencies

        Use the available tools when necessary to answer the user's questions.
        Be clear, objective and friendly in your responses, whenever possible
        show a summary of the information shown.
        If you are not sure about something, be honest and say you don't know.

        If the user wants to exit, say that to exit he needs to type 'sair',
        'quit', 'exit' or 'q'.
        If the user wants to clear the history, say that to clear the history
        he needs to type 'limpar', 'clear' or 'reset'.
    """)
    
    # Create agent using LangChain's new API with checkpointer
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer
    )
    
    return agent, checkpointer
