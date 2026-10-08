import asyncio
from datetime import date
from datetime import timedelta

import pytest

from backend.sectors_tools import SectorsResearchGateway, ToolRejected


class FakeMCP:
    def __init__(self, payload=None):
        self.calls = []
        self.payload = payload if payload is not None else {"data": [{"date": "2021-10-20", "value": 12}]}

    async def request(self, method, params):
        self.calls.append((method, params))
        return {"structuredContent": self.payload}


def gateway(mcp=None, **kwargs):
    defaults = dict(allowed_symbols={"BBCA", "TLKM"}, window_start="2021-10-01",
                    window_end="2021-10-31", credit_budget=8, max_calls=6)
    defaults.update(kwargs)
    return SectorsResearchGateway(mcp or FakeMCP(), **defaults)


def test_catalog_is_bundled_idx_only_and_matches_provider_schemas():
    catalog = gateway().catalog()
    names = {tool["name"] for tool in catalog}
    assert "fetch-news" in names and "fetch-quarterly-financials" in names
    assert len(names) == 32
    assert not any(token in name for name in names for token in ("sgx", "klse", "mining"))
    assert all(tool["inputSchema"]["type"] == "object" for tool in catalog)


def test_ticker_binding_and_unknown_tools_reject_before_provider_call():
    mcp = FakeMCP()
    g = gateway(mcp)
    for name, args in [
        ("fetch-sgx-daily-price", {"symbol": "BBCA"}),
        ("made-up-tool", {"symbol": "BBCA"}),
        ("fetch-daily-price", {"symbol": "BBRI", "start": "2021-10-01", "end": "2021-10-02"}),
        ("fetch-news", {"symbols": "BBCA,TLKM", "start": "2021-10-01", "end": "2021-10-02"}),
        ("fetch-news", {"symbols": "BBCA", "extension": "mining", "start": "2021-10-01", "end": "2021-10-02"}),
        ("fetch-news", {"symbols": "BBCA", "extension": "mining", "start": "2021-10-01", "end": "2021-10-02", "url": "https://evil.test"}),
    ]:
        with pytest.raises(ToolRejected):
            asyncio.run(g.execute(name, args))
    assert mcp.calls == []


def test_dates_ranges_pagination_reports_and_quarterly_are_bounded():
    g = gateway()
    with pytest.raises(ToolRejected):
        g._validate_args("fetch-daily-price", {"symbol": "BBCA", "start": "2021-09-30", "end": "2021-10-02"})
    with pytest.raises(ToolRejected):
        g._validate_args("fetch-index-daily", {"index_code": "ihsg", "start": "2021-10-01", "end": "2022-01-01"})
    with pytest.raises(ToolRejected):
        g._validate_args("fetch-broker-summary", {"symbol": "BBCA", "start": "2021-10-01", "end": "2021-10-15"})
    with pytest.raises(ToolRejected):
        g._validate_args("fetch-company-report", {"symbol": "BBCA"})
    with pytest.raises(ToolRejected):
        g._validate_args("fetch-quarterly-financials", {"symbol": "BBCA", "report_date": "2022-03-31", "n_quarters": 4})
    assert g._validate_args("fetch-quarterly-financials", {
        "symbol": "BBCA", "report_date": "2021-09-30", "n_quarters": 2
    })["approx"] is False
    assert g._validate_args("fetch-news", {"symbols": "BBCA", "start": "2021-10-01",
        "end": "2021-10-02", "limit": 30, "offset": 100})["limit"] == 10


def test_recent_only_reports_cannot_leak_current_state_into_old_replay():
    g = gateway(window_end="2021-10-31")
    with pytest.raises(ToolRejected, match="historical as-of"):
        g._validate_args("fetch-company-report", {"symbol": "BBCA", "sections": ["financials"]})
    with pytest.raises(ToolRejected):
        g._validate_args("fetch-companies", {"where": "symbol = 'TLKM'; DROP TABLE companies"})
    with pytest.raises(ToolRejected):
        g._validate_args("fetch-companies", {"where": "symbol = 'BBCA'", "q": "top tech stocks"})


def test_provider_sources_are_bounded_and_url_is_not_planner_controlled():
    mcp = FakeMCP({"articles": [{"title": "Context", "url": "https://news.example/article"}],
                   "noise": "x" * 5000})
    g = gateway(mcp, excerpt_chars=500)
    result = asyncio.run(g.execute("fetch-news", {"symbols": "BBCA", "start": "2021-10-01", "end": "2021-10-02"}))
    assert result["status"] == "completed"
    source = result["source"]
    assert source["url"].startswith("https://api.sectors.app/v2/news/?")
    assert "article" not in source["url"]
    assert source["untrusted_data"] is True and source["truncated"] is True
    assert len(source["excerpt"]) == 500
    assert source["query"]["extension"] == "idx"
    assert source["temporal_scope"] == "provider record for requested historical dates"
    assert source["published_at"] is None


def test_corporate_actions_are_window_filtered_and_wrong_provider_symbol_rejected():
    mcp = FakeMCP({"symbol": "BBCA.JK", "corporate_actions": {"dividend": [
        {"ex_date": "2021-10-12", "dividend_amount": 10},
        {"ex_date": "2022-10-12", "dividend_amount": 20},
    ]}})
    g = gateway(mcp)
    result = asyncio.run(g.execute("fetch-corporate-actions", {"symbol": "BBCA"}))
    assert result["status"] == "completed"
    assert "2022-10-12" not in result["source"]["excerpt"]
    assert "2021-10-12" in result["source"]["excerpt"]

    wrong = gateway(FakeMCP({"symbol": "OTHER", "data": [1]}))
    result = asyncio.run(wrong.execute("fetch-corporate-actions", {"symbol": "BBCA"}))
    assert result["status"] == "unavailable"
    assert not wrong._sources


def test_credit_and_call_budgets_count_provider_attempts():
    mcp = FakeMCP()
    today = date.today()
    g = gateway(mcp, window_start=today - timedelta(days=4), window_end=today,
                credit_budget=1, max_calls=6)
    with pytest.raises(ToolRejected, match="credit budget"):
        asyncio.run(g.execute("fetch-company-report", {"symbol": "BBCA", "sections": ["financials", "dividend"]}))
    result = asyncio.run(g.execute("fetch-index-daily", {"index_code": "ihsg",
        "start": str(today - timedelta(days=2)), "end": str(today)}))
    assert result["status"] == "completed"
    with pytest.raises(ToolRejected, match="credit budget"):
        asyncio.run(g.execute("fetch-news", {"symbols": "BBCA", "start": str(today - timedelta(days=1)), "end": str(today)}))
    assert len(mcp.calls) == 1


def test_provider_failures_are_charged_against_gateway_budget():
    class BrokenMCP:
        async def request(self, *_):
            raise RuntimeError("provider unavailable")
    today = date.today()
    g = gateway(BrokenMCP(), window_start=today - timedelta(days=2), window_end=today,
                credit_budget=1)
    result = asyncio.run(g.execute("fetch-index-daily", {"index_code": "ihsg",
        "start": str(today - timedelta(days=1)), "end": str(today)}))
    assert result["status"] == "unavailable" and result["credits_used"] == 1
    with pytest.raises(ToolRejected, match="credit budget"):
        asyncio.run(g.execute("fetch-index-daily", {"index_code": "ihsg",
            "start": str(today - timedelta(days=1)), "end": str(today)}))


def test_index_source_uses_canonical_query_url_not_provider_embedded_link():
    g = gateway(FakeMCP({"url": "https://wrong.example/ihsg", "data": [
        {"date": "2021-10-20", "close": 6000}
    ]}))
    result = asyncio.run(g.execute("fetch-index-daily", {
        "index_code": "ihsg", "start": "2021-10-19", "end": "2021-10-20"
    }))
    assert result["source"]["url"] == (
        "https://api.sectors.app/v2/index-daily/ihsg/?start=2021-10-19&end=2021-10-20"
    )
