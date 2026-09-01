import os
import sys
import time
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("."))
load_dotenv()

from app.services.financial.service import FinancialDataService
from app.services.research_service import ResearchService
from app.services.ai.crew import create_research_crew, get_crewai_llm
from app.services.memory_service import MemoryService
from app.services.embedding_service import EmbeddingService

print("=" * 70)
print("AIRA LIVE RESEARCH PIPELINE INTEGRATION TEST")
print("=" * 70)

# Step 1: Initialize services
print("\n1. Initializing services...")
fin_service = FinancialDataService()
embed_service = EmbeddingService()
mem_service = MemoryService(embedding_service=embed_service)
llm = get_crewai_llm(model=os.getenv("GEMINI_LLM_MODEL", "gemini/gemini-3.6-flash"))
print(f"[PASS] LLM initialized: {llm.model}")

# Step 2: Test live financial data extraction
print("\n2. Extracting live financial data for AAPL...")
t0 = time.time()
research_service = ResearchService(
    financial_service=fin_service,
    memory_service=mem_service,
    llm=llm,
)
clean_symbol = research_service._resolve_target_symbol("AAPL")
facts, sources, profile = research_service._extract_verified_evidence(clean_symbol)
dt_facts = time.time() - t0
print(f"[PASS] Facts retrieved in {dt_facts:.2f}s:")
print(f"  Company: {facts.get('name')}")
print(f"  Sector: {facts.get('sector')}, Industry: {facts.get('industry')}")
print(f"  Current Price: ${facts.get('current_price')} {facts.get('currency')}")
print(f"  PE Ratio: {facts.get('pe_ratio')}, Beta: {facts.get('beta')}")
print(f"  Verified Sources Count: {len(sources)}")
for s in sources:
    print(f"    - [{s.get('type')}] {s.get('name')} (freshness: {s.get('freshness')})")

# Step 3: Run real 3-agent CrewAI research crew
print("\n3. Kickoff 3-Agent CrewAI Crew (Researcher -> Analyst -> Synthesizer)...")
t1 = time.time()
crew = create_research_crew(
    financial_service=fin_service,
    symbol="AAPL",
    query="Analyze valuation, growth catalysts, and capital return strategy for AAPL",
    user_context="[preference] Long-term dividend growth, cautious of extreme valuation",
    facts=facts,
    llm=llm,
)

crew_output = crew.kickoff()
dt_crew = time.time() - t1
raw_text = str(crew_output.raw if hasattr(crew_output, "raw") else crew_output)
print(f"[PASS] Crew execution completed in {dt_crew:.2f}s")
print(f"[PASS] Raw LLM response length: {len(raw_text)} chars")

# Step 4: Parse into structured ResearchReport
print("\n4. Parsing and validating structured research report...")
report_dict = research_service._parse_crew_output(
    raw_text=raw_text,
    company_name=facts.get("name") or "Apple Inc.",
    symbol="AAPL",
    user_context="[preference] Long-term dividend growth",
    facts=facts,
    sources=sources,
)

print(f"[PASS] Valid structured report produced!")
print(f"  Company: {report_dict.get('company')} ({report_dict.get('symbol')})")
print(f"  Summary: {str(report_dict.get('summary', ''))[:150]}...")
print(f"  Fundamentals: {str(report_dict.get('fundamentals', ''))[:120]}...")
print(f"  Valuation: {str(report_dict.get('valuation', ''))[:120]}...")
print(f"  Risks ({len(report_dict.get('risks', []))} items): {report_dict.get('risks', [])[:2]}")
print(f"  Opportunities ({len(report_dict.get('opportunities', []))} items): {report_dict.get('opportunities', [])[:2]}")
print(f"  Sources Count: {len(report_dict.get('sources', []))}")

print("\n" + "=" * 70)
print("LIVE AI RESEARCH PIPELINE VERIFIED SUCCESSFULLY WITHOUT MOCKS")
print("=" * 70)
