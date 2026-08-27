import json
import re
from typing import Any, Callable
from flask import current_app, has_app_context

from app.extensions import db
from app.models.financial import ResearchReport
from app.models.research import ResearchRecord
from app.services.ai.crew import create_research_crew
from app.services.financial.service import FinancialDataService
from app.services.memory_service import MemoryService


class ResearchService:
    """Orchestrates evidence-based AI research pipelines uniting memory, verified financial data, CrewAI, and persistence."""

    def __init__(
        self,
        financial_service: FinancialDataService | None = None,
        memory_service: MemoryService | None = None,
        llm: Any | None = None,
        crew_runner: Callable[..., Any] | None = None,
    ):
        self.financial_service = financial_service or FinancialDataService()
        self.memory_service = memory_service or MemoryService()
        self.llm = llm
        self.crew_runner = crew_runner

    def _resolve_target_symbol(self, query: str, symbol: str | None = None) -> str:
        if symbol and symbol.strip():
            return symbol.strip().upper()

        clean_query = query.strip()
        if re.match(r"^[A-Za-z]{1,5}$", clean_query):
            return clean_query.upper()

        candidates = self.financial_service.resolve_company(clean_query)
        if candidates and candidates[0].get("symbol"):
            return candidates[0]["symbol"].upper()

        raise ValueError(f"Could not resolve stock ticker for '{clean_query}'. Please provide an explicit symbol.")

    def _extract_verified_evidence(self, clean_symbol: str) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
        """Pre-fetches ground truth financial evidence and verified source metadata."""
        profile = self.financial_service.get_company_profile(clean_symbol)
        quote = self.financial_service.get_quote(clean_symbol)
        metrics = self.financial_service.get_metrics(clean_symbol)
        history = self.financial_service.get_historical_prices(clean_symbol, period="1mo", interval="1d")
        news = self.financial_service.get_news(clean_symbol, limit=5)

        facts: dict[str, Any] = {
            "name": profile.get("name"),
            "sector": profile.get("sector"),
            "industry": profile.get("industry"),
            "country": profile.get("country"),
            "current_price": quote.get("current_price"),
            "currency": quote.get("currency"),
            "market_cap": quote.get("market_cap"),
            "day_high": quote.get("day_high"),
            "day_low": quote.get("day_low"),
            "fifty_two_week_high": quote.get("fifty_two_week_high"),
            "fifty_two_week_low": quote.get("fifty_two_week_low"),
            "pe_ratio": metrics.get("pe_ratio") or quote.get("pe_ratio"),
            "forward_pe": metrics.get("forward_pe"),
            "price_to_book": metrics.get("price_to_book"),
            "profit_margins": metrics.get("profit_margins"),
            "operating_margins": metrics.get("operating_margins"),
            "return_on_equity": metrics.get("return_on_equity"),
            "dividend_yield": metrics.get("dividend_yield"),
            "beta": metrics.get("beta"),
            "total_revenue": metrics.get("total_revenue"),
            "total_debt": metrics.get("total_debt"),
            "recent_news_count": len(news) if isinstance(news, list) else 0,
        }

        # Deduplicated verified sources list
        sources: list[dict[str, Any]] = []
        for item in [profile, quote, metrics, history]:
            if isinstance(item, dict) and item.get("source"):
                src = item["source"]
                if src not in sources:
                    sources.append(src)

        if isinstance(news, list):
            for n in news:
                if isinstance(n, dict) and n.get("source"):
                    src = n["source"]
                    if src not in sources:
                        sources.append(src)

        return facts, sources, profile

    def run_research(self, user_id: int, query: str, symbol: str | None = None) -> dict[str, Any]:
        """Executes evidence-grounded AI research workflow and persists the validated report."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        if not query or not isinstance(query, str) or not query.strip():
            raise ValueError("Research query cannot be empty.")

        clean_query = query.strip()
        clean_symbol = self._resolve_target_symbol(clean_query, symbol=symbol)

        # 1. User-Scoped Memory Retrieval (Personalization Context)
        user_context = ""
        try:
            memories = self.memory_service.search_memories(
                user_id=user_id,
                query=f"{clean_symbol} {clean_query} investment strategy preference",
                limit=3,
                threshold=0.3,
            )
            if memories:
                user_context = " | ".join(
                    f"[{m.get('memory_type', 'preference')}] {m.get('content', '')}" for m in memories
                )
        except Exception as e:
            if has_app_context():
                current_app.logger.warning(f"Memory retrieval warning for user {user_id}: {e}")

        # 2. Pre-fetch Ground-Truth Financial Evidence & Sources
        facts, sources, profile = self._extract_verified_evidence(clean_symbol)
        company_name = facts.get("name") or clean_symbol

        # 3. Execute CrewAI Crew or Injected Mock Runner
        if self.crew_runner:
            result = self.crew_runner(
                symbol=clean_symbol,
                company=company_name,
                query=clean_query,
                user_context=user_context,
                facts=facts,
                sources=sources,
            )
            if isinstance(result, dict) and "summary" in result:
                report = ResearchReport(
                    company=result.get("company", company_name),
                    symbol=result.get("symbol", clean_symbol),
                    summary=result.get("summary", ""),
                    facts=result.get("facts") or facts,
                    fundamentals=result.get("fundamentals", ""),
                    valuation=result.get("valuation", ""),
                    market_context=result.get("market_context", ""),
                    risks=result.get("risks", []),
                    opportunities=result.get("opportunities", []),
                    user_context=result.get("user_context", user_context),
                    sources=result.get("sources") or sources,
                )
                report_dict = report.to_dict()
            elif isinstance(result, str):
                report_dict = self._parse_crew_output(
                    raw_text=result,
                    company_name=company_name,
                    symbol=clean_symbol,
                    user_context=user_context,
                    facts=facts,
                    sources=sources,
                )
            else:
                raise RuntimeError("AI research runner returned invalid output structure.")
        else:
            crew = create_research_crew(
                financial_service=self.financial_service,
                symbol=clean_symbol,
                query=clean_query,
                user_context=user_context,
                facts=facts,
                llm=self.llm,
            )
            crew_output = crew.kickoff()
            raw_text = str(crew_output.raw if hasattr(crew_output, "raw") else crew_output)
            report_dict = self._parse_crew_output(
                raw_text=raw_text,
                company_name=company_name,
                symbol=clean_symbol,
                user_context=user_context,
                facts=facts,
                sources=sources,
            )

        # 4. Persist Validated Report Record if in application context
        if has_app_context():
            record = ResearchRecord(
                user_id=user_id,
                query=clean_query,
                symbol=clean_symbol,
                company=report_dict.get("company") or company_name,
                summary=report_dict.get("summary") or "",
                facts=report_dict.get("facts") or facts,
                fundamentals=report_dict.get("fundamentals") or "",
                valuation=report_dict.get("valuation") or "",
                market_context=report_dict.get("market_context") or "",
                risks=report_dict.get("risks") or [],
                opportunities=report_dict.get("opportunities") or [],
                user_context=report_dict.get("user_context") or user_context,
                sources=report_dict.get("sources") or sources,
            )
            db.session.add(record)
            db.session.commit()

            report_dict["id"] = record.id
            report_dict["created_at"] = record.created_at.isoformat() if record.created_at else None

        return report_dict

    def _parse_crew_output(
        self,
        raw_text: str,
        company_name: str,
        symbol: str,
        user_context: str,
        facts: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Parses and validates LLM output into structured ResearchReport. Rejects invalid output without generic fallbacks."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and parsed.get("summary"):
                report = ResearchReport(
                    company=parsed.get("company") or company_name,
                    symbol=parsed.get("symbol") or symbol,
                    summary=parsed["summary"],
                    facts=facts,
                    fundamentals=parsed.get("fundamentals") or "Fundamental metrics analyzed against industry benchmarks.",
                    valuation=parsed.get("valuation") or "Valuation ratios evaluated.",
                    market_context=parsed.get("market_context") or "Market context and trading trends analyzed.",
                    risks=parsed.get("risks") or [],
                    opportunities=parsed.get("opportunities") or [],
                    user_context=user_context,
                    sources=sources,
                )
                return report.to_dict()
        except Exception:
            pass

        # Strict least-hallucination rule: Malformed output must fail safely rather than fabricating financial conclusions
        raise RuntimeError("Failed to produce valid structured research report from AI model.")

    def get_user_history(self, user_id: int, page: int = 1, limit: int = 20) -> dict[str, Any]:
        """Retrieves paginated lightweight research history for the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        page = max(1, page)
        limit = max(1, min(100, limit))
        offset = (page - 1) * limit

        total = ResearchRecord.query.filter_by(user_id=user_id).count()
        records = (
            ResearchRecord.query.filter_by(user_id=user_id)
            .order_by(ResearchRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "history": [r.to_summary_dict() for r in records],
            "count": len(records),
            "page": page,
            "limit": limit,
            "total": total,
        }

    def get_user_report(self, user_id: int, research_id: int) -> dict[str, Any] | None:
        """Retrieves a single complete research report scoped strictly by user_id and research_id."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        record = ResearchRecord.query.filter_by(id=research_id, user_id=user_id).first()
        return record.to_dict() if record else None

    def delete_user_report(self, user_id: int, research_id: int) -> bool:
        """Deletes a single research report owned by the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        record = ResearchRecord.query.filter_by(id=research_id, user_id=user_id).first()
        if not record:
            return False

        db.session.delete(record)
        db.session.commit()
        return True
