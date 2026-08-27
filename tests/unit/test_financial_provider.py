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
from app.services.financial.provider import YFinanceProvider


def test_normalized_models_to_dict():
    """Verify dataclasses serialize cleanly to dictionaries with SourceMetadata."""
    source = SourceMetadata(
        provider="yfinance",
        source_url="https://finance.yahoo.com/quote/NVDA",
        retrieved_at="2026-08-27T20:00:00Z",
        data_type="profile",
        symbol="NVDA",
    )

    profile = CompanyProfile(
        symbol="NVDA",
        name="NVIDIA Corporation",
        sector="Technology",
        industry="Semiconductors",
        country="United States",
        website="https://www.nvidia.com",
        description="NVIDIA Corporation designs graphics processing units and AI processors.",
        currency="USD",
        source=source,
    )

    d = profile.to_dict()
    assert d["symbol"] == "NVDA"
    assert d["name"] == "NVIDIA Corporation"
    assert d["source"]["provider"] == "yfinance"
    assert d["source"]["data_type"] == "profile"


def test_market_quote_to_dict():
    """Verify MarketQuote serialization."""
    source = SourceMetadata(
        provider="yfinance",
        source_url="https://finance.yahoo.com/quote/NVDA",
        retrieved_at="2026-08-27T20:00:00Z",
        data_type="quote",
        symbol="NVDA",
    )
    quote = MarketQuote(
        symbol="NVDA",
        current_price=128.50,
        currency="USD",
        change=2.50,
        change_percent=1.98,
        day_high=130.00,
        day_low=126.50,
        volume=45000000,
        market_cap=3150000000000.0,
        pe_ratio=65.4,
        fifty_two_week_high=140.76,
        fifty_two_week_low=45.20,
        source=source,
    )
    d = quote.to_dict()
    assert d["symbol"] == "NVDA"
    assert d["current_price"] == 128.50
    assert d["market_cap"] == 3150000000000.0


def test_yfinance_provider_empty_symbol():
    """Verify YFinanceProvider rejects empty symbols."""
    provider = YFinanceProvider()
    with pytest.raises(ValueError, match="cannot be empty"):
        provider.get_company_profile("")


def test_research_report_to_dict():
    """Verify ResearchReport serialization includes facts and sources."""
    from app.models.financial import ResearchReport

    report = ResearchReport(
        company="NVIDIA Corporation",
        symbol="NVDA",
        summary="Executive research summary.",
        facts={"current_price": 150.0, "pe_ratio": 25.0},
        fundamentals="Solid balance sheet.",
        valuation="Fair multiples.",
        market_context="Bullish trend.",
        risks=["Supply chain"],
        opportunities=["AI expansion"],
        user_context="Tech focus",
        sources=[{"provider": "yfinance", "symbol": "NVDA"}],
    )
    d = report.to_dict()
    assert d["company"] == "NVIDIA Corporation"
    assert d["facts"]["current_price"] == 150.0
    assert d["facts"]["pe_ratio"] == 25.0
    assert len(d["sources"]) == 1
