import pytest
from app.models.alert import Alert
from app.services.alert_service import AlertService
from app.services.financial.service import FinancialDataService
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture
def alert_service(app):
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    wl_service = WatchlistService(financial_service=fin_service)
    return AlertService(
        portfolio_service=pf_service,
        watchlist_service=wl_service,
        financial_service=fin_service,
    )


def test_alert_model_instantiation_and_serialization(app):
    """Verify Alert model fields and to_dict serialization."""
    alert = Alert(
        user_id=1,
        symbol="NVDA",
        company_name="NVIDIA Corporation",
        alert_type="price_move",
        severity="warning",
        title="Price Movement: NVDA (+5.50%)",
        message="NVDA moved 5.50% today.",
        facts={"current_price": 150.0, "change_percent": 5.5},
        sources=[{"provider": "yfinance", "symbol": "NVDA"}],
    )
    d = alert.to_dict()
    assert d["symbol"] == "NVDA"
    assert d["alert_type"] == "price_move"
    assert d["severity"] == "warning"
    assert d["is_read"] is False
    assert d["is_dismissed"] is False
    assert d["facts"]["current_price"] == 150.0
    assert len(d["sources"]) == 1


def test_alert_service_validation(alert_service):
    """Verify user_id validation across service methods."""
    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        alert_service.check_and_create_alerts(user_id=0)

    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        alert_service.list_alerts(user_id=-1)

    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        alert_service.get_alert(user_id=0, alert_id=1)

    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        alert_service.mark_as_read(user_id=-5, alert_id=1)

    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        alert_service.dismiss_alert(user_id=0, alert_id=1)


def test_alert_service_empty_portfolio_and_watchlist(app, alert_service):
    """Verify checking empty accounts generates 0 alerts safely."""
    alerts = alert_service.check_and_create_alerts(user_id=1)
    assert alerts == []


def test_alert_service_portfolio_gain_loss_and_price_move_rules(app, alert_service):
    """Verify deterministic detection of gain/loss and price movement alerts."""
    # 1. Holding with gain: 10 NVDA @ $100 -> current price $150 (mock), +50% gain, +3.45% move (mock)
    alert_service.portfolio_service.create_holding(
        user_id=1, symbol="NVDA", quantity=10, average_cost=100
    )

    # 2. Holding with loss: 10 MSFT @ $200 -> current price $150 (mock), -25% loss (critical), +3.45% move
    alert_service.portfolio_service.create_holding(
        user_id=1, symbol="MSFT", quantity=10, average_cost=200
    )

    # Run check with gain_loss_threshold=10.0, price_threshold=1.0
    created = alert_service.check_and_create_alerts(
        user_id=1, price_threshold=1.0, gain_loss_threshold=10.0
    )

    # We expect:
    # - NVDA: portfolio_gain alert (+50%) & price_move alert (+1.01%)
    # - MSFT: portfolio_loss alert (-25% critical) & price_move alert (+1.01%)
    assert len(created) == 4
    types = {(a["symbol"], a["alert_type"]) for a in created}
    assert ("NVDA", "portfolio_gain") in types
    assert ("NVDA", "price_move") in types
    assert ("MSFT", "portfolio_loss") in types
    assert ("MSFT", "price_move") in types

    # Check MSFT severity is critical (loss <= -20%)
    msft_loss = next(a for a in created if a["symbol"] == "MSFT" and a["alert_type"] == "portfolio_loss")
    assert msft_loss["severity"] == "critical"

    # Duplicate Prevention: Running check again should create 0 new alerts!
    repeated = alert_service.check_and_create_alerts(
        user_id=1, price_threshold=1.0, gain_loss_threshold=10.0
    )
    assert len(repeated) == 0


def test_alert_service_watchlist_move_rule(app, alert_service):
    """Verify watchlist price move alerts."""
    alert_service.watchlist_service.add_item(user_id=1, symbol="AAPL", priority="high")

    # AAPL mock change_percent is +1.01%
    # If price_threshold=1.0 -> creates watchlist_move alert
    created = alert_service.check_and_create_alerts(user_id=1, price_threshold=1.0)
    assert len(created) == 1
    assert created[0]["symbol"] == "AAPL"
    assert created[0]["alert_type"] == "watchlist_move"


def test_alert_service_data_quality_rule(app):
    """Verify data quality alert when market quote is unavailable for a holding."""
    class FailingQuoteProvider(MockFinancialProvider):
        def get_quote(self, symbol: str):
            raise RuntimeError("Live market feed offline")

    fin_service = FinancialDataService(provider=FailingQuoteProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    wl_service = WatchlistService(financial_service=fin_service)
    service = AlertService(portfolio_service=pf_service, watchlist_service=wl_service, financial_service=fin_service)

    pf_service.create_holding(user_id=1, symbol="NVDA", quantity=10, average_cost=100)

    created = service.check_and_create_alerts(user_id=1)
    assert len(created) == 1
    assert created[0]["symbol"] == "NVDA"
    assert created[0]["alert_type"] == "data_quality"
    assert created[0]["severity"] == "warning"


def test_alert_service_crud_lifecycle(app, alert_service):
    """Verify list, get, mark_as_read, and dismiss alert workflow."""
    alert_service.portfolio_service.create_holding(user_id=1, symbol="NVDA", quantity=10, average_cost=100)
    created = alert_service.check_and_create_alerts(user_id=1, price_threshold=2.0, gain_loss_threshold=10.0)
    alert_id = created[0]["id"]

    # 1. Get alert
    fetched = alert_service.get_alert(user_id=1, alert_id=alert_id)
    assert fetched is not None
    assert fetched["is_read"] is False
    assert fetched["is_dismissed"] is False

    # 2. Mark as read
    updated = alert_service.mark_as_read(user_id=1, alert_id=alert_id)
    assert updated["is_read"] is True

    # 3. List with unread_only=True
    unread_res = alert_service.list_alerts(user_id=1, unread_only=True)
    assert alert_id not in [a["id"] for a in unread_res["alerts"]]

    # 4. Dismiss alert
    dismissed = alert_service.dismiss_alert(user_id=1, alert_id=alert_id)
    assert dismissed["is_dismissed"] is True

    # 5. List with include_dismissed=False (default)
    active_res = alert_service.list_alerts(user_id=1, include_dismissed=False)
    assert alert_id not in [a["id"] for a in active_res["alerts"]]

    # 6. List with include_dismissed=True
    all_res = alert_service.list_alerts(user_id=1, include_dismissed=True)
    assert alert_id in [a["id"] for a in all_res["alerts"]]
