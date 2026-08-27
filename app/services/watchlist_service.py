import re
from typing import Any
from flask import current_app, has_app_context

from app.extensions import db
from app.models.watchlist import WatchlistItem
from app.services.financial.service import FinancialDataService

SYMBOL_REGEX = re.compile(r"^[A-Za-z0-9\.\-\^]{1,10}$")
ALLOWED_PRIORITIES = {"low", "normal", "high"}


class WatchlistService:
    """Service layer managing authenticated user watchlists."""

    def __init__(self, financial_service: FinancialDataService | None = None):
        self.financial_service = financial_service or FinancialDataService()

    def _validate_symbol(self, symbol: str) -> str:
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Stock symbol cannot be empty.")
        clean = symbol.strip().upper()
        if not SYMBOL_REGEX.match(clean):
            raise ValueError(f"Invalid symbol format '{clean}'. Must be 1-10 alphanumeric characters.")
        return clean

    def _validate_priority(self, priority: str | None) -> str:
        if not priority:
            return "normal"
        clean = priority.strip().lower()
        if clean not in ALLOWED_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of: {', '.join(sorted(ALLOWED_PRIORITIES))}.")
        return clean

    def add_item(
        self,
        user_id: int,
        symbol: str,
        notes: str | None = None,
        priority: str = "normal",
    ) -> dict[str, Any]:
        """Adds a security to the authenticated user's watchlist."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        clean_symbol = self._validate_symbol(symbol)
        clean_priority = self._validate_priority(priority)

        # Check duplicate per user
        existing = WatchlistItem.query.filter_by(user_id=user_id, symbol=clean_symbol).first()
        if existing:
            raise ValueError(f"Symbol '{clean_symbol}' already exists in your watchlist.")

        # Graceful company name resolution
        company_name = None
        try:
            profile = self.financial_service.get_company_profile(clean_symbol)
            if isinstance(profile, dict) and profile.get("name"):
                company_name = profile["name"]
        except Exception as e:
            if has_app_context():
                current_app.logger.info(f"Optional company profile lookup skipped for {clean_symbol}: {e}")

        item = WatchlistItem(
            user_id=user_id,
            symbol=clean_symbol,
            company_name=company_name,
            notes=notes,
            priority=clean_priority,
        )
        db.session.add(item)
        db.session.commit()
        return item.to_dict()

    def list_items(self, user_id: int, priority: str | None = None) -> list[dict[str, Any]]:
        """Lists watchlist items for the authenticated user, optionally filtered by priority."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        query = WatchlistItem.query.filter_by(user_id=user_id)
        if priority:
            clean_priority = priority.strip().lower()
            if clean_priority in ALLOWED_PRIORITIES:
                query = query.filter_by(priority=clean_priority)

        items = query.order_by(WatchlistItem.created_at.desc()).all()
        return [item.to_dict() for item in items]

    def get_item(self, user_id: int, item_id: int) -> dict[str, Any] | None:
        """Retrieves a single watchlist item strictly scoped to the user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        item = WatchlistItem.query.filter_by(id=item_id, user_id=user_id).first()
        return item.to_dict() if item else None

    def update_item(
        self,
        user_id: int,
        item_id: int,
        notes: str | None = None,
        priority: str | None = None,
    ) -> dict[str, Any] | None:
        """Updates notes and/or priority for a user's watchlist item."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        item = WatchlistItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            return None

        if priority is not None:
            item.priority = self._validate_priority(priority)
        if notes is not None:
            item.notes = notes

        db.session.commit()
        return item.to_dict()

    def delete_item(self, user_id: int, item_id: int) -> bool:
        """Deletes a watchlist item owned by the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        item = WatchlistItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            return False

        db.session.delete(item)
        db.session.commit()
        return True
