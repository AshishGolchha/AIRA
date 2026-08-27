import json
from app.services.ai.tools import build_financial_tools
from app.services.financial.service import FinancialDataService
from tests.unit.test_financial_service import MockFinancialProvider


def test_build_financial_tools_delegates_to_financial_service():
    """Verify that CrewAI financial tools delegate directly to FinancialDataService."""
    provider = MockFinancialProvider()
    service = FinancialDataService(provider=provider)
    tools = build_financial_tools(service)

    # Tool count check
    assert len(tools) == 7
    tool_map = {t.name: t for t in tools}

    # 1. Test Get Company Profile tool
    profile_tool = tool_map["Get Company Profile"]
    res = json.loads(profile_tool.func("NVDA"))
    assert res["symbol"] == "NVDA"
    assert res["name"] == "NVDA Inc."

    # 2. Test Get Market Quote tool
    quote_tool = tool_map["Get Market Quote"]
    res = json.loads(quote_tool.func("NVDA"))
    assert res["symbol"] == "NVDA"
    assert res["current_price"] == 150.0

    # 3. Test Get Key Metrics tool
    metrics_tool = tool_map["Get Key Metrics"]
    res = json.loads(metrics_tool.func("NVDA"))
    assert res["symbol"] == "NVDA"
    assert res["pe_ratio"] == 25.0

    # 4. Test Search Company Symbol tool
    search_tool = tool_map["Search Company Symbol"]
    res = json.loads(search_tool.func("Nvidia"))
    assert len(res) == 1
    assert res[0]["symbol"] == "NVDA"
