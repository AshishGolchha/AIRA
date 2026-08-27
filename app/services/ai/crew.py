from typing import Any
from crewai import LLM, Agent, Crew, Process, Task
from flask import current_app, has_app_context

from app.services.ai.tools import build_financial_tools
from app.services.financial.service import FinancialDataService


def get_crewai_llm(api_key: str | None = None, model: str | None = None) -> LLM:
    """Instantiates CrewAI LLM configured for Google Gemini."""
    key = api_key
    if not key and has_app_context():
        key = current_app.config.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    model_name = model
    if not model_name and has_app_context():
        model_name = current_app.config.get("GEMINI_LLM_MODEL", "gemini/gemini-2.0-flash")
    model_name = model_name or "gemini/gemini-2.0-flash"

    return LLM(model=model_name, api_key=key)


def create_research_crew(
    financial_service: FinancialDataService,
    symbol: str,
    query: str,
    user_context: str = "",
    llm: LLM | None = None,
) -> Crew:
    """Builds a sequential 3-agent research crew for company investment intelligence."""
    active_llm = llm or get_crewai_llm()
    tools = build_financial_tools(financial_service)

    # 1. Financial Data Researcher Agent
    researcher = Agent(
        role="Senior Financial Researcher",
        goal=f"Gather verified market quotes, company profiles, historical trends, fundamental statements, key metrics, and news for {symbol}.",
        backstory=(
            "You are an expert financial data discovery specialist. You use financial tools to retrieve "
            "factual market data and company metrics without fabricating details."
        ),
        tools=tools,
        llm=active_llm,
        verbose=False,
    )

    # 2. Investment Analyst Agent
    analyst = Agent(
        role="Quantitative & Fundamental Investment Analyst",
        goal=f"Analyze valuation ratios, balance sheet health, operational margins, competitive moat, and risk factors for {symbol}.",
        backstory=(
            "You are a seasoned equity research analyst. You critically evaluate fundamental data, "
            "identify risks and growth catalysts, and objectively assess company valuation."
        ),
        llm=active_llm,
        verbose=False,
    )

    # 3. Research Synthesizer Agent
    synthesizer = Agent(
        role="Principal Investment Intelligence Synthesizer",
        goal=f"Synthesize comprehensive research findings into an executive-ready JSON report tailored to the user context: '{user_context}'.",
        backstory=(
            "You are a lead investment strategist. You synthesize quantitative metrics and fundamental "
            "analysis into clear, structured research reports with verifiable source citations."
        ),
        llm=active_llm,
        verbose=False,
    )

    # Task 1: Data Gathering
    task_gather = Task(
        description=(
            f"Collect all relevant financial and market data for '{symbol}'. "
            f"Retrieve company profile, current quote, key metrics, recent financials, and latest news using your tools."
        ),
        expected_output="Comprehensive raw data collection of company profile, quote, metrics, financials, and news.",
        agent=researcher,
    )

    # Task 2: Fundamental & Valuation Analysis
    task_analyze = Task(
        description=(
            f"Analyze the gathered data for '{symbol}'. Evaluate:\n"
            f"1. Valuation multiples (P/E, P/B, forward P/E) vs historical or sector norms.\n"
            f"2. Profitability, revenue growth, and free cash flow generation.\n"
            f"3. Balance sheet health and debt obligations.\n"
            f"4. Key investment risks and competitive moat opportunities."
        ),
        expected_output="In-depth fundamental, valuation, and risk assessment analysis.",
        agent=analyst,
        context=[task_gather],
    )

    # Task 3: Synthesis & Report Generation
    task_synthesize = Task(
        description=(
            f"Synthesize the research and analysis for user query '{query}' on symbol '{symbol}'.\n"
            f"User Context / Stored Preferences: {user_context or 'None provided.'}\n"
            f"Generate a final JSON object with the exact keys: 'company', 'symbol', 'summary', "
            f"'fundamentals', 'valuation', 'market_context', 'risks', 'opportunities', 'user_context', 'sources'."
        ),
        expected_output="Valid JSON object matching the ResearchReport structure.",
        agent=synthesizer,
        context=[task_gather, task_analyze],
    )

    return Crew(
        agents=[researcher, analyst, synthesizer],
        tasks=[task_gather, task_analyze, task_synthesize],
        process=Process.sequential,
        verbose=False,
    )
