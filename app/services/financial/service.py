import re
import time
from typing import Any

from app.services.financial.base import BaseFinancialProvider
from app.services.financial.provider import YFinanceProvider

SYMBOL_REGEX = re.compile(r"^[A-Za-z0-9\.\-\^]{1,10}$")


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
    """Service layer exposing normalized financial research intelligence with lightweight caching."""

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

    def get_company_profile(self, symbol: str) -> dict[str, Any]:
        clean = self._validate_symbol(symbol)
        cache_key = f"profile:{clean}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        profile = self.provider.get_company_profile(clean)
        data = profile.to_dict()
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
