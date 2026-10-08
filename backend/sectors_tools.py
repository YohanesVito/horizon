"""Bounded, read-only gateway to the IDX subset of Sectors MCP tools.

The model may select only tools in the bundled catalog. Arguments are checked
against the observed MCP schemas and then constrained to the simulation's
symbols and historical window before any provider call is made.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from importlib.resources import files
import json
import re
from urllib.parse import urlencode, urlparse

from jsonschema import Draft202012Validator


_DATA = json.loads(files("backend").joinpath("data/sectors_idx_tools.json").read_text())
_TOOL_SPECS = _DATA["tools"]
_TICKER = re.compile(r"^[A-Z0-9]{4}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DAILY = {"fetch-daily-price", "fetch-index-daily", "fetch-foreign-flow", "fetch-news", "fetch-filings", "fetch-suspensions"}
_BROKER = {"fetch-broker-summary", "fetch-broker-activity", "fetch-broker-summary-top", "fetch-broker-activity-top"}
_KNOWN_INDEXES = {"ihsg", "lq45", "idx30", "idx80", "idxesgl", "idxhidiv20", "idxq30", "idxv30", "idxgrowth30", "idxvalue30", "idxcyclic30", "idxnoncyclic30", "idxquality30", "idxhighdividend20", "idxsector"}
_COMPANY_SECTIONS = {"dividend", "financials", "management", "overview", "ownership", "peers", "valuation"}
_SUBSECTOR_SECTIONS = {"companies", "growth", "market_cap", "stability", "statistics", "valuation"}
_COST = {
    "fetch-broker-activity": 1, "fetch-broker-summary": 1,
    "fetch-companies": 1, "fetch-companies-top-changes": 1,
    "fetch-company-report": 1, "fetch-company-segments": 1,
    "fetch-corporate-actions": 1, "fetch-daily-price": 1,
    "fetch-filings": 1, "fetch-foreign-flow": 1, "fetch-index-daily": 1,
    "fetch-listing-performance": 1, "fetch-news": 1,
    "fetch-quarterly-financial-dates": 1, "fetch-quarterly-financials": 1,
    "fetch-shareholders-composition": 1, "fetch-subsector-report": 1,
    "fetch-suspensions": 1, "fetch-subsectors": 1, "fetch-tags": 1,
    "fetch-broker-activity-top": 2, "fetch-broker-summary-top": 2,
    "fetch-brokers": 1, "fetch-companies-quarterly-financial-dates": 1,
    "fetch-companies-with-segments": 1, "fetch-daily-close": 1,
    "fetch-free-float": 1, "fetch-idx-market-cap": 1,
    "fetch-industries": 1, "fetch-most-traded-stocks": 2,
    "fetch-subindustries": 1, "fetch-top-brokers": 2,
}
_MAX_ROWS = {"fetch-news": 10, "fetch-filings": 10, "fetch-suspensions": 10}
_TOOL_URLS = {
    "fetch-corporate-actions": "https://api.sectors.app/v2/company/corporate-actions/{symbol}/",
    "fetch-news": "https://docs.sectors.app/api-references/v2/indonesia/news/news",
    "fetch-filings": "https://docs.sectors.app/api-references/v2/indonesia/filings/filings",
    "fetch-daily-price": "https://api.sectors.app/v2/daily/{symbol}/",
}


class ToolRejected(ValueError):
    """A planner tool call was outside the bounded research contract."""


class SectorsResearchGateway:
    def __init__(self, mcp, *, allowed_symbols, window_start, window_end,
                 credit_budget=8, max_calls=6, excerpt_chars=3500):
        self.mcp = mcp
        symbols = {str(s).strip().upper().removesuffix(".JK") for s in allowed_symbols}
        if not symbols or any(not _TICKER.fullmatch(s) for s in symbols):
            raise ValueError("At least one valid IDX ticker is required.")
        self.allowed_symbols = symbols
        self.window_start = self._date(window_start, "window_start")
        self.window_end = self._date(window_end, "window_end")
        if self.window_start > self.window_end or self.window_end > date.today():
            raise ValueError("Invalid historical research window.")
        self.credit_budget = max(0, int(credit_budget))
        self.max_calls = max(0, min(8, int(max_calls)))
        self.excerpt_chars = max(500, min(5000, int(excerpt_chars)))
        self.calls = 0
        self.credits = 0
        self._sources = 0
        self.gaps = []

    @staticmethod
    def _date(value, label):
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, date):
            return value
        if not isinstance(value, str) or not _DATE.fullmatch(value):
            raise ValueError(f"{label} must be YYYY-MM-DD.")
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{label} must be YYYY-MM-DD.") from exc

    def catalog(self):
        """Return plain, exact provider schemas for only permitted IDX tools."""
        return [{"name": s["name"], "description": s["description"],
                 "inputSchema": s["inputSchema"]} for s in _TOOL_SPECS.values()]

    def _validate_args(self, name, arguments):
        if name not in _TOOL_SPECS:
            raise ToolRejected("Tool is not in the IDX research allowlist.")
        if not isinstance(arguments, dict):
            raise ToolRejected("Tool arguments must be an object.")
        schema = _TOOL_SPECS[name]["inputSchema"]
        if set(arguments) - set(schema.get("properties", {})):
            raise ToolRejected("Unknown tool argument.")
        errors = list(Draft202012Validator(schema).iter_errors(arguments))
        if errors:
            raise ToolRejected("Arguments do not match the provider schema.")
        args = dict(arguments)
        if "symbol" in args:
            symbol = str(args["symbol"]).strip().upper().removesuffix(".JK")
            if not _TICKER.fullmatch(symbol) or symbol not in self.allowed_symbols:
                raise ToolRejected("Ticker is outside this simulation's traded symbols.")
            args["symbol"] = symbol
        if name == "fetch-news":
            if args.get("extension", "idx") != "idx":
                raise ToolRejected("Only IDX news is permitted.")
            symbols = args.get("symbols", "")
            requested = [s.strip().upper().removesuffix(".JK") for s in symbols.split(",") if s.strip()]
            if len(requested) != 1 or requested[0] not in self.allowed_symbols:
                raise ToolRejected("News lookup must target one traded ticker.")
            args["symbols"] = requested[0]
            args["extension"] = "idx"
        if name == "fetch-index-daily":
            index_code = args.get("index_code", "").lower()
            if index_code not in _KNOWN_INDEXES:
                raise ToolRejected("Unknown IDX index code.")
            args["index_code"] = index_code
        if name in {"fetch-company-report", "fetch-subsector-report"}:
            sections = args.get("sections")
            allowed = _COMPANY_SECTIONS if name == "fetch-company-report" else _SUBSECTOR_SECTIONS
            if not isinstance(sections, list) or not 1 <= len(sections) <= 2 or any(s not in allowed for s in sections):
                raise ToolRejected("Reports require one or two explicit sections.")
        if name == "fetch-quarterly-financials":
            if "report_date" not in args:
                raise ToolRejected("Quarterly requests require an explicit report date.")
            args["approx"] = False
            quarters = args.get("n_quarters", 1)
            if not isinstance(quarters, (int, float)) or quarters not in (1, 2):
                raise ToolRejected("At most two quarters may be requested.")
            args["n_quarters"] = int(quarters)
            report_date = self._date(args["report_date"], "report_date")
            if report_date > self.window_end or report_date < self.window_start - timedelta(days=370):
                raise ToolRejected("Report date is outside the event-aligned historical window.")
            args["report_date"] = report_date.isoformat()
        if name == "fetch-shareholders-composition":
            yr = args.get("year")
            if not isinstance(yr, int) or yr < self.window_start.year - 1 or yr >= self.window_end.year:
                raise ToolRejected("Shareholder data is annual; select a complete year before the replay window.")
        if name == "fetch-broker-summary-top":
            args["n_brokers"] = min(5, max(1, int(args.get("n_brokers", 5))))
            if "start" not in args or "end" not in args:
                raise ToolRejected("Broker summary requires explicit historical dates.")
        if name == "fetch-broker-activity-top":
            args["n_brokers"] = min(5, max(1, int(args.get("n_brokers", 5))))
            if "start" not in args or "end" not in args:
                raise ToolRejected("Broker activity ranking requires explicit historical dates.")
        if name == "fetch-top-brokers":
            if "date" not in args:
                raise ToolRejected("Broker ranking requires an explicit historical date.")
            args["n_brokers"] = min(5, max(1, int(args.get("n_brokers", 5))))
            broker_date = self._date(args["date"], "date")
            if not self.window_start <= broker_date <= self.window_end:
                raise ToolRejected("Broker ranking date is outside the simulation window.")
            args["date"] = broker_date.isoformat()
        if name == "fetch-daily-close":
            if "date" not in args:
                raise ToolRejected("Daily close requires an explicit historical date.")
            requested_date = self._date(args["date"], "date")
            if not self.window_start <= requested_date <= self.window_end:
                raise ToolRejected("Daily close date is outside the simulation window.")
            args["date"] = requested_date.isoformat()
            args["limit"] = min(30, max(1, int(args.get("limit", 30))))
            args["offset"] = min(0, max(0, int(args.get("offset", 0))))
        if name == "fetch-companies-quarterly-financial-dates":
            if args.get("year") != self.window_end.year:
                raise ToolRejected("Quarterly company feed requires the replay end year.")
            args["limit"] = min(10, max(1, int(args.get("limit", 10))))
            args["offset"] = 0
            if "since" in args:
                since = self._date(args["since"], "since")
                if not self.window_start <= since <= self.window_end:
                    raise ToolRejected("Quarterly feed date is outside the simulation window.")
                args["since"] = since.isoformat()
        if name == "fetch-free-float":
            taxonomy_filters = [k for k in ("sector", "sub_sector", "industry", "sub_industry") if args.get(k)]
            if len(taxonomy_filters) != 1:
                raise ToolRejected("Free-float scans require exactly one taxonomy filter.")
            self._require_recent_snapshot(name)
        if name == "fetch-most-traded-stocks":
            if not args.get("sub_sector") or not args.get("start") or not args.get("end"):
                raise ToolRejected("Most-traded lookup requires a subsector and explicit dates.")
            args["n_stock"] = min(5, max(1, int(args.get("n_stock", 5))))
        if name == "fetch-companies-with-segments":
            self._require_recent_snapshot(name)
        if name in {"fetch-brokers", "fetch-industries", "fetch-subindustries", "fetch-subsectors", "fetch-tags"}:
            pass
        if name == "fetch-company-segments":
            yr = args.get("financial_year")
            if yr is None or not isinstance(yr, int) or yr >= self.window_end.year or yr < self.window_start.year - 1:
                raise ToolRejected("Segments require a complete financial year before the replay window.")
        if name == "fetch-companies":
            # Avoid natural-language query mode and broad-universe scans. Permit
            # only a ticker equality lookup, a bounded one-row response.
            where = args.get("where", "")
            match = re.fullmatch(r"\s*(?:symbol|ticker)\s*=\s*['\"]([A-Za-z0-9]{4})['\"]\s*", where, re.I)
            if "q" in args or not match or match.group(1).upper() not in self.allowed_symbols:
                raise ToolRejected("Company lookup must be an exact traded-ticker match.")
            args["where"] = f"symbol = '{match.group(1).upper()}'"
            args["limit"] = 1
            args.pop("offset", None)
            self._require_recent_snapshot(name)
        if name == "fetch-companies-top-changes":
            if not args.get("sub_sector") or len(args.get("classifications", [])) != 1 or len(args.get("periods", [])) != 1:
                raise ToolRejected("Market movers require one subsector, classification, and period.")
            if args.get("periods", [])[0] == "365d":
                raise ToolRejected("One-year market mover scans are outside the bounded context.")
            args["n_stock"] = min(5, max(1, int(args.get("n_stock", 5))))
            self._require_recent_snapshot(name)
        if name in {"fetch-company-report", "fetch-subsector-report"}:
            self._require_recent_snapshot(name)
        if name in {"fetch-subsectors", "fetch-tags"}:
            # Reference lists are small and do not expose ticker universes.
            pass
        elif name == "fetch-corporate-actions":
            pass
        elif name == "fetch-quarterly-financial-dates":
            pass
        elif name == "fetch-listing-performance":
            # This tool returns current rolling windows; it is not historical evidence.
            raise ToolRejected("Current listing performance is not historical evidence.")
        elif name in _MAX_ROWS:
            args["limit"] = min(_MAX_ROWS[name], max(1, int(args.get("limit", 5))))
            args["offset"] = min(30, max(0, int(args.get("offset", 0))))
        if "start" in schema.get("properties", {}) or "end" in schema.get("properties", {}):
            self._validate_dates(name, args)
        if name == "fetch-broker-activity" and "symbol" not in args:
            raise ToolRejected("Broker activity must be filtered to a traded ticker.")
        if name == "fetch-broker-summary" and "symbol" not in args:
            raise ToolRejected("Broker summary must be filtered to a traded ticker.")
        if name == "fetch-idx-market-cap":
            if "start" not in args or "end" not in args:
                raise ToolRejected("Market-cap context requires explicit historical dates.")
        if name == "fetch-daily-close" and args.get("offset", 0) != 0:
            raise ToolRejected("Daily-close universe pagination is disabled.")
        return args

    def _validate_dates(self, name, args):
        if "start" not in args or "end" not in args:
            raise ToolRejected("Historical tool calls require explicit start and end dates.")
        start, end = self._date(args["start"], "start"), self._date(args["end"], "end")
        if start > end or start < self.window_start or end > self.window_end or end > date.today():
            raise ToolRejected("Requested dates are outside the simulation's historical window.")
        max_days = 14 if name in _BROKER else 90
        if (end - start).days + 1 > max_days:
            raise ToolRejected(f"Date range exceeds the {max_days}-day limit.")
        args["start"], args["end"] = start.isoformat(), end.isoformat()

    def _require_recent_snapshot(self, name):
        # These reports/screens are current snapshots with no historical as-of
        # parameter. They cannot explain old events without temporal leakage.
        if self.window_end < date.today():
            raise ToolRejected(f"{name} has no historical as-of version for this simulation.")

    def _cost_for(self, name, args):
        if name == "fetch-company-report":
            return len(args["sections"])
        if name == "fetch-subsector-report":
            return len(args["sections"])
        if name == "fetch-quarterly-financials":
            return args["n_quarters"]
        if name == "fetch-companies-top-changes":
            return len(args["classifications"]) * len(args["periods"])
        if name == "fetch-free-float":
            # Cost is per 100 returned companies; no server-side limit exists.
            return 10
        return _COST[name]

    async def execute(self, name, arguments):
        args = self._validate_args(name, arguments)
        if self.calls >= self.max_calls:
            raise ToolRejected("Research tool-call budget is exhausted.")
        cost = self._cost_for(name, args)
        if self.credits + cost > self.credit_budget:
            raise ToolRejected("Sectors API credit budget is exhausted.")
        # Count before the remote call so retries cannot evade the bounded budget.
        self.calls += 1
        self.credits += cost
        try:
            result = await self.mcp.request("tools/call", {"name": name, "arguments": args})
            if not isinstance(result, dict) or result.get("isError"):
                raise ValueError("Provider reported an unavailable tool result.")
            payload = self._payload(result)
            payload = self._historical_payload(name, payload)
            payload = self._verify_and_filter_symbols(name, args, payload)
        except Exception as exc:
            self.gaps.append({"tool": name, "reason": "Sectors lookup failed or returned an invalid response."})
            return {"status": "unavailable", "error": "Sectors lookup failed.", "tool": name, "credits_used": cost}
        if self._empty_result(payload):
            self.gaps.append({"tool": name, "reason": "Sectors returned no matching historical records."})
            return {"status": "unavailable", "error": "No matching Sectors records.", "tool": name, "credits_used": cost}
        self._sources += 1
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
        excerpt = raw[:self.excerpt_chars]
        source_url = self._source_url(name, args, payload)
        source = {
            "id": f"sectors-{self._sources:02d}", "provider": "Sectors",
            "source_kind": "provider_record", "tool": name,
            "title": f"Sectors {name.removeprefix('fetch-').replace('-', ' ')}" + (f" · {args.get('symbol', args.get('symbols'))}" if args.get("symbol", args.get("symbols")) else ""),
            "query": args, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "url": source_url, "excerpt": excerpt,
            "temporal_scope": "historical provider record; report-period data may be retrospective, not publication-time evidence"
            if name == "fetch-quarterly-financials" else (
                "current snapshot as of retrieval; not event-time evidence" if name in {
                    "fetch-companies", "fetch-companies-top-changes", "fetch-company-report",
                    "fetch-subsector-report", "fetch-free-float", "fetch-companies-with-segments", "fetch-brokers"
                } else "provider record for requested historical dates"),
            "published_at": None,
            "truncated": len(raw) > len(excerpt),
            "untrusted_data": True,
        }
        return {"status": "completed", "ok": True, "tool": name, "credits_used": cost,
                "source": source}

    @staticmethod
    def _payload(result):
        structured = result.get("structuredContent")
        if structured is not None:
            return structured
        texts = [item.get("text", "") for item in result.get("content", [])
                 if item.get("type") == "text"]
        if not texts:
            raise ValueError("Empty MCP result.")
        joined = "\n".join(texts)
        try:
            return json.loads(joined)
        except json.JSONDecodeError:
            return {"text": joined[:3500], "text_truncated": len(joined) > 3500}

    def _historical_payload(self, name, payload):
        """Drop provider rows dated after the replay window from unbounded tools."""
        cutoff = self.window_end
        changed = False

        lower_bound = self.window_start
        def clean(value):
            nonlocal changed
            if isinstance(value, dict):
                # Corporate actions are arrays grouped by action type. Keep only
                # dated records in the permitted replay window; omit undated
                # records because their timing cannot be established.
                result = {}
                for key, item in value.items():
                    if isinstance(item, list):
                        result[key] = clean(item)
                    elif isinstance(item, str) and _DATE.fullmatch(item):
                        try:
                            parsed = date.fromisoformat(item)
                        except ValueError:
                            result[key] = item
                            continue
                        if parsed > cutoff or parsed < lower_bound - timedelta(days=370):
                            changed = True
                        else:
                            result[key] = item
                    else:
                        result[key] = clean(item) if isinstance(item, (dict, list)) else item
                return result
            if isinstance(value, list):
                kept = []
                for item in value:
                    if isinstance(item, str) and _DATE.fullmatch(item):
                        parsed = date.fromisoformat(item)
                        if not lower_bound - timedelta(days=370) <= parsed <= cutoff:
                            changed = True
                            continue
                    if isinstance(item, dict) and any(k.endswith("date") or k == "date" for k in item):
                        raw_date = next((item[k] for k in item if (k.endswith("date") or k == "date") and isinstance(item[k], str) and _DATE.fullmatch(item[k])), None)
                        if not raw_date or not lower_bound <= date.fromisoformat(raw_date) <= cutoff:
                            changed = True
                            continue
                    kept.append(clean(item))
                return kept
            return value

        filtered = clean(payload) if name in {"fetch-corporate-actions", "fetch-quarterly-financial-dates"} else payload
        if changed and isinstance(filtered, dict):
            filtered = dict(filtered)
            filtered["historical_filter_applied"] = f"Future/unanchored dates after {cutoff.isoformat()} were omitted."
        return filtered

    def _verify_and_filter_symbols(self, name, args, payload):
        if isinstance(payload, dict) and payload.get("symbol"):
            response_symbol = str(payload["symbol"]).upper().removesuffix(".JK")
            if response_symbol not in self.allowed_symbols:
                raise ValueError("Provider returned a record outside the traded-symbol set.")
        filtered = False
        def scrub(value):
            nonlocal filtered
            if isinstance(value, dict):
                ticker = value.get("symbol", value.get("ticker"))
                if isinstance(ticker, str) and ticker.upper().removesuffix(".JK") not in self.allowed_symbols:
                    filtered = True
                    return None
                output = {}
                for key, item in value.items():
                    cleaned = scrub(item) if isinstance(item, (dict, list)) else item
                    if cleaned is None and isinstance(item, (dict, list)):
                        filtered = True
                    else:
                        output[key] = cleaned
                return output
            if isinstance(value, list):
                result = []
                for item in value:
                    cleaned = scrub(item)
                    if cleaned is None:
                        filtered = True
                    else:
                        result.append(cleaned)
                return result
            return value
        if name in {"fetch-daily-close", "fetch-free-float", "fetch-most-traded-stocks", "fetch-companies-quarterly-financial-dates", "fetch-companies-with-segments"}:
            clean_value = scrub(payload)
            if filtered and isinstance(clean_value, dict):
                clean_value["ticker_filter_applied"] = sorted(self.allowed_symbols)
            return clean_value
        return payload

    @staticmethod
    def _empty_result(payload):
        if payload is None or payload == [] or payload == {}:
            return True
        if isinstance(payload, dict):
            for key in ("results", "articles", "items", "data", "corporate_actions", "reports"):
                if key in payload:
                    value = payload[key]
                    if value is None or value == [] or value == {}:
                        return True
                    if isinstance(value, dict) and not any(v not in (None, [], {}) for v in value.values()):
                        return True
        return False

    @staticmethod
    def _source_url(name, args, payload):
        # Use provider-record links from the Sectors response when valid HTTPS;
        # never accept a URL supplied by the planner.
        if name == "fetch-news":
            query = urlencode({k: v for k, v in args.items() if k in {"symbols", "extension", "start", "end", "limit", "offset"}})
            return f"https://api.sectors.app/v2/news/?{query}"
        if name == "fetch-daily-price":
            query = urlencode({k: v for k, v in args.items() if k in {"start", "end"}})
            return f"https://api.sectors.app/v2/daily/{args['symbol']}/?{query}"
        if name == "fetch-index-daily":
            query = urlencode({k: v for k, v in args.items() if k in {"start", "end"}})
            return f"https://api.sectors.app/v2/index-daily/{args['index_code']}/?{query}"
        candidates = []
        if isinstance(payload, dict) and not any(isinstance(v, list) and len(v) > 1 for v in payload.values()):
            candidates = [payload[k] for k in ("url", "link", "source_url", "article_url")
                          if isinstance(payload.get(k), str)]
        for candidate in candidates:
            parsed = urlparse(candidate)
            if parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password:
                return candidate
        template = _TOOL_URLS.get(name)
        if template:
            return template.format(**args) if "{symbol}" in template and "symbol" in args else template
        return "https://api.sectors.app/"
