import json
import math
from typing import Any
from crewai.tools import tool

from app.services.financial.service import FinancialDataService


def _clean_json_values(obj: Any) -> Any:
    """Recursively replaces NaN, Infinity, and -Infinity with None for strict JSON compliance."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: _clean_json_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_clean_json_values(item) for item in obj]
    return obj


def _safe_json_dumps(data: Any) -> str:
    return json.dumps(_clean_json_values(data))


def build_financial_tools(financial_service: FinancialDataService):
    """Factory function creating CrewAI tools that wrap the existing FinancialDataService."""

    @tool("Get Company Profile")
    def get_company_profile(symbol: str) -> str:
        """Retrieves company profile, business description, sector, industry, country, and website for a stock symbol."""
        try:
            profile = financial_service.get_company_profile(symbol)
            return _safe_json_dumps(profile)
        except Exception as e:
            return f"Error retrieving company profile: {e}"

    @tool("Get Market Quote")
    def get_market_quote(symbol: str) -> str:
        """Retrieves real-time or latest stock quote including current price, day high/low, volume, 52-week range, and PE ratio."""
        try:
            quote = financial_service.get_quote(symbol)
            return _safe_json_dumps(quote)
        except Exception as e:
            return f"Error retrieving market quote: {e}"

    @tool("Get Historical Prices")
    def get_historical_prices(symbol: str, period: str = "1mo", interval: str = "1d") -> str:
        """Retrieves historical OHLCV price series for a symbol over a period (e.g. 1mo, 3mo, 1y) and interval (e.g. 1d, 1wk)."""
        try:
            history = financial_service.get_historical_prices(symbol, period=period, interval=interval)
            return _safe_json_dumps(history)
        except Exception as e:
            return f"Error retrieving historical prices: {e}"

    @tool("Get Financial Statements")
    def get_financial_statements(
        symbol: str, statement_type: str = "income_statement", period_type: str = "annual"
    ) -> str:
        """Retrieves fundamental financial statements (income_statement, balance_sheet, cash_flow) for annual or quarterly periods."""
        try:
            financials = financial_service.get_financials(
                symbol, statement_type=statement_type, period_type=period_type
            )
            return _safe_json_dumps(financials)
        except Exception as e:
            return f"Error retrieving financial statements: {e}"

    @tool("Get Key Metrics")
    def get_key_metrics(symbol: str) -> str:
        """Retrieves key financial ratios including trailing PE, forward PE, price-to-book, profit margins, ROE, dividend yield, and debt metrics."""
        try:
            metrics = financial_service.get_metrics(symbol)
            return _safe_json_dumps(metrics)
        except Exception as e:
            return f"Error retrieving key metrics: {e}"

    @tool("Get Company News")
    def get_company_news(symbol: str, limit: int = 5) -> str:
        """Retrieves recent news articles with titles, publishers, links, and summaries for a stock symbol."""
        try:
            news = financial_service.get_news(symbol, limit=limit)
            return _safe_json_dumps(news)
        except Exception as e:
            return f"Error retrieving company news: {e}"

    @tool("Search Company Symbol")
    def search_company_symbol(query: str) -> str:
        """Searches and resolves a company name to its matching stock ticker symbols."""
        try:
            results = financial_service.resolve_company(query)
            return _safe_json_dumps(results)
        except Exception as e:
            return f"Error resolving company symbol: {e}"

    return [
        get_company_profile,
        get_market_quote,
        get_historical_prices,
        get_financial_statements,
        get_key_metrics,
        get_company_news,
        search_company_symbol,
    ]
