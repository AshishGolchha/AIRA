from decimal import Decimal, InvalidOperation
import re
from typing import Any
from flask import current_app, has_app_context

from app.extensions import db
from app.models.portfolio import PortfolioHolding
from app.services.financial.service import FinancialDataService

SYMBOL_REGEX = re.compile(r"^[A-Za-z0-9\.\-\^]{1,10}$")


class PortfolioService:
    """Service layer managing authenticated user portfolio holdings and valuation snapshots."""

    def __init__(self, financial_service: FinancialDataService | None = None):
        self.financial_service = financial_service or FinancialDataService()

    def _validate_symbol(self, symbol: str) -> str:
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Stock symbol cannot be empty.")
        clean = symbol.strip().upper()
        if not SYMBOL_REGEX.match(clean):
            raise ValueError(f"Invalid symbol format '{clean}'. Must be 1-10 alphanumeric characters.")
        return clean

    def _parse_quantity(self, quantity: Any) -> Decimal:
        if quantity is None:
            raise ValueError("Quantity is required.")
        try:
            val = Decimal(str(quantity).strip())
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Quantity must be a valid numeric value.")
        if val <= Decimal("0"):
            raise ValueError("Quantity must be greater than 0.")
        return val

    def _parse_average_cost(self, average_cost: Any) -> Decimal:
        if average_cost is None:
            raise ValueError("Average cost is required.")
        try:
            val = Decimal(str(average_cost).strip())
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Average cost must be a valid numeric value.")
        if val < Decimal("0"):
            raise ValueError("Average cost must be greater than or equal to 0.")
        return val

    def create_holding(
        self,
        user_id: int,
        symbol: str,
        quantity: Decimal | float | str,
        average_cost: Decimal | float | str,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Creates a single portfolio holding position for the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        clean_symbol = self._validate_symbol(symbol)
        dec_qty = self._parse_quantity(quantity)
        dec_avg_cost = self._parse_average_cost(average_cost)

        # Check duplicate per user
        existing = PortfolioHolding.query.filter_by(user_id=user_id, symbol=clean_symbol).first()
        if existing:
            raise ValueError(f"Holding for symbol '{clean_symbol}' already exists in your portfolio.")

        # Graceful company name lookup
        company_name = None
        try:
            profile = self.financial_service.get_company_profile(clean_symbol)
            if isinstance(profile, dict) and profile.get("name"):
                company_name = profile["name"]
        except Exception as e:
            if has_app_context():
                current_app.logger.info(f"Optional company profile lookup skipped for {clean_symbol}: {e}")

        holding = PortfolioHolding(
            user_id=user_id,
            symbol=clean_symbol,
            quantity=dec_qty,
            average_cost=dec_avg_cost,
            company_name=company_name,
            notes=notes,
        )
        db.session.add(holding)
        db.session.commit()
        return holding.to_dict()

    def list_holdings(self, user_id: int) -> list[dict[str, Any]]:
        """Lists all portfolio holdings for the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        holdings = PortfolioHolding.query.filter_by(user_id=user_id).order_by(PortfolioHolding.symbol.asc()).all()
        return [h.to_dict() for h in holdings]

    def get_holding(self, user_id: int, holding_id: int) -> dict[str, Any] | None:
        """Retrieves a single holding owned by the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        holding = PortfolioHolding.query.filter_by(id=holding_id, user_id=user_id).first()
        return holding.to_dict() if holding else None

    def update_holding(
        self,
        user_id: int,
        holding_id: int,
        quantity: Any = None,
        average_cost: Any = None,
        notes: Any = None,
    ) -> dict[str, Any] | None:
        """Updates quantity, average cost, or notes for a user's portfolio holding."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        holding = PortfolioHolding.query.filter_by(id=holding_id, user_id=user_id).first()
        if not holding:
            return None

        if quantity is not None:
            holding.quantity = self._parse_quantity(quantity)
        if average_cost is not None:
            holding.average_cost = self._parse_average_cost(average_cost)
        if notes is not None:
            holding.notes = notes

        db.session.commit()
        return holding.to_dict()

    def delete_holding(self, user_id: int, holding_id: int) -> bool:
        """Deletes a portfolio holding owned by the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        holding = PortfolioHolding.query.filter_by(id=holding_id, user_id=user_id).first()
        if not holding:
            return False

        db.session.delete(holding)
        db.session.commit()
        return True

    def get_portfolio_snapshot(self, user_id: int) -> dict[str, Any]:
        """Calculates deterministic read-only portfolio valuation snapshot for the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        holdings = PortfolioHolding.query.filter_by(user_id=user_id).order_by(PortfolioHolding.symbol.asc()).all()

        if not holdings:
            return {
                "holdings": [],
                "total_market_value": 0.0,
                "total_cost_basis": 0.0,
                "total_unrealized_gain_loss": 0.0,
                "total_unrealized_gain_loss_percent": None,
                "holdings_count": 0,
            }

        holding_snapshots: list[dict[str, Any]] = []
        total_market_value = Decimal("0")
        total_cost_basis = Decimal("0")

        for h in holdings:
            qty = Decimal(str(h.quantity))
            avg_cost = Decimal(str(h.average_cost))
            cost_basis = qty * avg_cost

            # Fetch quote
            quote_data = None
            try:
                quote_data = self.financial_service.get_quote(h.symbol)
            except Exception as e:
                if has_app_context():
                    current_app.logger.warning(f"Quote lookup failed for holding {h.symbol}: {e}")

            if isinstance(quote_data, dict) and quote_data.get("current_price") is not None:
                current_price = Decimal(str(quote_data["current_price"]))
                market_val = qty * current_price
                unrealized_gl = market_val - cost_basis
                unrealized_gl_pct = (
                    (unrealized_gl / cost_basis * Decimal("100")) if cost_basis > Decimal("0") else None
                )

                total_market_value += market_val
                total_cost_basis += cost_basis

                holding_snapshots.append({
                    "id": h.id,
                    "symbol": h.symbol,
                    "company_name": h.company_name,
                    "quantity": float(qty),
                    "average_cost": float(avg_cost),
                    "current_price": float(current_price),
                    "market_value": round(float(market_val), 2),
                    "cost_basis": round(float(cost_basis), 2),
                    "unrealized_gain_loss": round(float(unrealized_gl), 2),
                    "unrealized_gain_loss_percent": (
                        round(float(unrealized_gl_pct), 2) if unrealized_gl_pct is not None else None
                    ),
                    "currency": quote_data.get("currency", "USD"),
                    "source": quote_data.get("source"),
                })
            else:
                # Quote unavailable - do not fabricate price
                holding_snapshots.append({
                    "id": h.id,
                    "symbol": h.symbol,
                    "company_name": h.company_name,
                    "quantity": float(qty),
                    "average_cost": float(avg_cost),
                    "current_price": None,
                    "market_value": None,
                    "cost_basis": round(float(cost_basis), 2),
                    "unrealized_gain_loss": None,
                    "unrealized_gain_loss_percent": None,
                    "currency": None,
                    "source": None,
                })

        total_unrealized_gl = total_market_value - total_cost_basis
        total_unrealized_gl_pct = (
            (total_unrealized_gl / total_cost_basis * Decimal("100")) if total_cost_basis > Decimal("0") else None
        )

        return {
            "holdings": holding_snapshots,
            "total_market_value": round(float(total_market_value), 2),
            "total_cost_basis": round(float(total_cost_basis), 2),
            "total_unrealized_gain_loss": round(float(total_unrealized_gl), 2),
            "total_unrealized_gain_loss_percent": (
                round(float(total_unrealized_gl_pct), 2) if total_unrealized_gl_pct is not None else None
            ),
            "holdings_count": len(holdings),
        }
