from decimal import Decimal
import logging
import re
import time
from typing import Any

from app.services.financial.base import BaseFinancialProvider
from app.services.financial.provider import YFinanceProvider

logger = logging.getLogger(__name__)
SYMBOL_REGEX = re.compile(r"^[A-Za-z0-9\.\-\^]{1,20}$")


class _SimpleTTLCache:
    """Lightweight in-memory cache to prevent external API rate-limiting."""

    def __init__(self):
        self._cache: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        if key in self._cache:
            expires_at, value = self._cache[key]
            if time.time() < expires_at:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        self._cache[key] = (time.time() + ttl_seconds, value)

    def clear(self) -> None:
        self._cache.clear()


class FinancialDataService:
    """Service layer exposing normalized, real-world financial research intelligence with currency conversion & caching."""

    def __init__(self, provider: BaseFinancialProvider | None = None):
        self.provider = provider or YFinanceProvider()
        self.cache = _SimpleTTLCache()

    def _validate_symbol(self, symbol: str) -> str:
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Stock symbol cannot be empty.")
        clean_symbol = symbol.strip().upper()
        if not SYMBOL_REGEX.match(clean_symbol):
            raise ValueError(
                f"Invalid symbol format '{clean_symbol}'. Must be 1-10 alphanumeric characters."
            )
        return clean_symbol

    def get_fx_rate(self, from_currency: str = "USD", to_currency: str = "INR") -> float:
        """Retrieves and caches foreign exchange rates with resilient fallback."""
        clean_from = (from_currency or "USD").strip().upper()
        clean_to = (to_currency or "INR").strip().upper()

        if clean_from == clean_to:
            return 1.0

        cache_key = f"fx:{clean_from}:{clean_to}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        rate = 1.0
        try:
            if hasattr(self.provider, "get_fx_rate"):
                rate = self.provider.get_fx_rate(clean_from, clean_to)
            else:
                rate = 87.0 if (clean_from == "USD" and clean_to == "INR") else 1.0
        except Exception as e:
            logger.warning(f"FX rate lookup for {clean_from}/{clean_to} failed: {e}. Using baseline rate.")
            rate = 87.0 if (clean_from == "USD" and clean_to == "INR") else 1.0

        self.cache.set(cache_key, rate, ttl_seconds=900)  # 15 minutes TTL
        return rate

    def convert_to_inr(self, amount: float | int | Decimal | None, from_currency: str | None = "USD") -> float | None:
        """Converts any monetary amount from source currency to INR."""
        if amount is None:
            return None
        src = (from_currency or "USD").strip().upper()
        if src == "INR":
            return round(float(amount), 2)
        rate = self.get_fx_rate(src, "INR")
        return round(float(amount) * rate, 2)

    def _detect_source_currency(self, symbol: str, provider_currency: str | None = None) -> str:
        """Determines the true native source currency for a security."""
        if provider_currency and provider_currency.strip():
            return provider_currency.strip().upper()
        clean = symbol.strip().upper()
        if clean.endswith((".NS", ".BO", ".BSE", ".NSE")):
            return "INR"
        return "USD"

    def get_company_profile(self, symbol: str) -> dict[str, Any]:
        clean = self._validate_symbol(symbol)
        cache_key = f"profile:{clean}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        profile = self.provider.get_company_profile(clean)
        data = profile.to_dict()
        src_curr = self._detect_source_currency(clean, data.get("currency"))
        data["currency"] = "INR"
        data["source_currency"] = src_curr
        self.cache.set(cache_key, data, ttl_seconds=300)
        return data

    def get_quote(self, symbol: str) -> dict[str, Any]:
        clean = self._validate_symbol(symbol)
        cache_key = f"quote:{clean}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        quote = self.provider.get_quote(clean)
        data = quote.to_dict()
        src_curr = self._detect_source_currency(clean, data.get("currency"))

        if src_curr == "USD":
            fx_rate = self.get_fx_rate("USD", "INR")
            data["source_price"] = data.get("current_price")
            data["source_currency"] = "USD"
            data["fx_rate"] = fx_rate
            data["currency"] = "INR"

            # Convert monetary values to INR
            if data.get("current_price") is not None:
                data["current_price"] = round(data["current_price"] * fx_rate, 2)
            if data.get("day_high") is not None:
                data["day_high"] = round(data["day_high"] * fx_rate, 2)
            if data.get("day_low") is not None:
                data["day_low"] = round(data["day_low"] * fx_rate, 2)
            if data.get("fifty_two_week_high") is not None:
                data["fifty_two_week_high"] = round(data["fifty_two_week_high"] * fx_rate, 2)
            if data.get("fifty_two_week_low") is not None:
                data["fifty_two_week_low"] = round(data["fifty_two_week_low"] * fx_rate, 2)
            if data.get("change") is not None:
                data["change"] = round(data["change"] * fx_rate, 2)
            if data.get("market_cap") is not None:
                data["market_cap"] = round(data["market_cap"] * fx_rate, 2)
            # change_percent, volume, pe_ratio are non-monetary and remain untouched
        else:
            # Source currency is already INR - do not perform double conversion
            data["source_price"] = data.get("current_price")
            data["source_currency"] = "INR"
            data["fx_rate"] = 1.0
            data["currency"] = "INR"

        self.cache.set(cache_key, data, ttl_seconds=60)
        return data

    def get_historical_prices(
        self, symbol: str, period: str = "1mo", interval: str = "1d"
    ) -> dict[str, Any]:
        clean = self._validate_symbol(symbol)
        cache_key = f"history:{clean}:{period}:{interval}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        history = self.provider.get_historical_prices(clean, period=period, interval=interval)
        data = history.to_dict()
        src_curr = self._detect_source_currency(clean)

        if src_curr == "USD":
            fx_rate = self.get_fx_rate("USD", "INR")
            for p in data.get("prices", []):
                p["open"] = round(p["open"] * fx_rate, 2)
                p["high"] = round(p["high"] * fx_rate, 2)
                p["low"] = round(p["low"] * fx_rate, 2)
                p["close"] = round(p["close"] * fx_rate, 2)
            data["currency"] = "INR"
            data["source_currency"] = "USD"
            data["fx_rate"] = fx_rate
        else:
            data["currency"] = "INR"
            data["source_currency"] = "INR"
            data["fx_rate"] = 1.0

        self.cache.set(cache_key, data, ttl_seconds=300)
        return data

    def get_financials(
        self,
        symbol: str,
        statement_type: str = "income_statement",
        period_type: str = "annual",
    ) -> dict[str, Any]:
        clean = self._validate_symbol(symbol)
        cache_key = f"financials:{clean}:{statement_type}:{period_type}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        stmt = self.provider.get_financials(clean, statement_type=statement_type, period_type=period_type)
        data = stmt.to_dict()
        src_curr = self._detect_source_currency(clean)

        if src_curr == "USD":
            fx_rate = self.get_fx_rate("USD", "INR")
            for period in data.get("periods", []):
                metrics = period.get("metrics", {})
                for k, v in metrics.items():
                    if isinstance(v, (int, float)):
                        metrics[k] = round(v * fx_rate, 2)
            data["currency"] = "INR"
            data["source_currency"] = "USD"
            data["fx_rate"] = fx_rate
        else:
            data["currency"] = "INR"
            data["source_currency"] = "INR"
            data["fx_rate"] = 1.0

        self.cache.set(cache_key, data, ttl_seconds=600)
        return data

    def get_metrics(self, symbol: str) -> dict[str, Any]:
        clean = self._validate_symbol(symbol)
        cache_key = f"metrics:{clean}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        metrics = self.provider.get_key_metrics(clean)
        data = metrics.to_dict()
        src_curr = self._detect_source_currency(clean)

        if src_curr == "USD":
            fx_rate = self.get_fx_rate("USD", "INR")
            if data.get("total_revenue") is not None:
                data["total_revenue"] = round(data["total_revenue"] * fx_rate, 2)
            if data.get("total_debt") is not None:
                data["total_debt"] = round(data["total_debt"] * fx_rate, 2)
            if data.get("free_cash_flow") is not None:
                data["free_cash_flow"] = round(data["free_cash_flow"] * fx_rate, 2)
            data["currency"] = "INR"
            data["source_currency"] = "USD"
            data["fx_rate"] = fx_rate
            # Valuation ratios: pe_ratio, forward_pe, price_to_book, profit_margins,
            # operating_margins, return_on_equity, dividend_yield, beta are unitless ratios
        else:
            data["currency"] = "INR"
            data["source_currency"] = "INR"
            data["fx_rate"] = 1.0

        self.cache.set(cache_key, data, ttl_seconds=300)
        return data

    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        clean = self._validate_symbol(symbol)
        bounded_limit = min(max(1, limit), 20)
        cache_key = f"news:{clean}:{bounded_limit}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        news = self.provider.get_company_news(clean, limit=bounded_limit)
        data = [item.to_dict() for item in news]
        self.cache.set(cache_key, data, ttl_seconds=180)
        return data

    def resolve_company(self, query: str) -> list[dict[str, Any]]:
        clean_query = query.strip() if query else ""
        if not clean_query:
            return []
        cache_key = f"search:{clean_query.lower()}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        results = self.provider.resolve_symbol(clean_query)
        self.cache.set(cache_key, results, ttl_seconds=600)
        return results
