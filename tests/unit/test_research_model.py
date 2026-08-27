from datetime import datetime, timezone
from app.models.research import ResearchRecord


def test_research_record_instantiation_and_serialization():
    """Verify ResearchRecord model instantiates and serializes correctly."""
    record = ResearchRecord(
        id=1,
        user_id=42,
        query="Analyze NVDA",
        symbol="NVDA",
        company="NVIDIA Corporation",
        summary="Solid semiconductor growth.",
        facts={"current_price": 150.0, "pe_ratio": 25.0},
        fundamentals="Growing revenues.",
        valuation="Fair multiples.",
        market_context="Positive momentum.",
        risks=["Supply chain"],
        opportunities=["AI boom"],
        user_context="Tech investor",
        sources=[{"provider": "yfinance", "symbol": "NVDA"}],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    full_dict = record.to_dict()
    assert full_dict["id"] == 1
    assert full_dict["user_id"] == 42
    assert full_dict["symbol"] == "NVDA"
    assert full_dict["facts"]["current_price"] == 150.0
    assert len(full_dict["risks"]) == 1
    assert len(full_dict["sources"]) == 1

    summary_dict = record.to_summary_dict()
    assert summary_dict["id"] == 1
    assert summary_dict["symbol"] == "NVDA"
    assert summary_dict["company"] == "NVIDIA Corporation"
    assert summary_dict["summary"] == "Solid semiconductor growth."
    assert "facts" not in summary_dict
    assert "sources" not in summary_dict
