from datetime import datetime, timezone
from typing import Any
import yfinance as yf

from app.models.financial import (
    CompanyProfile,
    FinancialStatement,
    HistoricalPrices,
    KeyMetrics,
    MarketQuote,
    NewsArticle,
    PricePoint,
    SourceMetadata,
)
from app.services.financial.base import BaseFinancialProvider


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class YFinanceProvider(BaseFinancialProvider):
    """Financial and market data provider using Yahoo Finance (yfinance)."""

    def _get_ticker(self, symbol: str) -> yf.Ticker:
        clean_symbol = symbol.strip().upper()
        if not clean_symbol:
            raise ValueError("Stock symbol cannot be empty.")
        return yf.Ticker(clean_symbol)

    def get_company_profile(self, symbol: str) -> CompanyProfile:
        clean_symbol = symbol.strip().upper()
        ticker = self._get_ticker(clean_symbol)
        try:
            info = ticker.info or {}
        except Exception as e:
            raise RuntimeError(f"Failed to fetch profile for '{clean_symbol}': {e}")

        name = info.get("longName") or info.get("shortName")
        if not name:
            raise ValueError(f"Company profile for '{clean_symbol}' not found.")

        source = SourceMetadata(
            provider="yfinance",
            source_url=f"https://finance.yahoo.com/quote/{clean_symbol}",
            retrieved_at=_now_utc_iso(),
            data_type="profile",
            symbol=clean_symbol,
        )

        return CompanyProfile(
            symbol=clean_symbol,
            name=name,
            sector=info.get("sector"),
            industry=info.get("industry"),
            country=info.get("country"),
            website=info.get("website"),
            description=info.get("longBusinessSummary"),
            currency=info.get("currency"),
            source=source,
        )

    def get_quote(self, symbol: str) -> MarketQuote:
        clean_symbol = symbol.strip().upper()
        ticker = self._get_ticker(clean_symbol)
        try:
            info = ticker.info or {}
        except Exception as e:
            raise RuntimeError(f"Failed to fetch quote for '{clean_symbol}': {e}")

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        if current_price is None:
            raise ValueError(f"Real-time quote for '{clean_symbol}' not available.")

        source = SourceMetadata(
            provider="yfinance",
            source_url=f"https://finance.yahoo.com/quote/{clean_symbol}",
            retrieved_at=_now_utc_iso(),
            data_type="quote",
            symbol=clean_symbol,
        )

        return MarketQuote(
            symbol=clean_symbol,
            current_price=float(current_price),
            currency=info.get("currency"),
            change=info.get("regularMarketChange"),
            change_percent=info.get("regularMarketChangePercent"),
            day_high=info.get("dayHigh") or info.get("regularMarketDayHigh"),
            day_low=info.get("dayLow") or info.get("regularMarketDayLow"),
            volume=info.get("volume") or info.get("regularMarketVolume"),
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            source=source,
        )

    def get_historical_prices(
        self, symbol: str, period: str = "1mo", interval: str = "1d"
    ) -> HistoricalPrices:
        clean_symbol = symbol.strip().upper()
        ticker = self._get_ticker(clean_symbol)
        try:
            df = ticker.history(period=period, interval=interval)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch history for '{clean_symbol}': {e}")

        if df is None or df.empty:
            raise ValueError(
                f"No historical prices available for '{clean_symbol}' with period '{period}'."
            )

        prices: list[PricePoint] = []
        for idx, row in df.iterrows():
            date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)
            prices.append(
                PricePoint(
                    date=date_str,
                    open=round(float(row.get("Open", 0.0)), 4),
                    high=round(float(row.get("High", 0.0)), 4),
                    low=round(float(row.get("Low", 0.0)), 4),
                    close=round(float(row.get("Close", 0.0)), 4),
                    volume=int(row.get("Volume", 0)),
                )
            )

        source = SourceMetadata(
            provider="yfinance",
            source_url=f"https://finance.yahoo.com/quote/{clean_symbol}/history",
            retrieved_at=_now_utc_iso(),
            data_type="history",
            symbol=clean_symbol,
        )

        return HistoricalPrices(
            symbol=clean_symbol,
            period=period,
            interval=interval,
            prices=prices,
            source=source,
        )

    def get_financials(
        self,
        symbol: str,
        statement_type: str = "income_statement",
        period_type: str = "annual",
    ) -> FinancialStatement:
        clean_symbol = symbol.strip().upper()
        ticker = self._get_ticker(clean_symbol)

        statement_type = statement_type.lower().replace("-", "_")
        try:
            if statement_type in {"income_statement", "income", "financials"}:
                df = ticker.quarterly_income_stmt if period_type == "quarterly" else ticker.income_stmt
                normalized_type = "income_statement"
            elif statement_type in {"balance_sheet", "balance"}:
                df = ticker.quarterly_balance_sheet if period_type == "quarterly" else ticker.balance_sheet
                normalized_type = "balance_sheet"
            elif statement_type in {"cash_flow", "cashflow"}:
                df = ticker.quarterly_cashflow if period_type == "quarterly" else ticker.cashflow
                normalized_type = "cash_flow"
            else:
                raise ValueError(
                    f"Invalid statement type '{statement_type}'. Allowed: income_statement, balance_sheet, cash_flow."
                )
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise RuntimeError(f"Failed to fetch financials for '{clean_symbol}': {e}")

        periods_data: list[dict[str, Any]] = []
        if df is not None and not df.empty:
            for col in df.columns:
                col_date = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
                metrics = {str(k): (float(v) if v is not None and str(v) != "nan" else None) for k, v in df[col].to_dict().items()}
                periods_data.append({"date": col_date, "metrics": metrics})

        source = SourceMetadata(
            provider="yfinance",
            source_url=f"https://finance.yahoo.com/quote/{clean_symbol}/financials",
            retrieved_at=_now_utc_iso(),
            data_type="financials",
            symbol=clean_symbol,
        )

        return FinancialStatement(
            symbol=clean_symbol,
            statement_type=normalized_type,
            period_type=period_type,
            periods=periods_data,
            source=source,
        )

    def get_key_metrics(self, symbol: str) -> KeyMetrics:
        clean_symbol = symbol.strip().upper()
        ticker = self._get_ticker(clean_symbol)
        try:
            info = ticker.info or {}
        except Exception as e:
            raise RuntimeError(f"Failed to fetch metrics for '{clean_symbol}': {e}")

        source = SourceMetadata(
            provider="yfinance",
            source_url=f"https://finance.yahoo.com/quote/{clean_symbol}/key-statistics",
            retrieved_at=_now_utc_iso(),
            data_type="metrics",
            symbol=clean_symbol,
        )

        return KeyMetrics(
            symbol=clean_symbol,
            pe_ratio=info.get("trailingPE"),
            forward_pe=info.get("forwardPE"),
            price_to_book=info.get("priceToBook"),
            profit_margins=info.get("profitMargins"),
            operating_margins=info.get("operatingMargins"),
            return_on_equity=info.get("returnOnEquity"),
            dividend_yield=info.get("dividendYield"),
            beta=info.get("beta"),
            free_cash_flow=info.get("freeCashflow"),
            total_revenue=info.get("totalRevenue"),
            total_debt=info.get("totalDebt"),
            source=source,
        )

    def get_company_news(self, symbol: str, limit: int = 5) -> list[NewsArticle]:
        clean_symbol = symbol.strip().upper()
        ticker = self._get_ticker(clean_symbol)
        try:
            news_items = ticker.news or []
        except Exception as e:
            raise RuntimeError(f"Failed to fetch news for '{clean_symbol}': {e}")

        articles: list[NewsArticle] = []
        for item in news_items[:limit]:
            source = SourceMetadata(
                provider="yfinance",
                source_url=item.get("link"),
                retrieved_at=_now_utc_iso(),
                data_type="news",
                symbol=clean_symbol,
            )
            articles.append(
                NewsArticle(
                    title=item.get("title", ""),
                    publisher=item.get("publisher"),
                    link=item.get("link"),
                    published_at=str(item.get("providerPublishTime")) if item.get("providerPublishTime") else None,
                    summary=item.get("summary") or item.get("description"),
                    source=source,
                )
            )

        return articles

    def resolve_symbol(self, query: str) -> list[dict[str, Any]]:
        clean_query = query.strip()
        if not clean_query:
            return []

        try:
            search = yf.Search(clean_query)
            quotes = search.quotes or []
        except Exception as e:
            raise RuntimeError(f"Symbol search failed for '{clean_query}': {e}")

        results: list[dict[str, Any]] = []
        for q in quotes:
            symbol = q.get("symbol")
            if not symbol:
                continue
            name = q.get("shortname") or q.get("longname") or symbol
            results.append({
                "symbol": symbol,
                "name": name,
                "exchange": q.get("exchDisp") or q.get("exchange"),
                "type": q.get("quoteType") or q.get("typeDisp"),
                "sector": q.get("sector"),
                "industry": q.get("industry"),
            })
        return results
