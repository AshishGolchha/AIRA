from decimal import Decimal
from datetime import datetime, timezone
from app.models.portfolio import PortfolioHolding


def test_portfolio_holding_model_instantiation_and_serialization():
    """Verify PortfolioHolding model instantiates with Decimal types and serializes correctly."""
    holding = PortfolioHolding(
        id=20,
        user_id=1,
        symbol="msft",
        company_name="Microsoft Corporation",
        quantity="15.75",
        average_cost="410.50",
        notes="Enterprise SaaS leader",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    assert holding.symbol == "MSFT"
    assert holding.quantity == Decimal("15.75")
    assert holding.average_cost == Decimal("410.50")

    data = holding.to_dict()
    assert data["id"] == 20
    assert data["symbol"] == "MSFT"
    assert data["company_name"] == "Microsoft Corporation"
    assert data["quantity"] == 15.75
    assert data["average_cost"] == 410.50
    assert data["notes"] == "Enterprise SaaS leader"
    assert "user_id" not in data
    assert "created_at" in data
    assert "updated_at" in data
