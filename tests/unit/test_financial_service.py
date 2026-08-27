import pytest
from app.models.financial import (
    CompanyProfile,
    FinancialStatement,
    HistoricalPrices,
    KeyMetrics,
    MarketQuote,
    NewsArticle,
    PricePoint,
    SourceMetadata,
)
from app.services.financial.base import BaseFinancialProvider
from app.services.financial.service import FinancialDataService


class MockFinancialProvider(BaseFinancialProvider):
    def __init__(self):
        self.call_counts = {
            "profile": 0,
            "quote": 0,
            "history": 0,
            "financials": 0,
            "metrics": 0,
            "news": 0,
            "search": 0,
        }

    def _source(self, symbol: str, data_type: str) -> SourceMetadata:
        return SourceMetadata(
            provider="mock_provider",
            source_url=f"https://mock.finance/{symbol}",
            retrieved_at="2026-08-27T20:00:00Z",
            data_type=data_type,
            symbol=symbol,
        )

    def get_company_profile(self, symbol: str) -> CompanyProfile:
        self.call_counts["profile"] += 1
        if symbol == "UNKNOWN":
            raise ValueError(f"Company profile for '{symbol}' not found.")
        return CompanyProfile(
            symbol=symbol,
            name=f"{symbol} Inc.",
            sector="Technology",
            industry="Semiconductors",
            country="United States",
            website=f"https://www.{symbol.lower()}.com",
            description=f"Description for {symbol}",
            currency="USD",
            source=self._source(symbol, "profile"),
        )

    def get_quote(self, symbol: str) -> MarketQuote:
        self.call_counts["quote"] += 1
        return MarketQuote(
            symbol=symbol,
            current_price=150.0,
            currency="USD",
            change=1.5,
            change_percent=1.01,
            day_high=152.0,
            day_low=148.0,
            volume=1000000,
            market_cap=2000000000.0,
            pe_ratio=25.0,
            fifty_two_week_high=160.0,
            fifty_two_week_low=120.0,
            source=self._source(symbol, "quote"),
        )

    def get_historical_prices(self, symbol: str, period: str = "1mo", interval: str = "1d") -> HistoricalPrices:
        self.call_counts["history"] += 1
        return HistoricalPrices(
            symbol=symbol,
            period=period,
            interval=interval,
            prices=[PricePoint("2026-08-26", 148.0, 151.0, 147.5, 150.0, 1000000)],
            source=self._source(symbol, "history"),
        )

    def get_financials(self, symbol: str, statement_type: str = "income_statement", period_type: str = "annual") -> FinancialStatement:
        self.call_counts["financials"] += 1
        return FinancialStatement(
            symbol=symbol,
            statement_type=statement_type,
            period_type=period_type,
            periods=[{"date": "2025-12-31", "metrics": {"Total Revenue": 100000000.0}}],
            source=self._source(symbol, "financials"),
        )

    def get_key_metrics(self, symbol: str) -> KeyMetrics:
        self.call_counts["metrics"] += 1
        return KeyMetrics(
            symbol=symbol,
            pe_ratio=25.0,
            forward_pe=22.0,
            price_to_book=5.0,
            profit_margins=0.25,
            operating_margins=0.30,
            return_on_equity=0.28,
            dividend_yield=0.015,
            beta=1.1,
            free_cash_flow=25000000.0,
            total_revenue=100000000.0,
            total_debt=10000000.0,
            source=self._source(symbol, "metrics"),
        )

    def get_company_news(self, symbol: str, limit: int = 5) -> list[NewsArticle]:
        self.call_counts["news"] += 1
        return [
            NewsArticle(
                title=f"{symbol} Reports Record Earnings",
                publisher="Financial Times",
                link="https://mock.news/1",
                published_at="2026-08-27T18:00:00Z",
                summary="Strong revenue growth driven by AI demand.",
                source=self._source(symbol, "news"),
            )
        ]

    def resolve_symbol(self, query: str) -> list[dict]:
        self.call_counts["search"] += 1
        return [{"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "type": "Equity"}]


def test_financial_service_validation():
    """Verify symbol validation in FinancialDataService."""
    provider = MockFinancialProvider()
    service = FinancialDataService(provider=provider)

    # Empty symbol
    with pytest.raises(ValueError, match="cannot be empty"):
        service.get_company_profile("")

    # Invalid symbol format
    with pytest.raises(ValueError, match="Invalid symbol format"):
        service.get_company_profile("INVALID$$$CHARS")

    # Valid lowercase symbol normalized to uppercase
    profile = service.get_company_profile("aapl")
    assert profile["symbol"] == "AAPL"


def test_financial_service_ttl_caching():
    """Verify that subsequent calls hit the in-memory cache and don't re-invoke provider."""
    provider = MockFinancialProvider()
    service = FinancialDataService(provider=provider)

    # First call
    q1 = service.get_quote("NVDA")
    assert provider.call_counts["quote"] == 1
    assert q1["current_price"] == 150.0

    # Second call for same symbol should hit cache
    q2 = service.get_quote("NVDA")
    assert provider.call_counts["quote"] == 1  # Unchanged!
    assert q2["current_price"] == 150.0

    # Query for different symbol should invoke provider
    service.get_quote("MSFT")
    assert provider.call_counts["quote"] == 2


def test_financial_service_search():
    """Verify company symbol search and resolution."""
    provider = MockFinancialProvider()
    service = FinancialDataService(provider=provider)

    results = service.resolve_company("Nvidia")
    assert len(results) == 1
    assert results[0]["symbol"] == "NVDA"
    assert provider.call_counts["search"] == 1
