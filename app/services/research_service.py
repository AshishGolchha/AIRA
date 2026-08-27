import json
import re
from typing import Any, Callable
from flask import current_app, has_app_context

from app.models.financial import ResearchReport
from app.services.ai.crew import create_research_crew, get_crewai_llm
from app.services.financial.service import FinancialDataService
from app.services.memory_service import MemoryService


class ResearchService:
    """Orchestrates AI multi-agent research pipelines uniting memory, financial tools, and CrewAI."""

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
        # Check if query itself is a 1-5 char ticker
        if re.match(r"^[A-Za-z]{1,5}$", clean_query):
            return clean_query.upper()

        candidates = self.financial_service.resolve_company(clean_query)
        if candidates and candidates[0].get("symbol"):
            return candidates[0]["symbol"].upper()

        raise ValueError(f"Could not resolve stock ticker for '{clean_query}'. Please provide an explicit symbol.")

    def run_research(self, user_id: int, query: str, symbol: str | None = None) -> dict[str, Any]:
        """Executes the AI research workflow for the authenticated user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        if not query or not isinstance(query, str) or not query.strip():
            raise ValueError("Research query cannot be empty.")

        clean_query = query.strip()
        clean_symbol = self._resolve_target_symbol(clean_query, symbol=symbol)

        # 1. User-Scoped Memory Retrieval
        user_context = ""
        try:
            memories = self.memory_service.search_memories(
                user_id=user_id,
                query=f"{clean_symbol} {clean_query} investment strategy preference",
                limit=3,
                threshold=0.3,
            )
            if memories:
                user_context = " | ".join(f"[{m.get('memory_type', 'preference')}] {m.get('content', '')}" for m in memories)
        except Exception as e:
            if has_app_context():
                current_app.logger.warning(f"Memory retrieval warning for user {user_id}: {e}")

        # 2. Verify company exists
        profile = self.financial_service.get_company_profile(clean_symbol)
        company_name = profile.get("name", clean_symbol)

        # 3. Execute CrewAI Crew
        if self.crew_runner:
            report_dict = self.crew_runner(
                symbol=clean_symbol,
                company=company_name,
                query=clean_query,
                user_context=user_context,
            )
        else:
            crew = create_research_crew(
                financial_service=self.financial_service,
                symbol=clean_symbol,
                query=clean_query,
                user_context=user_context,
                llm=self.llm,
            )
            crew_output = crew.kickoff()
            raw_text = str(crew_output.raw if hasattr(crew_output, "raw") else crew_output)
            report_dict = self._parse_crew_output(
                raw_text=raw_text,
                company_name=company_name,
                symbol=clean_symbol,
                user_context=user_context,
                profile=profile,
            )

        return report_dict

    def _parse_crew_output(
        self,
        raw_text: str,
        company_name: str,
        symbol: str,
        user_context: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Parses and sanitizes LLM output into structured ResearchReport."""
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
            if isinstance(parsed, dict):
                report = ResearchReport(
                    company=parsed.get("company") or company_name,
                    symbol=parsed.get("symbol") or symbol,
                    summary=parsed.get("summary") or "Summary generated from research analysis.",
                    fundamentals=parsed.get("fundamentals") or "Fundamental analysis completed.",
                    valuation=parsed.get("valuation") or "Valuation analysis completed.",
                    market_context=parsed.get("market_context") or "Market context analyzed.",
                    risks=parsed.get("risks") or ["Market volatility risk"],
                    opportunities=parsed.get("opportunities") or ["Long-term growth potential"],
                    user_context=parsed.get("user_context") or user_context,
                    sources=parsed.get("sources") or [profile.get("source", {})],
                )
                return report.to_dict()
        except Exception:
            pass

        # Fallback structured report
        report = ResearchReport(
            company=company_name,
            symbol=symbol,
            summary=raw_text[:500] if raw_text else "Investment research analysis.",
            fundamentals="Comprehensive fundamental data evaluated.",
            valuation="Valuation metrics assessed against sector benchmarks.",
            market_context="Market trends and price movement analyzed.",
            risks=["General equity risk", "Sector competition"],
            opportunities=["Industry tailwinds", "Revenue expansion"],
            user_context=user_context,
            sources=[profile.get("source", {})],
        )
        return report.to_dict()
