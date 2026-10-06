"""Read-only Sectors MCP probe. Credentials stay in the local environment/file."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
URL = "https://sectors-mcp.supertype.ai/mcp"


def load_key():
    key = os.environ.get("SECTORS_API_KEY", "").strip()
    if not key:
        path = ROOT / ".env.local"
        if path.exists():
            for line in path.read_text().splitlines():
                if line.startswith("SECTORS_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip("\"'")
                    break
    if not key:
        raise RuntimeError("SECTORS_API_KEY is missing")
    return key


class Client:
    def __init__(self):
        self.key = load_key()
        self.session = None
        self.protocol = None
        self.request_id = 0

    def request(self, method, params=None, notification=False):
        body = {"jsonrpc": "2.0", "method": method}
        if not notification:
            self.request_id += 1
            body["id"] = self.request_id
        if params is not None:
            body["params"] = params
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": "Bearer " + self.key,
        }
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        if self.protocol:
            headers["MCP-Protocol-Version"] = self.protocol
        # Use the standard curl client. Keep credentials on stdin, never in argv.
        config = ["url = " + json.dumps(URL), 'request = "POST"']
        config.extend("header = " + json.dumps(k + ": " + v) for k, v in headers.items())
        config.append("data = " + json.dumps(json.dumps(body)))
        with tempfile.NamedTemporaryFile() as header_file:
            response = subprocess.run([
                "curl", "--silent", "--show-error", "--max-time", "45",
                "--config", "-", "--dump-header", header_file.name,
                "--write-out", "\n%{http_code}",
            ], input="\n".join(config) + "\n", text=True, capture_output=True)
            if response.returncode:
                raise RuntimeError(response.stderr.replace(self.key, "[REDACTED]"))
            raw, status = response.stdout.rsplit("\n", 1)
            raw = raw.replace(self.key, "[REDACTED]")
            response_headers = {}
            for line in Path(header_file.name).read_text().splitlines():
                if ":" in line:
                    name, value = line.split(":", 1)
                    response_headers[name.lower()] = value.strip()
            self.session = response_headers.get("mcp-session-id", self.session)
            content_type = response_headers.get("content-type", "")
            if int(status) >= 400:
                raise RuntimeError(f"MCP HTTP {status}: {raw[:1000]}")
        if not raw.strip():
            return None
        if "text/event-stream" in content_type:
            messages = []
            for block in raw.replace("\r\n", "\n").split("\n\n"):
                data = "\n".join(line[5:].lstrip() for line in block.splitlines() if line.startswith("data:"))
                if data:
                    messages.append(json.loads(data))
            result = next((m for m in messages if m.get("id") == body.get("id")), None)
            if result is None:
                raise RuntimeError("No matching MCP response")
        else:
            result = json.loads(raw)
        if "error" in result:
            raise RuntimeError(json.dumps(result["error"], ensure_ascii=False))
        return result.get("result")

    def initialize(self):
        result = self.request("initialize", {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "dividend-research-audit", "version": "0.1"},
        })
        self.protocol = result["protocolVersion"]
        self.request("notifications/initialized", notification=True)
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool")
    parser.add_argument("--arguments", default="{}")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    client = Client()
    initialization = client.initialize()
    if args.tool:
        result = client.request("tools/call", {"name": args.tool, "arguments": json.loads(args.arguments)})
        method = "tools/call"
    else:
        all_tools = []
        params = {}
        while True:
            page = client.request("tools/list", params)
            all_tools.extend(page["tools"])
            if not page.get("nextCursor"):
                break
            params = {"cursor": page["nextCursor"]}
        result = {"tools": all_tools}
        method = "tools/list"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"transport": "MCP Streamable HTTP",
                                  "retrieved_at": datetime.now(ZoneInfo("Asia/Makassar")).isoformat(),
                                  "initialization": initialization,
                                  "method": method, "tool": args.tool, "arguments": json.loads(args.arguments),
                                  "result": result}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(output), "server": initialization.get("serverInfo"),
                      "method": method, "tool": args.tool, "isError": result.get("isError", False),
                      "tool_count": len(result.get("tools", []))}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        message = str(exc)
        try:
            message = message.replace(load_key(), "[REDACTED]")
        except RuntimeError:
            pass
        print(json.dumps({"error": message}, ensure_ascii=False))
        raise SystemExit(1)
