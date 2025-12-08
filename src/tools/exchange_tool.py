"""
LangChain tool for searching exchange rates.
"""

from textwrap import dedent

from langchain_core.tools import StructuredTool

from src.api.clients.exchange import get_exchange_rate
from src.core.schemas import ExchangeRateInput


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
    
    return dedent(f"""\
        Taxa de câmbio:
        - {base} → {target}
        - Taxa: 1 {base} = {rate:.4f} {target}
        - Data: {date}
    """)


def create_exchange_tool() -> StructuredTool:
    """
    Creates the exchange rate tool for LangChain.
    
    Returns:
        StructuredTool configured for exchange rate
    """
    return StructuredTool.from_function(
        func=get_exchange_rate_wrapper,
        name="get_exchange_rate",
        description=dedent("""\
            Search for current exchange rate between two currencies.
            The function returns an object with the exchange rate, with the
            base currency, the target currency, the exchange rate and the
            date of the exchange rate.
            Use when the user asks about currency conversion, exchange rate,
            or value of a currency in relation to another.
        """),
        args_schema=ExchangeRateInput
    )

