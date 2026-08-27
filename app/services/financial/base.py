from abc import ABC, abstractmethod
from typing import Any

from app.models.financial import (
    CompanyProfile,
    FinancialStatement,
    HistoricalPrices,
    KeyMetrics,
    MarketQuote,
    NewsArticle,
)


class BaseFinancialProvider(ABC):
    """Abstract interface for external market and financial data providers."""

    @abstractmethod
    def get_company_profile(self, symbol: str) -> CompanyProfile:
        """Retrieves company business summary, sector, and metadata."""
        pass

    @abstractmethod
    def get_quote(self, symbol: str) -> MarketQuote:
        """Retrieves latest market price, volume, and day range."""
        pass

    @abstractmethod
    def get_historical_prices(
        self, symbol: str, period: str = "1mo", interval: str = "1d"
    ) -> HistoricalPrices:
        """Retrieves historical OHLCV series."""
        pass

    @abstractmethod
    def get_financials(
        self,
        symbol: str,
        statement_type: str = "income_statement",
        period_type: str = "annual",
    ) -> FinancialStatement:
        """Retrieves fundamental financial statement reports."""
        pass

    @abstractmethod
    def get_key_metrics(self, symbol: str) -> KeyMetrics:
        """Retrieves valuation ratios, profit margins, and balance sheet metrics."""
        pass

    @abstractmethod
    def get_company_news(self, symbol: str, limit: int = 5) -> list[NewsArticle]:
        """Retrieves recent news articles for the given symbol."""
        pass

    @abstractmethod
    def resolve_symbol(self, query: str) -> list[dict[str, Any]]:
        """Resolves a company name or ticker query to matching securities."""
        pass
