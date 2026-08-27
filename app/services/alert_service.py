from typing import Any
from flask import current_app, has_app_context
from sqlalchemy import desc

from app.extensions import db
from app.models.alert import Alert
from app.services.financial.service import FinancialDataService
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService


class AlertService:
    """Orchestrates deterministic rule-based alert detection, deduplication, and user-scoped alert management."""

    def __init__(
        self,
        portfolio_service: PortfolioService | None = None,
        watchlist_service: WatchlistService | None = None,
        financial_service: FinancialDataService | None = None,
    ):
        self.financial_service = financial_service or FinancialDataService()
        self.portfolio_service = portfolio_service or PortfolioService(financial_service=self.financial_service)
        self.watchlist_service = watchlist_service or WatchlistService(financial_service=self.financial_service)

    def check_and_create_alerts(
        self,
        user_id: int,
        price_threshold: float | None = None,
        gain_loss_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """Runs deterministic alert rules against user's portfolio and watchlist, creating deduplicated alerts."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        p_thresh = (
            price_threshold
            if price_threshold is not None
            else (
                current_app.config.get("ALERT_PRICE_MOVE_THRESHOLD_PERCENT", 5.0)
                if has_app_context()
                else 5.0
            )
        )
        gl_thresh = (
            gain_loss_threshold
            if gain_loss_threshold is not None
            else (
                current_app.config.get("ALERT_PORTFOLIO_GAIN_LOSS_THRESHOLD_PERCENT", 10.0)
                if has_app_context()
                else 10.0
            )
        )

        def _has_active_alert(sym: str, a_type: str) -> bool:
            return (
                Alert.query.filter_by(
                    user_id=user_id,
                    symbol=sym,
                    alert_type=a_type,
                    is_dismissed=False,
                ).first()
                is not None
            )

        new_alerts: list[Alert] = []

        # 1. Inspect Portfolio Holdings
        snapshot = self.portfolio_service.get_portfolio_snapshot(user_id=user_id)
        for h in snapshot.get("holdings", []):
            sym = h["symbol"]
            cp = h.get("current_price")

            # Rule A: Data Quality Alert (Quote unavailable)
            if cp is None:
                if not _has_active_alert(sym, "data_quality"):
                    alert = Alert(
                        user_id=user_id,
                        symbol=sym,
                        company_name=h.get("company_name"),
                        alert_type="data_quality",
                        severity="warning",
                        title=f"Quote Data Unavailable for {sym}",
                        message=f"Live market quote could not be retrieved for holding {sym}.",
                        facts={"symbol": sym, "quantity": h.get("quantity")},
                        sources=[h.get("source")] if h.get("source") else [],
                    )
                    new_alerts.append(alert)
                    db.session.add(alert)
            else:
                # Rule B: Portfolio Gain / Loss Thresholds
                ugl_pct = h.get("unrealized_gain_loss_percent")
                if ugl_pct is not None:
                    if ugl_pct >= gl_thresh:
                        if not _has_active_alert(sym, "portfolio_gain"):
                            alert = Alert(
                                user_id=user_id,
                                symbol=sym,
                                company_name=h.get("company_name"),
                                alert_type="portfolio_gain",
                                severity="info",
                                title=f"Gain Alert: {sym} (+{ugl_pct:.2f}%)",
                                message=f"Holding {sym} has an unrealized gain of {ugl_pct:.2f}% (Market Value: ${h.get('market_value')}).",
                                facts=h,
                                sources=[h.get("source")] if h.get("source") else [],
                            )
                            new_alerts.append(alert)
                            db.session.add(alert)
                    elif ugl_pct <= -gl_thresh:
                        if not _has_active_alert(sym, "portfolio_loss"):
                            sev = "critical" if ugl_pct <= -(gl_thresh * 2) else "warning"
                            alert = Alert(
                                user_id=user_id,
                                symbol=sym,
                                company_name=h.get("company_name"),
                                alert_type="portfolio_loss",
                                severity=sev,
                                title=f"Loss Alert: {sym} ({ugl_pct:.2f}%)",
                                message=f"Holding {sym} has an unrealized loss of {ugl_pct:.2f}% (Market Value: ${h.get('market_value')}).",
                                facts=h,
                                sources=[h.get("source")] if h.get("source") else [],
                            )
                            new_alerts.append(alert)
                            db.session.add(alert)

                # Rule C: Daily Price Move Threshold on Holding
                try:
                    quote = self.financial_service.get_quote(sym)
                    if quote and quote.get("change_percent") is not None:
                        chg_pct = quote["change_percent"]
                        if abs(chg_pct) >= p_thresh:
                            if not _has_active_alert(sym, "price_move"):
                                sev = "warning" if chg_pct < 0 else "info"
                                alert = Alert(
                                    user_id=user_id,
                                    symbol=sym,
                                    company_name=h.get("company_name"),
                                    alert_type="price_move",
                                    severity=sev,
                                    title=f"Price Movement: {sym} ({chg_pct:+.2f}%)",
                                    message=f"{sym} moved {chg_pct:+.2f}% today to ${quote.get('current_price')}.",
                                    facts=quote,
                                    sources=[quote.get("source")] if quote.get("source") else [],
                                )
                                new_alerts.append(alert)
                                db.session.add(alert)
                except Exception as e:
                    if has_app_context():
                        current_app.logger.warning(f"Quote check failed for holding {sym}: {e}")

        # 2. Inspect Watchlist Items
        watchlist_items = self.watchlist_service.list_items(user_id=user_id)
        portfolio_symbols = {h["symbol"] for h in snapshot.get("holdings", [])}

        for w in watchlist_items:
            sym = w["symbol"]
            # Avoid redundant duplicate price_move alert if holding already alerted
            if sym in portfolio_symbols and _has_active_alert(sym, "price_move"):
                continue

            try:
                quote = self.financial_service.get_quote(sym)
                if quote and quote.get("change_percent") is not None:
                    chg_pct = quote["change_percent"]
                    if abs(chg_pct) >= p_thresh:
                        if not _has_active_alert(sym, "watchlist_move"):
                            sev = "warning" if chg_pct < 0 else "info"
                            alert = Alert(
                                user_id=user_id,
                                symbol=sym,
                                company_name=w.get("company_name"),
                                alert_type="watchlist_move",
                                severity=sev,
                                title=f"Watchlist Move: {sym} ({chg_pct:+.2f}%)",
                                message=f"Watchlist stock {sym} moved {chg_pct:+.2f}% today to ${quote.get('current_price')}.",
                                facts=quote,
                                sources=[quote.get("source")] if quote.get("source") else [],
                            )
                            new_alerts.append(alert)
                            db.session.add(alert)
            except Exception as e:
                if has_app_context():
                    current_app.logger.warning(f"Quote check failed for watchlist {sym}: {e}")

        if new_alerts:
            db.session.commit()

        return [a.to_dict() for a in new_alerts]

    def list_alerts(
        self,
        user_id: int,
        unread_only: bool = False,
        include_dismissed: bool = False,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Lists user-scoped alerts with pagination and filtering."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        page = max(1, page)
        limit = min(max(1, limit), 100)

        query = Alert.query.filter(Alert.user_id == user_id)
        if unread_only:
            query = query.filter(Alert.is_read.is_(False))
        if not include_dismissed:
            query = query.filter(Alert.is_dismissed.is_(False))

        total_count = query.count()
        alerts = (
            query.order_by(desc(Alert.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return {
            "alerts": [a.to_dict() for a in alerts],
            "total_count": total_count,
            "page": page,
            "limit": limit,
        }

    def get_alert(self, user_id: int, alert_id: int) -> dict[str, Any] | None:
        """Retrieves a single alert strictly scoped by user_id."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")
        if not isinstance(alert_id, int) or alert_id <= 0:
            return None

        alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
        return alert.to_dict() if alert else None

    def mark_as_read(self, user_id: int, alert_id: int) -> dict[str, Any] | None:
        """Marks a user-owned alert as read."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")
        if not isinstance(alert_id, int) or alert_id <= 0:
            return None

        alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
        if not alert:
            return None

        alert.is_read = True
        db.session.commit()
        return alert.to_dict()

    def dismiss_alert(self, user_id: int, alert_id: int) -> dict[str, Any] | None:
        """Dismisses a user-owned alert."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")
        if not isinstance(alert_id, int) or alert_id <= 0:
            return None

        alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
        if not alert:
            return None

        alert.is_dismissed = True
        db.session.commit()
        return alert.to_dict()
