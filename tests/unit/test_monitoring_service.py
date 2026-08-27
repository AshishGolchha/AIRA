import pytest
from app.extensions import db
from app.models.user import User
from app.services.alert_service import AlertService
from app.services.financial.service import FinancialDataService
from app.services.monitoring_service import MonitoringService
from app.services.notifications import NotificationService
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture
def monitoring_setup(app):
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    wl_service = WatchlistService(financial_service=fin_service)
    alert_service = AlertService(
        portfolio_service=pf_service,
        watchlist_service=wl_service,
        financial_service=fin_service,
    )
    notif_service = NotificationService()
    monitoring_service = MonitoringService(
        alert_service=alert_service,
        notification_service=notif_service,
    )
    return {
        "monitoring_service": monitoring_service,
        "alert_service": alert_service,
        "portfolio_service": pf_service,
        "watchlist_service": wl_service,
    }


def test_monitoring_service_discovers_eligible_users(app, monitoring_setup):
    """Verify monitoring run processes only users with alerts_enabled=True."""
    ms = monitoring_setup["monitoring_service"]
    pf = monitoring_setup["portfolio_service"]

    # User 1: alerts_enabled=True
    u1 = User(email="mon_u1@example.com", alerts_enabled=True)
    u1.set_password("Password123!")
    db.session.add(u1)
    db.session.commit()
    pf.create_holding(user_id=u1.id, symbol="NVDA", quantity=10, average_cost=100)

    # User 2: alerts_enabled=False
    u2 = User(email="mon_u2@example.com", alerts_enabled=False)
    u2.set_password("Password123!")
    db.session.add(u2)
    db.session.commit()
    pf.create_holding(user_id=u2.id, symbol="MSFT", quantity=10, average_cost=100)

    res = ms.run_alert_monitoring(price_threshold=1.0, gain_loss_threshold=10.0)
    assert res["status"] == "completed"
    assert res["users_checked"] == 1  # Only u1 was eligible
    assert res["users_succeeded"] == 1
    assert res["alerts_generated"] >= 1


def test_monitoring_service_failure_isolation(app, monitoring_setup):
    """Verify failure for User 1 does not terminate processing for User 2."""
    ms = monitoring_setup["monitoring_service"]
    pf = monitoring_setup["portfolio_service"]

    u1 = User(email="fail_u1@example.com", alerts_enabled=True)
    u1.set_password("Password123!")
    u2 = User(email="success_u2@example.com", alerts_enabled=True)
    u2.set_password("Password123!")
    db.session.add_all([u1, u2])
    db.session.commit()

    pf.create_holding(user_id=u2.id, symbol="NVDA", quantity=10, average_cost=100)

    # Mock alert_service.check_and_create_alerts to fail only for u1
    orig_check = ms.alert_service.check_and_create_alerts

    def flaky_check(user_id, **kwargs):
        if user_id == u1.id:
            raise RuntimeError("Database connection glitch for user 1")
        return orig_check(user_id, **kwargs)

    ms.alert_service.check_and_create_alerts = flaky_check

    res = ms.run_alert_monitoring(price_threshold=1.0, gain_loss_threshold=10.0)
    assert res["status"] in ("partial_failure", "partial_success")
    assert res["users_checked"] == 2
    assert res["users_succeeded"] == 1
    assert res["users_failed"] == 1
    assert "User " in res["error_summary"]


def test_monitoring_service_empty_user_population(app, monitoring_setup):
    """Verify monitoring run with 0 users succeeds cleanly."""
    ms = monitoring_setup["monitoring_service"]
    res = ms.run_alert_monitoring()
    assert res["status"] == "completed"
    assert res["users_checked"] == 0
    assert res["alerts_generated"] == 0


def test_monitoring_service_run_user_monitoring(app, monitoring_setup):
    """Verify single user monitoring execution."""
    ms = monitoring_setup["monitoring_service"]
    pf = monitoring_setup["portfolio_service"]

    u = User(email="single_mon@example.com", alerts_enabled=True)
    u.set_password("Password123!")
    db.session.add(u)
    db.session.commit()
    pf.create_holding(user_id=u.id, symbol="NVDA", quantity=10, average_cost=100)

    res = ms.run_user_monitoring(user_id=u.id, price_threshold=1.0, gain_loss_threshold=10.0)
    assert res["status"] == "completed"
    assert res["alerts_generated"] >= 1
