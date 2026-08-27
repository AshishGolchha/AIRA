import pytest
from app.services.financial.service import FinancialDataService
from app.services.portfolio_service import PortfolioService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture
def portfolio_service():
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    return PortfolioService(financial_service=fin_service)


def test_portfolio_service_validations(portfolio_service):
    """Verify input validation for user_id, symbol, quantity, and average_cost."""
    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        portfolio_service.create_holding(user_id=0, symbol="NVDA", quantity=10, average_cost=100)

    with pytest.raises(ValueError, match="Stock symbol cannot be empty"):
        portfolio_service.create_holding(user_id=1, symbol="", quantity=10, average_cost=100)

    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        portfolio_service.create_holding(user_id=1, symbol="NVDA", quantity=0, average_cost=100)

    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        portfolio_service.create_holding(user_id=1, symbol="NVDA", quantity=-5, average_cost=100)

    with pytest.raises(ValueError, match="Average cost must be greater than or equal to 0"):
        portfolio_service.create_holding(user_id=1, symbol="NVDA", quantity=10, average_cost=-1)


def test_portfolio_service_crud_lifecycle(app, portfolio_service):
    """Verify portfolio holdings CRUD operations with multi-tenant isolation."""
    # 1. Create holding
    h = portfolio_service.create_holding(
        user_id=1,
        symbol="nvda",
        quantity="10.5",
        average_cost="120.00",
        notes="Initial buy",
    )
    assert h["symbol"] == "NVDA"
    assert h["quantity"] == 10.5
    assert h["average_cost"] == 120.00
    assert h["company_name"] == "NVDA Inc."
    h_id = h["id"]

    # 2. Duplicate symbol rejected for same user
    with pytest.raises(ValueError, match="already exists in your portfolio"):
        portfolio_service.create_holding(user_id=1, symbol="NVDA", quantity=5, average_cost=130)

    # 3. User 2 can create same symbol
    h_u2 = portfolio_service.create_holding(user_id=2, symbol="NVDA", quantity=20, average_cost=110)
    assert h_u2["id"] != h_id

    # 4. List holdings
    holdings_u1 = portfolio_service.list_holdings(user_id=1)
    assert len(holdings_u1) == 1
    assert holdings_u1[0]["id"] == h_id

    # 5. Get holding (User 2 cannot access User 1's holding)
    assert portfolio_service.get_holding(user_id=1, holding_id=h_id) is not None
    assert portfolio_service.get_holding(user_id=2, holding_id=h_id) is None

    # 6. Update holding
    updated = portfolio_service.update_holding(
        user_id=1,
        holding_id=h_id,
        quantity="15.0",
        average_cost="125.50",
        notes="Averaged up",
    )
    assert updated["quantity"] == 15.0
    assert updated["average_cost"] == 125.50

    # User 2 cannot update User 1's holding
    assert portfolio_service.update_holding(user_id=2, holding_id=h_id, quantity=100) is None

    # 7. Delete holding
    assert portfolio_service.delete_holding(user_id=2, holding_id=h_id) is False
    assert portfolio_service.delete_holding(user_id=1, holding_id=h_id) is True
    assert portfolio_service.get_holding(user_id=1, holding_id=h_id) is None


def test_portfolio_service_snapshot_calculations_and_zero_cost(app, portfolio_service):
    """
    Verify deterministic valuation snapshot calculation:
    - market_value = qty * current_price ($150.0 from MockFinancialProvider)
    - cost_basis = qty * average_cost
    - unrealized_gain_loss = market_val - cost_basis
    - zero-cost percentage safe handling (null instead of divide-by-zero)
    """
    # Position 1: 10 shares NVDA @ $100 average cost (Market price is $150.0 in MockFinancialProvider)
    # Market value = 10 * 150 = 1500, Cost basis = 1000, Gain = 500, Gain % = 50.0%
    portfolio_service.create_holding(user_id=1, symbol="NVDA", quantity=10, average_cost=100)

    # Position 2: 5 shares MSFT @ $0.0 average cost (e.g. gifted/spun-off shares)
    # Market value = 5 * 150 = 750, Cost basis = 0, Gain = 750, Gain % = None (zero-cost handling)
    portfolio_service.create_holding(user_id=1, symbol="MSFT", quantity=5, average_cost=0)

    snapshot = portfolio_service.get_portfolio_snapshot(user_id=1)
    assert snapshot["holdings_count"] == 2
    assert snapshot["total_cost_basis"] == 1000.00
    assert snapshot["total_market_value"] == 2250.00
    assert snapshot["total_unrealized_gain_loss"] == 1250.00
    assert snapshot["total_unrealized_gain_loss_percent"] == 125.00  # (1250 / 1000) * 100

    holdings = snapshot["holdings"]
    nvda = next(h for h in holdings if h["symbol"] == "NVDA")
    assert nvda["market_value"] == 1500.00
    assert nvda["cost_basis"] == 1000.00
    assert nvda["unrealized_gain_loss"] == 500.00
    assert nvda["unrealized_gain_loss_percent"] == 50.00

    msft = next(h for h in holdings if h["symbol"] == "MSFT")
    assert msft["market_value"] == 750.00
    assert msft["cost_basis"] == 0.00
    assert msft["unrealized_gain_loss"] == 750.00
    assert msft["unrealized_gain_loss_percent"] is None  # Safe zero division


def test_portfolio_service_snapshot_quote_unavailable_handling(app):
    """Verify that quote failures do not fabricate prices."""
    class FailingQuoteProvider(MockFinancialProvider):
        def get_quote(self, symbol: str):
            raise RuntimeError("External market provider unavailable.")

    service = PortfolioService(
        financial_service=FinancialDataService(provider=FailingQuoteProvider())
    )

    service.create_holding(user_id=1, symbol="NVDA", quantity=10, average_cost=100)
    snapshot = service.get_portfolio_snapshot(user_id=1)

    assert snapshot["holdings_count"] == 1
    assert snapshot["holdings"][0]["current_price"] is None
    assert snapshot["holdings"][0]["market_value"] is None
    assert snapshot["holdings"][0]["cost_basis"] == 1000.00
    assert snapshot["holdings"][0]["unrealized_gain_loss"] is None
