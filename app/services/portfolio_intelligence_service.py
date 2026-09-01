import json
from typing import Any, Callable
from flask import current_app, has_app_context

from app.extensions import db
from app.models.financial import PortfolioIntelligenceReport
from app.models.portfolio_intelligence import PortfolioIntelligenceRecord
from app.models.user import User
from app.services.ai.crew import create_portfolio_intelligence_crew
from app.services.financial.service import FinancialDataService
from app.services.memory_service import MemoryService
from app.services.portfolio_service import PortfolioService
from app.services.research_service import ResearchService
from app.services.watchlist_service import WatchlistService


class PortfolioIntelligenceService:
    """Orchestrates evidence-grounded personalized investment intelligence across portfolio, watchlist, and user context."""

    def __init__(
        self,
        portfolio_service: PortfolioService | None = None,
        watchlist_service: WatchlistService | None = None,
        financial_service: FinancialDataService | None = None,
        memory_service: MemoryService | None = None,
        research_service: ResearchService | None = None,
        llm: Any | None = None,
        crew_runner: Callable[..., Any] | None = None,
    ):
        self.financial_service = financial_service or FinancialDataService()
        self.portfolio_service = portfolio_service or PortfolioService(financial_service=self.financial_service)
        self.watchlist_service = watchlist_service or WatchlistService(financial_service=self.financial_service)
        self.memory_service = memory_service or MemoryService()
        self.research_service = research_service or ResearchService(
            financial_service=self.financial_service,
            memory_service=self.memory_service,
        )
        self.llm = llm
        self.crew_runner = crew_runner

    def run_portfolio_intelligence(self, user_id: int, query: str | None = None) -> dict[str, Any]:
        """Runs personalized portfolio and watchlist intelligence workflow strictly scoped to the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        clean_query = (
            query.strip()
            if (query and isinstance(query, str) and query.strip())
            else "Review my portfolio and watchlist and identify the most important investment risks, opportunities, and areas that deserve further research."
        )

        # 1. Retrieve User Profile & Preferences
        user_context_parts: list[str] = []
        user = None
        if has_app_context():
            user = db.session.get(User, user_id)
            if user and user.profile:
                prof = user.profile
                if prof.display_name:
                    user_context_parts.append(f"[investor] {prof.display_name}")
                if prof.investment_focus:
                    user_context_parts.append(f"[focus] {prof.investment_focus}")
                if prof.risk_preference:
                    user_context_parts.append(f"[risk_preference] {prof.risk_preference}")
                if prof.investment_horizon:
                    user_context_parts.append(f"[horizon] {prof.investment_horizon}")

        # 2. Retrieve Private Semantic User Memories
        try:
            memories = self.memory_service.search_memories(
                user_id=user_id,
                query="portfolio investment risk strategy preference allocation",
                limit=3,
                threshold=0.3,
            )
            for m in memories:
                user_context_parts.append(f"[{m.get('memory_type', 'memory')}] {m.get('content', '')}")
        except Exception as e:
            if has_app_context():
                current_app.logger.warning(f"Memory retrieval warning for user {user_id}: {e}")

        # 3. Retrieve Bounded Recent Research History
        try:
            history_res = self.research_service.get_user_history(user_id=user_id, page=1, limit=3)
            for h in history_res.get("history", []):
                user_context_parts.append(f"[past_research:{h.get('symbol')}] {h.get('summary', '')}")
        except Exception as e:
            if has_app_context():
                current_app.logger.warning(f"Research history retrieval warning for user {user_id}: {e}")

        user_context = " | ".join(user_context_parts)

        # 4. Retrieve Deterministic Portfolio Snapshot & Calculate Concentration Weights
        snapshot = self.portfolio_service.get_portfolio_snapshot(user_id=user_id)
        total_mv = snapshot.get("total_market_value") or 0.0

        for h in snapshot.get("holdings", []):
            mv = h.get("market_value")
            if mv is not None and total_mv > 0:
                h["weight_percent"] = round((mv / total_mv) * 100.0, 2)
            else:
                h["weight_percent"] = None

        # 5. Retrieve User Watchlist & Enriched Verified Financial Data
        watchlist_items = self.watchlist_service.list_items(user_id=user_id)
        enriched_watchlist: list[dict[str, Any]] = []
        sources: list[dict[str, Any]] = []

        facts: dict[str, Any] = {
            "portfolio_totals": {
                "total_market_value": snapshot.get("total_market_value"),
                "total_cost_basis": snapshot.get("total_cost_basis"),
                "total_unrealized_gain_loss": snapshot.get("total_unrealized_gain_loss"),
                "total_unrealized_gain_loss_percent": snapshot.get("total_unrealized_gain_loss_percent"),
                "holdings_count": snapshot.get("holdings_count"),
            },
            "holdings": {},
            "watchlist": {},
        }

        # Collect sources from portfolio holdings
        for h in snapshot.get("holdings", []):
            sym = h["symbol"]
            facts["holdings"][sym] = {
                "quantity": h["quantity"],
                "average_cost": h["average_cost"],
                "current_price": h["current_price"],
                "market_value": h["market_value"],
                "cost_basis": h["cost_basis"],
                "unrealized_gain_loss": h["unrealized_gain_loss"],
                "unrealized_gain_loss_percent": h["unrealized_gain_loss_percent"],
                "weight_percent": h.get("weight_percent"),
            }
            if h.get("source") and h["source"] not in sources:
                sources.append(h["source"])

        # Collect watchlist items and quotes
        for w in watchlist_items:
            sym = w["symbol"]
            quote_data = None
            try:
                quote_data = self.financial_service.get_quote(sym)
            except Exception as e:
                if has_app_context():
                    current_app.logger.warning(f"Quote lookup failed for watchlist {sym}: {e}")

            w_entry = {
                "id": w["id"],
                "symbol": sym,
                "company_name": w.get("company_name"),
                "priority": w.get("priority"),
                "notes": w.get("notes"),
                "current_price": quote_data.get("current_price") if quote_data else None,
                "source": quote_data.get("source") if quote_data else None,
            }
            enriched_watchlist.append(w_entry)
            facts["watchlist"][sym] = {
                "priority": w.get("priority"),
                "notes": w.get("notes"),
                "current_price": w_entry["current_price"],
            }
            if quote_data and quote_data.get("source") and quote_data["source"] not in sources:
                sources.append(quote_data["source"])

        # 6. Execute Generation (Empty state vs AI Research Crew)
        if not snapshot.get("holdings") and not watchlist_items:
            report_dict = PortfolioIntelligenceReport(
                summary="No investment holdings or watchlist items have been added to your account yet.",
                portfolio_overview="Your portfolio is currently empty. Add your security positions via the portfolio API to receive personalized valuation and risk analysis.",
                portfolio_risks=[],
                portfolio_opportunities=[],
                watchlist_priorities=[],
                recommended_research=[
                    "Add securities to your watchlist to begin tracking companies",
                    "Log existing portfolio holdings to enable asset allocation intelligence",
                ],
                portfolio_summary=snapshot,
                user_context=user_context,
                facts=facts,
                sources=[],
            ).to_dict()
        elif self.crew_runner:
            result = self.crew_runner(
                query=clean_query,
                portfolio_context=snapshot.get("holdings", []),
                watchlist_context=enriched_watchlist,
                user_context=user_context,
                facts=facts,
                sources=sources,
            )
            if isinstance(result, dict) and "summary" in result:
                report_dict = PortfolioIntelligenceReport(
                    summary=result.get("summary", ""),
                    portfolio_overview=result.get("portfolio_overview", ""),
                    portfolio_risks=result.get("portfolio_risks", []),
                    portfolio_opportunities=result.get("portfolio_opportunities", []),
                    watchlist_priorities=result.get("watchlist_priorities", []),
                    recommended_research=result.get("recommended_research", []),
                    portfolio_summary=snapshot,
                    user_context=user_context,
                    facts=facts,
                    sources=sources,
                ).to_dict()
            elif isinstance(result, str):
                report_dict = self._parse_crew_output(
                    raw_text=result,
                    snapshot=snapshot,
                    user_context=user_context,
                    facts=facts,
                    sources=sources,
                )
            else:
                raise RuntimeError("Portfolio intelligence runner returned invalid structure.")
        else:
            crew = create_portfolio_intelligence_crew(
                financial_service=self.financial_service,
                query=clean_query,
                portfolio_context=snapshot.get("holdings", []),
                watchlist_context=enriched_watchlist,
                user_context=user_context,
                facts=facts,
                llm=self.llm,
            )
            crew_output = crew.kickoff()
            raw_text = str(crew_output.raw if hasattr(crew_output, "raw") else crew_output)
            report_dict = self._parse_crew_output(
                raw_text=raw_text,
                snapshot=snapshot,
                user_context=user_context,
                facts=facts,
                sources=sources,
            )

        # 7. Persist Successful Intelligence Report into Database
        if has_app_context():
            record = PortfolioIntelligenceRecord(
                user_id=user_id,
                query=clean_query,
                summary=report_dict.get("summary", ""),
                portfolio_overview=report_dict.get("portfolio_overview", ""),
                portfolio_risks=report_dict.get("portfolio_risks") or [],
                portfolio_opportunities=report_dict.get("portfolio_opportunities") or [],
                watchlist_priorities=report_dict.get("watchlist_priorities") or [],
                recommended_research=report_dict.get("recommended_research") or [],
                portfolio_summary=report_dict.get("portfolio_summary") or snapshot,
                user_context=report_dict.get("user_context") or user_context,
                facts=report_dict.get("facts") or facts,
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
        snapshot: dict[str, Any],
        user_context: str,
        facts: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Parses and validates LLM output into structured PortfolioIntelligenceReport. Fails safely upon malformed output."""
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
                def _to_str(val: Any, default: str) -> str:
                    if val is None:
                        return default
                    if isinstance(val, (dict, list)):
                        return json.dumps(val, indent=2)
                    return str(val)

                def _to_list(val: Any) -> list[str]:
                    if val is None:
                        return []
                    if isinstance(val, list):
                        return [str(item) for item in val]
                    return [str(val)]

                report = PortfolioIntelligenceReport(
                    summary=str(parsed["summary"]),
                    portfolio_overview=_to_str(parsed.get("portfolio_overview"), "Portfolio and watchlist reviewed against current market context."),
                    portfolio_risks=_to_list(parsed.get("portfolio_risks")),
                    portfolio_opportunities=_to_list(parsed.get("portfolio_opportunities")),
                    watchlist_priorities=_to_list(parsed.get("watchlist_priorities")),
                    recommended_research=_to_list(parsed.get("recommended_research")),
                    portfolio_summary=snapshot,
                    user_context=user_context,
                    facts=facts,
                    sources=sources,
                )
                return report.to_dict()
        except Exception:
            pass

        raise RuntimeError("Failed to produce valid structured portfolio intelligence report from AI model.")

    def get_user_history(self, user_id: int, page: int = 1, limit: int = 20) -> dict[str, Any]:
        """Retrieves paginated lightweight portfolio intelligence history for the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        page = max(1, page)
        limit = max(1, min(100, limit))
        offset = (page - 1) * limit

        total = PortfolioIntelligenceRecord.query.filter_by(user_id=user_id).count()
        records = (
            PortfolioIntelligenceRecord.query.filter_by(user_id=user_id)
            .order_by(PortfolioIntelligenceRecord.created_at.desc())
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

    def get_user_report(self, user_id: int, intelligence_id: int) -> dict[str, Any] | None:
        """Retrieves a single complete portfolio intelligence report scoped strictly by user_id and intelligence_id."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        record = PortfolioIntelligenceRecord.query.filter_by(id=intelligence_id, user_id=user_id).first()
        return record.to_dict() if record else None

    def delete_user_report(self, user_id: int, intelligence_id: int) -> bool:
        """Deletes a single portfolio intelligence report owned by the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        record = PortfolioIntelligenceRecord.query.filter_by(id=intelligence_id, user_id=user_id).first()
        if not record:
            return False

        db.session.delete(record)
        db.session.commit()
        return True

    def get_latest_report(self, user_id: int) -> dict[str, Any] | None:
        """Retrieves the latest persisted portfolio intelligence report summary for the user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        record = (
            PortfolioIntelligenceRecord.query.filter_by(user_id=user_id)
            .order_by(PortfolioIntelligenceRecord.created_at.desc())
            .first()
        )
        return record.to_dashboard_dict() if record else None
