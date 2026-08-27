from datetime import datetime, timezone
from typing import Any
from flask import current_app, has_app_context
from sqlalchemy import desc

from app.extensions import db
from app.models.alert import Alert
from app.models.monitoring import AlertMonitoringRun
from app.models.notification import NotificationDelivery
from app.models.user import User
from app.services.alert_service import AlertService
from app.services.notifications.service import NotificationService
from app.services.portfolio_service import PortfolioService
from app.services.research_service import ResearchService
from app.services.watchlist_service import WatchlistService


class DashboardService:
    """Orchestration and read-model service synthesizing a unified investor dashboard snapshot."""

    def __init__(
        self,
        portfolio_service: PortfolioService | None = None,
        watchlist_service: WatchlistService | None = None,
        alert_service: AlertService | None = None,
        research_service: ResearchService | None = None,
        notification_service: NotificationService | None = None,
    ):
        self.portfolio_service = portfolio_service or PortfolioService()
        self.watchlist_service = watchlist_service or WatchlistService()
        self.alert_service = alert_service or AlertService()
        self.research_service = research_service or ResearchService()
        self.notification_service = notification_service or NotificationService()

    def get_dashboard(self, user_id: int) -> dict[str, Any]:
        """Assembles full structured dashboard snapshot for the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        # 1. User / Profile Summary
        profile_data = {
            "id": user.id,
            "email": user.email,
            "name": (
                user.profile.display_name
                if user.profile and user.profile.display_name
                else user.email.split("@")[0]
            ),
            "investment_focus": user.profile.investment_focus if user.profile else None,
            "risk_tolerance": (
                user.profile.risk_preference if user.profile and user.profile.risk_preference else "moderate"
            ),
            "investment_horizon": (
                user.profile.investment_horizon if user.profile else "long_term"
            ),
        }

        # 2. Portfolio Summary
        portfolio_snap = self.portfolio_service.get_portfolio_snapshot(user_id=user_id)
        holdings = portfolio_snap.get("holdings", [])
        sorted_holdings = sorted(
            holdings,
            key=lambda h: (h.get("market_value") or 0.0, h.get("cost_basis") or 0.0),
            reverse=True,
        )
        portfolio_data = {
            "total_market_value": portfolio_snap.get("total_market_value", 0.0),
            "total_cost_basis": portfolio_snap.get("total_cost_basis", 0.0),
            "unrealized_gain_loss": portfolio_snap.get("total_unrealized_gain_loss", 0.0),
            "unrealized_gain_loss_percent": portfolio_snap.get("total_unrealized_gain_loss_percent"),
            "holdings_count": portfolio_snap.get("holdings_count", 0),
            "top_holdings": sorted_holdings[:5],
        }

        # 3. Watchlist Summary
        watchlist_items = self.watchlist_service.list_items(user_id=user_id)
        watchlist_data = {
            "total_count": len(watchlist_items),
            "high_priority_count": sum(1 for w in watchlist_items if w.get("priority") == "high"),
            "normal_priority_count": sum(1 for w in watchlist_items if w.get("priority") == "normal"),
            "low_priority_count": sum(1 for w in watchlist_items if w.get("priority") == "low"),
            "items": watchlist_items[:5],
        }

        # 4. Alert Summary
        unread_count = Alert.query.filter_by(user_id=user_id, is_read=False, is_dismissed=False).count()
        critical_count = Alert.query.filter_by(user_id=user_id, severity="critical", is_dismissed=False).count()
        warning_count = Alert.query.filter_by(user_id=user_id, severity="warning", is_dismissed=False).count()
        info_count = Alert.query.filter_by(user_id=user_id, severity="info", is_dismissed=False).count()
        recent_alerts = (
            Alert.query.filter_by(user_id=user_id, is_dismissed=False)
            .order_by(desc(Alert.created_at))
            .limit(5)
            .all()
        )
        alerts_data = {
            "unread_count": unread_count,
            "critical_count": critical_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "recent": [a.to_dict() for a in recent_alerts],
        }

        # 5. Recent Research History Summary
        history_res = self.research_service.get_user_history(user_id=user_id, page=1, limit=5)
        research_data = {
            "total_reports": history_res.get("total", 0),
            "recent": history_res.get("history", []),
        }

        # 6. Notification Summary
        pref = self.notification_service.get_or_create_preferences(user_id)
        pending_retry_count = NotificationDelivery.query.filter_by(
            user_id=user_id, is_retryable=True, status="failed"
        ).count()
        failed_count = NotificationDelivery.query.filter_by(
            user_id=user_id, status="failed"
        ).count()
        delivered_count = NotificationDelivery.query.filter_by(
            user_id=user_id, status="delivered"
        ).count()

        enabled_channels = []
        if pref.in_app_enabled:
            enabled_channels.append("in_app")
        if pref.email_enabled:
            enabled_channels.append("email")
        if pref.webhook_enabled:
            enabled_channels.append("webhook")

        notifications_data = {
            "preferences": {
                "in_app_enabled": pref.in_app_enabled,
                "email_enabled": pref.email_enabled,
                "webhook_enabled": pref.webhook_enabled,
                "minimum_severity": pref.minimum_severity,
                "alert_types": pref.alert_types,
            },
            "enabled_channels": enabled_channels,
            "pending_retry_count": pending_retry_count,
            "failed_delivery_count": failed_count,
            "delivered_count": delivered_count,
        }

        # 7. Monitoring Status
        monitoring_enabled = (
            current_app.config.get("ALERT_MONITORING_ENABLED", True)
            if has_app_context()
            else True
        )
        latest_run = (
            AlertMonitoringRun.query.order_by(desc(AlertMonitoringRun.created_at)).first()
        )
        latest_run_summary = None
        if latest_run:
            latest_run_summary = {
                "id": latest_run.id,
                "status": latest_run.status,
                "started_at": latest_run.started_at.isoformat() if latest_run.started_at else None,
                "completed_at": latest_run.completed_at.isoformat() if latest_run.completed_at else None,
                "duration_seconds": latest_run.to_dict().get("duration_seconds"),
            }

        monitoring_data = {
            "system_monitoring_enabled": monitoring_enabled,
            "user_alerts_enabled": bool(user.alerts_enabled),
            "latest_run": latest_run_summary,
        }

        # 8. Portfolio Intelligence Summary (Zero LLM on GET)
        portfolio_intelligence_data = {
            "available": False,
            "message": "Portfolio intelligence is generated on demand. Use POST /api/v1/portfolio/intelligence to generate AI insights.",
        }

        return {
            "user": profile_data,
            "portfolio": portfolio_data,
            "watchlist": watchlist_data,
            "alerts": alerts_data,
            "research": research_data,
            "notifications": notifications_data,
            "monitoring": monitoring_data,
            "portfolio_intelligence": portfolio_intelligence_data,
        }

    def get_summary(self, user_id: int) -> dict[str, Any]:
        """Assembles lightweight top-level metrics for quick widget/header rendering."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        portfolio_snap = self.portfolio_service.get_portfolio_snapshot(user_id=user_id)
        watchlist_items = self.watchlist_service.list_items(user_id=user_id)
        unread_alerts = Alert.query.filter_by(
            user_id=user_id, is_read=False, is_dismissed=False
        ).count()
        critical_alerts = Alert.query.filter_by(
            user_id=user_id, severity="critical", is_dismissed=False
        ).count()
        history_res = self.research_service.get_user_history(user_id=user_id, page=1, limit=1)

        monitoring_enabled = (
            current_app.config.get("ALERT_MONITORING_ENABLED", True)
            if has_app_context()
            else True
        )

        return {
            "portfolio_market_value": portfolio_snap.get("total_market_value", 0.0),
            "portfolio_gain_loss_percent": portfolio_snap.get("total_unrealized_gain_loss_percent"),
            "holdings_count": portfolio_snap.get("holdings_count", 0),
            "watchlist_count": len(watchlist_items),
            "unread_alerts_count": unread_alerts,
            "critical_alerts_count": critical_alerts,
            "research_reports_count": history_res.get("total", 0),
            "monitoring_enabled": monitoring_enabled,
        }
